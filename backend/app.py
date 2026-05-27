from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime
from types import SimpleNamespace

import jwt
from jwt import InvalidTokenError
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import os
import re
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai


os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TQDM_DISABLE", "1")

# Build absolute paths so the app works no matter which folder starts Python.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "knowledge_base", "diabetes_rules.txt")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")


# Load secret values such as GEMINI_API_KEY from backend/.env.
load_dotenv(os.path.join(BASE_DIR, ".env"))

mongo_client = None
db = None
in_memory_db = None
next_memory_id = 1


class InMemoryCursor:
    def __init__(self, documents):
        self.documents = documents

    def __iter__(self):
        return iter(self.documents)

    def sort(self, field, direction):
        reverse = direction < 0
        self.documents.sort(key=lambda item: item.get(field) or datetime.min, reverse=reverse)
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self


class InMemoryCollection:
    def __init__(self):
        self.documents = []

    def _matches(self, document, query):
        return all(document.get(key) == value for key, value in query.items())

    def _project(self, document, projection):
        output = dict(document)

        if projection and projection.get("_id") == 0:
            output.pop("_id", None)

        return output

    def find_one(self, query):
        for document in self.documents:
            if self._matches(document, query):
                return dict(document)

        return None

    def insert_one(self, document):
        global next_memory_id

        stored_document = dict(document)
        stored_document.setdefault("_id", str(next_memory_id))
        next_memory_id += 1
        self.documents.append(stored_document)

        return SimpleNamespace(inserted_id=stored_document["_id"])

    def find(self, query, projection=None):
        documents = [
            self._project(document, projection)
            for document in self.documents
            if self._matches(document, query)
        ]

        return InMemoryCursor(documents)


class InMemoryDb:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = InMemoryCollection()

        return self.collections[name]


def get_db():
    """Create the MongoDB connection only when an API route needs it."""
    global mongo_client, db, in_memory_db

    if db is None:
        mongo_uri = os.getenv("MONGO_URI")

        if not mongo_uri:
            raise PyMongoError("MONGO_URI is not configured")

        try:
            mongo_client = MongoClient(
                mongo_uri,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
            )
            mongo_client.admin.command("ping")
            db = mongo_client["diabetes_rag_chatbot"]
        except PyMongoError as error:
            if os.getenv("DISABLE_IN_MEMORY_DB_FALLBACK") == "1":
                raise

            app.logger.warning("MongoDB unavailable; using in-memory development database: %s", error)
            in_memory_db = in_memory_db or InMemoryDb()
            db = in_memory_db

    return db


class LazyMongoCollection:
    def __init__(self, name):
        self.name = name

    def __getattr__(self, attribute):
        return getattr(get_db()[self.name], attribute)


glucose_collection = LazyMongoCollection("glucose_logs")
chat_collection = LazyMongoCollection("chat_history")
users_collection = LazyMongoCollection("users")
# Configure the Gemini model used to generate chatbot answers.
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-2.5-flash")


# Create the Flask app and allow browser requests from the frontend.
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

glucose_logs = []
embedding_model = None

# Create or open the persistent ChromaDB vector database.
client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)

collection = client.get_or_create_collection(
    name="diabetes_knowledge"
)


def api_error(message, status_code=400):
    return jsonify({"error": message}), status_code


def get_embedding_model():
    """Load the local embedding model only when retrieval needs it."""
    global embedding_model

    if embedding_model is None:
        from transformers.utils import logging as transformers_logging
        from sentence_transformers import SentenceTransformer

        transformers_logging.disable_progress_bar()
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

    return embedding_model


def split_text(text, chunk_size=500):
    """Split long knowledge-base text into readable chunks for embedding."""
    chunks = []
    current_chunk = ""

    for paragraph in text.splitlines():
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{paragraph}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def load_knowledge_base():
    """Read diabetes guidance, embed it, and store it in ChromaDB."""
    model = get_embedding_model()

    knowledge_files = [
    os.path.join(BASE_DIR, "knowledge_base", "diabetes_rules.txt"),
    os.path.join(BASE_DIR, "knowledge_base", "food_knowledge.txt")
    ]

    text = ""

    for file_path in knowledge_files:
        with open(file_path, "r", encoding="utf-8") as file:
            text += file.read() + "\n\n"

    chunks = split_text(text)

    for index, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        collection.upsert(
            ids=[f"chunk_{index}"],
            embeddings=[embedding],
            documents=[chunk]
        )

    print(f"{len(chunks)} chunks stored in ChromaDB")


