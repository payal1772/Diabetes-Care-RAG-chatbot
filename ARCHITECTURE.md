# System Architecture

This document explains the architecture of the Diabetes RAG Chatbot system.

---

# High-Level Architecture

Frontend
↓
JWT Authentication
↓
Flask Backend APIs
↓
MongoDB + Query Router
↓
RAG Pipeline
↓
ChromaDB Vector Database
↓
Gemini LLM
↓
Guardrails + Explainability
↓
Final Response

---

# Core Components

## 1. Frontend Layer

Technologies:
- HTML
- CSS
- JavaScript
- Apache ECharts

Responsibilities:
- Chat interface
- Dashboard visualization
- Login/Register pages
- User interaction
- API communication

---

# 2. Authentication Layer

Technology:
- JWT Authentication

Responsibilities:
- User registration
- User login
- Token generation
- Protected API access
- User-specific data isolation

Flow:

User Login
↓
JWT Token Generated
↓
Frontend stores token
↓
Token sent with API requests
↓
Backend validates token

---

# 3. Backend API Layer

Technology:
- Flask

Responsibilities:
- Chat APIs
- Analytics APIs
- Dashboard APIs
- Profile APIs
- Authentication APIs
- Query routing
- Memory retrieval

Main APIs:
- /api/register
- /api/login
- /api/chat
- /api/dashboard
- /api/analytics
- /api/profile

---

# 4. MongoDB Layer

Technology:
- MongoDB Atlas

Collections:
- users
- glucose_logs
- chat_history

Responsibilities:
- Store user accounts
- Store patient health metrics
- Store conversational memory
- Store analytics data

---

# 5. Query Routing Layer

Purpose:
Determine how a user query should be processed.

Routes:
- Generic conversation
- RAG retrieval
- Analytics requests
- Emergency escalation

Example:

hello
↓
Generic response

Can rice increase glucose?
↓
RAG retrieval

What is my average glucose?
↓
Analytics engine

---

# 6. RAG Pipeline

Purpose:
Retrieve trusted healthcare knowledge before generation.

Flow:

Knowledge Base
↓
Chunking
↓
Embeddings
↓
ChromaDB Storage
↓
User Query Embedding
↓
Similarity Search
↓
Prompt Augmentation
↓
Gemini Response

Knowledge Sources:
- diabetes_rules.txt
- food_knowledge.txt
- USDA food datasets

---

# 7. Vector Database Layer

Technology:
- ChromaDB

Responsibilities:
- Store embeddings
- Semantic similarity search
- Retrieve relevant healthcare knowledge

Embedding Model:
- all-MiniLM-L6-v2

---

# 8. Gemini LLM Layer

Technology:
- Gemini API

Responsibilities:
- Response generation
- Conversational interaction
- Explainable AI responses
- Context-aware reasoning

Inputs:
- User query
- Retrieved knowledge
- Patient metrics
- Memory context

---

# 9. Memory Layer

Technology:
- MongoDB

Responsibilities:
- Store recent conversations
- Retrieve contextual memory
- Improve conversational continuity

Current Memory Type:
- Short-term conversational memory

---

# 10. Guardrail Layer

Purpose:
Improve healthcare AI safety.

Responsibilities:
- Unsafe advice prevention
- Emergency detection
- No dosage recommendations
- Educational-only responses

Example:
- Chest pain detection
- Severe symptom escalation

---

# 11. Analytics Engine

Responsibilities:
- Glucose trend analysis
- Time in range calculation
- Risky meal detection
- Sleep correlation analysis
- Dashboard insights

---

# 12. Explainable AI Layer

Purpose:
Explain why suggestions are generated.

Responses include:
- patient context used
- retrieved knowledge used
- reasoning behind guidance

---

# Current System Features

- RAG chatbot
- Food-aware intelligence
- JWT authentication
- User-specific memory
- MongoDB persistence
- Analytics dashboard
- Explainable AI
- Emergency detection
- Healthcare guardrails

---

# Future Architecture Improvements

- Agentic RAG
- Thompson Sampling
- Long-term memory
- CGM integration
- Wearable integrations
- Recommendation engine
- Multi-agent workflows