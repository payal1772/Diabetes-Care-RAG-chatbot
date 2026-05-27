# Features

This document explains the current features implemented in the Diabetes RAG Chatbot.

---

# Core AI Features

## 1. Retrieval-Augmented Generation (RAG)

The chatbot uses Retrieval-Augmented Generation to provide grounded healthcare responses.

Instead of relying only on generic LLM outputs, the system retrieves trusted healthcare knowledge before generating responses.

Current knowledge sources:
- diabetes_rules.txt
- food_knowledge.txt
- USDA food datasets

Benefits:
- reduced hallucinations
- safer healthcare guidance
- explainable responses
- trusted knowledge retrieval

---

# 2. Semantic Search

The system uses embeddings and ChromaDB to perform semantic similarity search.

This allows the chatbot to retrieve relevant information even when wording differs.

Example:

User Query:
```text
Can rice spike my sugar?
```

Retrieved Knowledge:
```text
White rice may increase glucose levels due to high carbohydrate content.
```

---

# 3. Conversational Memory

The chatbot stores recent user conversations in MongoDB.

This allows:
- contextual responses
- continuity in conversations
- better personalization

Example:

```text
User:
My sugar rises after dinner.

Later:
What should I improve first?
```

The chatbot remembers previous context.

---

# 4. Query Routing

Not every query triggers RAG retrieval.

The system classifies queries into:
- Generic conversation
- Healthcare RAG
- Analytics requests
- Emergency detection

Example:

```text
hello
↓
Generic conversational response

Can rice increase glucose?
↓
RAG retrieval

What is my average glucose?
↓
Analytics engine
```

This makes the chatbot feel more natural and intelligent.

---

# 5. Explainable AI

The chatbot explains:
- why suggestions were generated
- what patient context was used
- what retrieved knowledge supported the answer

Example:

```text
Why This Suggestion:
- Your glucose was high after a rice-based meal.
- Retrieved food knowledge indicates rice is high in carbohydrates.
```

---

# Healthcare Features

## 6. Diabetes-Focused Guidance

The chatbot provides educational guidance related to:
- glucose management
- meals and carbohydrates
- lifestyle awareness
- hydration
- sleep
- physical activity

---

# 7. Food Intelligence

The chatbot includes food-aware nutrition understanding using:
- food knowledge base
- USDA food datasets

Current food features:
- carbohydrate awareness
- meal guidance
- risky meal detection
- food-related glucose insights

Example Questions:
- Can I eat rice?
- Is pizza bad for glucose?
- Which is better: rice or roti?

---

# 8. Emergency Detection

The chatbot detects severe symptoms such as:
- chest pain
- severe dizziness
- breathing difficulty
- unconsciousness

Emergency messages bypass normal RAG flow and return urgent healthcare warnings.

---

# 9. Healthcare Guardrails

The system prevents unsafe medical responses.

Blocked unsafe behavior:
- insulin dosage advice
- medication changes
- diagnosis claims
- unsafe treatment suggestions

The chatbot is designed for educational support only.

---

# Dashboard Features

## 10. Glucose Analytics Dashboard

The dashboard visualizes patient health metrics.

Current charts:
- glucose trend chart
- sleep tracking
- water tracking
- activity/steps tracking

---

# 11. Advanced Analytics

The system calculates:
- average glucose
- highest glucose
- time in range
- risky meals
- low sleep glucose correlation

These insights help identify health patterns.

---

# 12. User Profile System

Users can view:
- profile information
- total glucose logs
- average glucose metrics

---

# Authentication Features

## 13. User Registration

Users can create accounts using:
- name
- email
- password

---

# 14. User Login

The system supports JWT-based login authentication.

Features:
- secure login
- token-based authentication
- protected routes

---

# 15. User-Specific Data Isolation

Each user sees only:
- their own dashboard
- their own glucose logs
- their own chat memory
- their own analytics

This is implemented using:
```text
user_id
```

inside MongoDB collections.

---

# Backend Features

## 16. Flask REST APIs

The backend exposes APIs for:
- authentication
- chatbot interaction
- analytics
- dashboard data
- user profiles

Main APIs:
- /api/register
- /api/login
- /api/chat
- /api/dashboard
- /api/analytics
- /api/profile

---

# 17. MongoDB Integration

MongoDB Atlas is used for:
- user accounts
- glucose logs
- chat history
- conversational memory
- analytics data

---

# 18. ChromaDB Vector Database

ChromaDB stores:
- embeddings
- semantic indexes
- healthcare knowledge chunks

This enables fast semantic retrieval.

---

# 19. Embedding-Based Retrieval

The system uses SentenceTransformers to generate embeddings for:
- healthcare knowledge
- food knowledge
- user queries

Model Used:
```text
all-MiniLM-L6-v2
```

---

# Frontend Features

## 20. ChatGPT-Style Interface

The frontend includes:
- conversational chat UI
- smooth interaction flow
- typing-style experience

---

# 21. Dashboard Visualization

Dashboard visualizations are built using:
- Apache ECharts

Features:
- responsive charts
- analytics cards
- glucose visualization
- lifestyle metrics

---

# 22. Responsive User Interface

The frontend is designed to support:
- desktop layouts
- mobile responsiveness
- clean healthcare dashboard design

---

# Security Features

## 23. JWT Authentication

Protected APIs require valid JWT tokens.

Flow:

```text
Login
↓
JWT token generated
↓
Frontend stores token
↓
Protected API access
```

---

# 24. Environment Variable Protection

Sensitive credentials are stored in:
```text
.env
```

Example:

```env
GEMINI_API_KEY=
MONGO_URI=
JWT_SECRET=
```

---

# AI Architecture Features

## 25. Prompt Engineering

The chatbot uses structured prompts containing:
- retrieved knowledge
- explainability instructions
- safety instructions
- formatting rules
- conversational memory

---

# 26. Multi-Layer AI Pipeline

Current AI architecture:

```text
User Query
↓
Emergency Detection
↓
Query Router
↓
RAG Retrieval
↓
Memory Injection
↓
Gemini Generation
↓
Guardrails
↓
Explainable Response
```

---

# Planned Future Features

Future improvements may include:
- CGM integration
- wearable APIs
- food comparison engine
- recommendation engine
- Thompson Sampling
- long-term memory
- agentic RAG
- personalized interventions
- doctor/admin workflows

---

# Current System Summary

The Diabetes RAG Chatbot currently combines:
- RAG
- food intelligence
- healthcare analytics
- conversational memory
- explainable AI
- JWT authentication
- MongoDB persistence
- healthcare guardrails
- dashboard analytics

into a healthcare-aware AI assistant system.