def retrieve_relevant_knowledge(query, top_k=3):
    try:
        if collection.count() == 0:
            load_knowledge_base()

        model = get_embedding_model()
        query_embedding = model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results["documents"][0]
    except Exception as error:
        app.logger.exception("Knowledge retrieval failed: %s", error)
        documents = []

    combined_knowledge = "\n\n".join(documents)

    return combined_knowledge, documents


def generate_gemini_answer(prompt):
    """Generate text with Gemini and convert provider failures into safe responses."""
    try:
        gemini_response = model.generate_content(
            prompt,
            request_options={"timeout": 20}
        )
        return gemini_response.text
    except Exception as error:
        error_text = str(error)
        error_name = error.__class__.__name__
        app.logger.exception("Gemini response generation failed: %s", error)

        if "403" in error_text or "PermissionDenied" in error_name:
            return """
Quick Summary:
The AI provider rejected this Gemini API key or project.

Safe Actions:
- Create or use a Gemini API key from a project that has access enabled.
- Update GEMINI_API_KEY in backend/.env.
- Restart Flask after changing backend/.env.

Safety Note:
The backend is running, but Gemini is refusing the request before an AI answer can be generated.
"""

        if "429" in error_text or "ResourceExhausted" in error_name:
            return """
Quick Summary:
The AI service quota is temporarily exhausted.

Safe Actions:
- Please wait a short time and try again.
- Avoid sending repeated messages quickly.
- For urgent symptoms or very abnormal glucose readings, contact a healthcare professional.

Safety Note:
This is a service limit issue, not a problem with your health data.
"""

        return """
Quick Summary:
I could not complete the AI response right now.

Safe Actions:
- Please try again in a moment.
- Check that your glucose, meal, and symptom details are entered correctly.
- Contact a healthcare professional for urgent or severe symptoms.

Safety Note:
This tool provides general education only.
"""

def check_emergency(glucose, symptoms):
    """Detect urgent symptoms or glucose readings that need medical help."""
    emergency_keywords = [
        "chest pain",
        "breathing difficulty",
        "unconscious",
        "fainting",
        "seizure",
        "confusion",
        "severe dizziness",
        "vomiting",
        "extreme weakness"
    ]

    symptoms_text = (symptoms or "").lower()

    for keyword in emergency_keywords:
        if keyword in symptoms_text:
            return True

    try:
        glucose_value = float(glucose)

        if glucose_value < 54 or glucose_value > 300:
            return True

    except (TypeError, ValueError):
        pass

    return False

def classify_query(user_message):
    message = (user_message or "").lower()
    normalized_message = re.sub(r"\s+", " ", message).strip()

    analytics_keywords = [
        "average", "highest", "trend", "dashboard",
        "logs", "time in range", "risky meal"
    ]

    health_keywords = [
        "glucose", "sugar", "diabetes", "insulin", "meal", "high", "low",
        "rice", "roti", "food", "carbs", "diet", "walking",
        "symptoms", "dizziness", "sleep", "water", "steps"
    ]

    if any(word in message for word in analytics_keywords):
        return "analytics"

    if any(word in message for word in health_keywords):
        return "rag"

    generic_messages = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "how are you",
        "thanks",
        "thank you",
        "who are you",
    }

    if normalized_message in generic_messages:
        return "generic"

    return "rag"

def apply_medical_guardrails(response):
    """Block unsafe medical advice before sending the answer to the user."""
    unsafe_phrases = [
        "take insulin",
        "increase insulin",
        "decrease insulin",
        "stop medication",
        "stop taking medicine",
        "change your dose",
        "double your dose",
        "you have diabetes",
        "you definitely have",
        "ignore symptoms"
    ]

    response_lower = response.lower()

    for phrase in unsafe_phrases:
        if phrase in response_lower:
            return """
Safety Notice:

I cannot provide medication changes, diagnosis, or insulin dosage advice.

Please follow your doctor's prescribed treatment plan and contact a healthcare professional for medical decisions.
"""

    return response


