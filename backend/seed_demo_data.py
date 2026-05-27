from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import random


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from backend/.env no matter where this script starts.
load_dotenv(os.path.join(BASE_DIR, ".env"))

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGO_URI"))

db = mongo_client["diabetes_rag_chatbot"]

glucose_collection = db["glucose_logs"]

# Demo meals
meals = [
    "Rice and curry",
    "Roti and dal",
    "Poha",
    "Idli sambar",
    "Dosa",
    "Paneer salad",
    "Vegetable soup",
    "Burger and fries",
    "Pizza",
    "Fruit bowl"
]

# Demo symptoms
symptoms_list = [
    "None",
    "Mild headache",
    "Tiredness",
    "Dizziness",
    "Fatigue"
]

# Generate 30 demo logs
demo_logs = []

base_time = datetime.now() - timedelta(days=7)

for i in range(30):

    meal = random.choice(meals)

    # Simulate glucose based on meal type
    if "Rice" in meal or "Pizza" in meal or "Burger" in meal:
        glucose = random.randint(170, 240)

    elif "Paneer" in meal or "Salad" in meal or "Soup" in meal:
        glucose = random.randint(90, 150)

    else:
        glucose = random.randint(110, 190)

    log = {
        "time": (base_time + timedelta(hours=i * 4)).strftime("%I:%M %p"),
        "glucose": glucose,
        "meal": meal,
        "sleep": random.randint(4, 9),
        "water": random.randint(3, 8),
        "steps": random.randint(1000, 12000),
        "symptoms": random.choice(symptoms_list),
        "created_at": base_time + timedelta(hours=i * 4)
    }

    demo_logs.append(log)

# Insert into MongoDB
glucose_collection.insert_many(demo_logs)

print("30 demo glucose logs inserted successfully.")