def parse_optional_float(value):
    """Return a float for numeric input, or None when the user left it blank."""
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_optional_int(value):
    if value in (None, ""):
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def build_patient_log(data):
    created_at = datetime.now()

    return {
        "time": data.get("time") or created_at.strftime("%I:%M %p"),
        "glucose": parse_optional_float(data.get("glucose")),
        "meal": data.get("meal") or "",
        "sleep": parse_optional_float(data.get("sleep")),
        "water": parse_optional_float(data.get("water")),
        "steps": parse_optional_int(data.get("steps")),
        "symptoms": data.get("symptoms") or "",
        "created_at": created_at
    }


def serialize_patient_log(log):
    serialized = dict(log)
    serialized.pop("_id", None)

    created_at = serialized.get("created_at")
    if isinstance(created_at, datetime):
        serialized["created_at"] = created_at.isoformat()

    return serialized


@app.route("/")
def home():
    """Serve the chatbot page from the frontend folder."""
    return send_from_directory(FRONTEND_DIR, "chatbot.html")


@app.route("/favicon.ico")
def favicon():
    """Avoid a browser console 404 when no favicon asset is configured."""
    return "", 204


@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_metadata():
    """Avoid noise from Chrome DevTools' local app metadata probe."""
    return "", 204


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return api_error("Name, email, and password are required", 400)

    try:
        if users_collection.find_one({"email": email}):
            return api_error("User already exists", 400)

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now()
        })
    except PyMongoError as error:
        app.logger.exception("Registration database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    return jsonify({"message": "User registered successfully"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return api_error("Email and password are required", 400)

    try:
        user = users_collection.find_one({"email": email})
    except PyMongoError as error:
        app.logger.exception("Login database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    if not user or not check_password_hash(user["password"], password):
        return api_error("Invalid email or password", 401)

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user["email"]
        },
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "name": user["name"]
    })

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            token = auth_header.replace("Bearer ", "")

        if not token:
            return api_error("Token is missing", 401)

        try:
            decoded = jwt.decode(
                token,
                os.getenv("JWT_SECRET"),
                algorithms=["HS256"]
            )

            current_user = users_collection.find_one({
                "email": decoded["email"]
            })

            if not current_user:
                return api_error("User account was not found. Please login again.", 401)

        except InvalidTokenError:
            return api_error("Token is invalid. Please login again.", 401)
        except PyMongoError as error:
            app.logger.exception("Authentication database error: %s", error)
            return api_error("Database is unavailable. Please try again shortly.", 503)

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/api/chat", methods=["POST"])
@token_required
def chat(current_user):
    """Receive user input, retrieve knowledge, ask Gemini, and return an answer."""
    data = request.get_json() or {}

    # Extract patient context sent from frontend/js/script.js.
    user_message = data.get("message")
    glucose = data.get("glucose")
    meal = data.get("meal")
    sleep = data.get("sleep")
    water = data.get("water")
    steps = data.get("steps")
    symptoms = data.get("symptoms")
    glucose_value = parse_optional_float(glucose)

    if not user_message or not user_message.strip():
        return api_error("Message is required", 400)

    # Log the chat message and patient context to MongoDB.
    if glucose and glucose_value is None:
        return api_error("Glucose must be a valid number", 400)

    if glucose_value is not None:
        try:
            glucose_collection.insert_one({
                "user_id": str(current_user["_id"]),
                "time": datetime.now().strftime("%I:%M %p"),
                "glucose": glucose_value,
                "meal": meal,
                "sleep": parse_optional_float(sleep),
                "water": parse_optional_float(water),
                "steps": parse_optional_int(steps),
                "symptoms": symptoms,
                "created_at": datetime.now()
            })
        except PyMongoError as error:
            app.logger.exception("Glucose log write failed: %s", error)

    # # Save each chatbot glucose reading so the dashboard can display it.
    # if glucose:
    #     glucose_logs.append({
    #         "time": datetime.now().strftime("%I:%M %p"),
    #         "glucose": float(glucose),
    #         "meal": meal,
    #         "symptoms": symptoms
    #     })

    # Handle emergency cases before calling the AI model.
    is_emergency = check_emergency(glucose, symptoms)

    if is_emergency:
        return jsonify({
            "answer": """
Emergency Warning:

Your symptoms or glucose reading may need urgent medical attention.

Please contact a doctor, caregiver, or emergency medical service immediately.

This chatbot cannot handle emergency medical situations.
"""
        })
    query_type = classify_query(user_message)

    if query_type == "generic":
        response = "Hi, I'm here. Ask me about glucose, meals, sleep, water, steps, symptoms, or safe lifestyle guidance."

        return jsonify({
            "answer": response,
            "sources": []
        })
     

    # Retrieve knowledge using both the question and patient context so meal-specific
    # answers do not drift toward unrelated generic food examples.
    retrieval_query = f"""
    User question: {user_message}
    Glucose: {glucose}
    Meal: {meal}
    Sleep: {sleep}
    Water: {water}
    Steps: {steps}
    Symptoms: {symptoms}
    """
    retrieved_knowledge, source_chunks = retrieve_relevant_knowledge(retrieval_query)
    # Include recent chat history in the prompt to help Gemini generate more context-aware answers.
    try:
        recent_chats = list(
            chat_collection.find(
                {"user_id": str(current_user["_id"])},
                {"_id": 0}
            ).sort("created_at", -1).limit(6)
        )
    except PyMongoError as error:
        app.logger.exception("Chat history lookup failed: %s", error)
        recent_chats = []

    memory_text = ""

    for chat in reversed(recent_chats):
        memory_text += f"""
    User: {chat.get("user_message")}
    Assistant: {chat.get("bot_response")}
    """

    prompt = f"""
    You are a supportive diabetes wellness assistant.

    Your role is to:
    - provide safe educational guidance
    - help users understand glucose trends
    - support healthy lifestyle habits
    - respond empathetically to emotional concerns
    - encourage professional medical help when needed

    You are supportive, calm, conversational, and human-like.

    PATIENT CONTEXT:
    - Glucose reading: {glucose}
    - Meal: {meal}
    - Sleep: {sleep} hours
    - Water: {water} glasses
    - Steps: {steps}
    - Symptoms: {symptoms}

    RECENT CONVERSATION MEMORY:
    {memory_text}

    RETRIEVED MEDICAL KNOWLEDGE:
    {retrieved_knowledge}

    USER QUESTION:
    {user_message}

    EXPLAINABILITY REQUIREMENT:
    - Briefly explain why the advice was given.
    - Mention which patient context was used.
    - Mention which retrieved knowledge supported the answer.
    - Keep explanation short and simple.

    RESPONSE STYLE:
    - Do not use markdown.
    - Do not use ** bold symbols.
    - Keep answer short.
    - Use simple headings.
    - Use 2 to 3 bullets only.
    - Avoid long paragraphs.
    - Do not repeat the same advice again and again.
    - Do not say the user ate or drank something unless it appears in PATIENT CONTEXT.
    - If retrieved knowledge mentions examples such as juice or sugary drinks, use them only as general examples, not as detected patient intake.
    RESPONSE FORMAT:

    Quick Summary:
    Write 1 short sentence.

    Why This Suggestion:
    - Mention patient context used.
    - Mention retrieved knowledge used.

    Safe Actions:
    - action 1
    - action 2
    - action 3

    When to Contact Doctor:
    Write 1 short sentence.

    Safety Note:
    Write 1 short sentence.
    """

    # Apply a final safety filter to the AI response.
    response = apply_medical_guardrails(generate_gemini_answer(prompt))

    # Log the full chat history with patient context to MongoDB for future analysis.
    try:
        chat_collection.insert_one({
            "user_id": str(current_user["_id"]),
            "user_message": user_message,
            "bot_response": response,
            "glucose": glucose_value,
            "meal": meal,
            "sleep": parse_optional_float(sleep),
            "water": parse_optional_float(water),
            "steps": parse_optional_int(steps),
            "symptoms": symptoms,
            "created_at": datetime.now()
        })
    except PyMongoError as error:
        app.logger.exception("Chat history write failed: %s", error)

    return jsonify({
        "answer": response,
        "sources": source_chunks
    })

@app.route("/api/dashboard", methods=["GET"])
@token_required
def dashboard_data(current_user):
    try:
        logs = list(
            glucose_collection.find(
                {"user_id": str(current_user["_id"])},
                {"_id": 0}
            )
        )
    except PyMongoError as error:
        app.logger.exception("Dashboard database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    if len(logs) == 0:
        logs = [
            {"time": "8 AM", "glucose": 110, "meal": "Oats", "sleep": 7, "water": 2, "steps": 1200, "symptoms": "None"},
            {"time": "10 AM", "glucose": 145, "meal": "Tea", "sleep": 7, "water": 3, "steps": 2600, "symptoms": "None"},
            {"time": "12 PM", "glucose": 185, "meal": "Rice and curry", "sleep": 7, "water": 4, "steps": 3900, "symptoms": "Tired"},
            {"time": "2 PM", "glucose": 170, "meal": "Curd", "sleep": 7, "water": 5, "steps": 4800, "symptoms": "None"},
            {"time": "4 PM", "glucose": 150, "meal": "Fruit", "sleep": 7, "water": 6, "steps": 6200, "symptoms": "None"},
            {"time": "6 PM", "glucose": 135, "meal": "Light snack", "sleep": 7, "water": 7, "steps": 7600, "symptoms": "None"}
        ]

    return jsonify({
        "glucose_logs": [serialize_patient_log(log) for log in logs]
    })

@app.route("/api/log-glucose", methods=["POST"])
def log_glucose():
    data = request.get_json() or {}
    glucose_log = build_patient_log(data)

    if glucose_log["glucose"] is None:
        return api_error("Glucose is required", 400)

    try:
        result = glucose_collection.insert_one(glucose_log)
    except PyMongoError as error:
        app.logger.exception("Glucose log database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    glucose_log["_id"] = result.inserted_id

    return jsonify({
        "message": "Glucose log saved successfully",
        "glucose_log": serialize_patient_log(glucose_log)
    })

@app.route("/api/profile", methods=["GET"])
@token_required
def profile(current_user):
    user_id = str(current_user["_id"])

    try:
        logs = list(glucose_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ))
    except PyMongoError as error:
        app.logger.exception("Profile database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    total_logs = len(logs)

    if total_logs > 0:
        avg_glucose = round(
            sum(log["glucose"] for log in logs) / total_logs,
            2
        )
    else:
        avg_glucose = 0

    return jsonify({
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "total_logs": total_logs,
        "average_glucose": avg_glucose
    })

@app.route("/api/analytics", methods=["GET"])
@token_required
def analytics(current_user):

    user_id = str(current_user["_id"])

    try:
        logs = list(
            glucose_collection.find(
                {"user_id": user_id},
                {"_id": 0}
            )
        )
    except PyMongoError as error:
        app.logger.exception("Analytics database error: %s", error)
        return api_error("Database is unavailable. Please try again shortly.", 503)

    if len(logs) == 0:
        return jsonify({
            "average_glucose": 0,
            "highest_glucose": 0,
            "time_in_range": 0,
            "risky_meal": "No data",
            "low_sleep_high_glucose": 0
        })

    glucose_values = [log["glucose"] for log in logs]

    average_glucose = round(
        sum(glucose_values) / len(glucose_values),
        2
    )

    highest_glucose = max(glucose_values)

    # Time in range (70-180)
    in_range = [
        g for g in glucose_values
        if 70 <= g <= 180
    ]

    time_in_range = round(
        (len(in_range) / len(glucose_values)) * 100,
        2
    )

    # Risky meal detection
    meal_glucose = {}

    for log in logs:
        meal = log.get("meal", "Unknown")
        glucose = log.get("glucose", 0)

        if meal not in meal_glucose:
            meal_glucose[meal] = []

        meal_glucose[meal].append(glucose)

    risky_meal = "No data"
    highest_avg = 0

    for meal, values in meal_glucose.items():
        avg = sum(values) / len(values)

        if avg > highest_avg:
            highest_avg = avg
            risky_meal = meal

    # Low sleep correlation
    low_sleep_logs = [
        log for log in logs
        if log.get("sleep") and int(log["sleep"]) < 6
    ]

    if len(low_sleep_logs) > 0:
        low_sleep_high_glucose = round(
            sum(log["glucose"] for log in low_sleep_logs)
            / len(low_sleep_logs),
            2
        )
    else:
        low_sleep_high_glucose = 0

    return jsonify({
        "average_glucose": average_glucose,
        "highest_glucose": highest_glucose,
        "time_in_range": time_in_range,
        "risky_meal": risky_meal,
        "low_sleep_high_glucose": low_sleep_high_glucose
    })

if __name__ == "__main__":
    # Start the local development server.
    app.run(debug=True,use_reloader=False)
