# API Documentation

This document explains all backend APIs used in the Diabetes RAG Chatbot.

Base URL:

```text
http://127.0.0.1:5000
```

---

# Authentication APIs

## 1. Register User

Endpoint:

```text
POST /api/register
```

Purpose:
Create a new user account.

Request Body:

```json
{
  "name": "Payal",
  "email": "payal@test.com",
  "password": "123456"
}
```

Success Response:

```json
{
  "message": "User registered successfully"
}
```

Error Response:

```json
{
  "error": "User already exists"
}
```

---

# 2. Login User

Endpoint:

```text
POST /api/login
```

Purpose:
Authenticate user and generate JWT token.

Request Body:

```json
{
  "email": "payal@test.com",
  "password": "123456"
}
```

Success Response:

```json
{
  "message": "Login successful",
  "token": "jwt_token_here",
  "name": "Payal"
}
```

---

# Chatbot APIs

## 3. Chat Endpoint

Endpoint:

```text
POST /api/chat
```

Authentication:
JWT Protected

Purpose:
Main healthcare chatbot endpoint.

Features:
- RAG retrieval
- Food intelligence
- Conversational memory
- Explainable AI
- Guardrails
- Query routing

Headers:

```text
Authorization: Bearer <jwt_token>
```

Request Body:

```json
{
  "message": "Can rice increase glucose?",
  "glucose": 185,
  "meal": "Rice",
  "sleep": 5,
  "water": 4,
  "steps": 2000,
  "symptoms": "Fatigue"
}
```

Success Response:

```json
{
  "answer": "Rice may increase glucose...",
  "sources": [
    "Food: White rice...",
    "High carbohydrate meals..."
  ]
}
```

---

# Dashboard APIs

## 4. Dashboard Data API

Endpoint:

```text
GET /api/dashboard
```

Authentication:
JWT Protected

Purpose:
Returns dashboard chart data.

Headers:

```text
Authorization: Bearer <jwt_token>
```

Success Response:

```json
{
  "glucose_logs": [...]
}
```

Returned Metrics:
- glucose
- meal
- sleep
- water
- steps
- symptoms

---

# Analytics APIs

## 5. Analytics Endpoint

Endpoint:

```text
GET /api/analytics
```

Authentication:
JWT Protected

Purpose:
Returns advanced healthcare analytics.

Headers:

```text
Authorization: Bearer <jwt_token>
```

Success Response:

```json
{
  "average_glucose": 152,
  "highest_glucose": 240,
  "time_in_range": 72,
  "risky_meal": "Rice and curry",
  "low_sleep_high_glucose": 190
}
```

Analytics Generated:
- Average glucose
- Highest glucose
- Time in range
- Risky meal detection
- Low sleep correlation

---

# Profile APIs

## 6. User Profile Endpoint

Endpoint:

```text
GET /api/profile
```

Authentication:
JWT Protected

Purpose:
Returns user profile information.

Headers:

```text
Authorization: Bearer <jwt_token>
```

Success Response:

```json
{
  "name": "Payal",
  "email": "payal@test.com",
  "total_logs": 42,
  "average_glucose": 154
}
```

---

# Query Routing System

The chatbot classifies user queries into:
- Generic conversation
- Healthcare RAG
- Analytics requests
- Emergency detection

Example Routing:

```text
hello
↓
Generic response

Can rice increase glucose?
↓
RAG retrieval

What is my average glucose?
↓
Analytics engine

I feel chest pain
↓
Emergency escalation
```

---

# Emergency Handling

Emergency symptoms:
- chest pain
- severe dizziness
- breathing difficulty
- unconsciousness

Emergency queries bypass normal RAG flow and trigger safety escalation responses.

Example Emergency Response:

```json
{
  "answer": "Emergency Warning: Please contact a healthcare professional immediately."
}
```

---

# Authentication Flow

```text
User Login
↓
JWT Token Generated
↓
Frontend stores token
↓
Token sent in API headers
↓
Backend validates token
```

---

# Security Features

Protected APIs:
- /api/chat
- /api/dashboard
- /api/analytics
- /api/profile

Security Implementations:
- JWT authentication
- User-specific data isolation
- Protected API routes
- MongoDB Atlas
- Environment variable protection
- Guardrail layer

---

# Explainable AI

The chatbot explains:
- why suggestions were generated
- what patient context was used
- what retrieved knowledge supported the answer

Example:

```text
Why This Suggestion:
- Your glucose level was high after a rice-based meal.
- Retrieved food knowledge indicates rice is high in carbohydrates.
```

---

# Knowledge Sources

Current knowledge sources:
- diabetes_rules.txt
- food_knowledge.txt
- USDA food datasets

---

# Error Responses

Unauthorized:

```json
{
  "error": "Token is invalid"
}
```

Missing Token:

```json
{
  "error": "Token is missing"
}
```

Internal Error:

```json
{
  "error": "Something went wrong"
}
```

---

# Current System Features

- RAG chatbot
- Explainable AI
- Food intelligence
- Conversational memory
- Analytics dashboard
- JWT authentication
- MongoDB persistence
- Query routing
- Emergency detection
- Healthcare guardrails

---

# Future APIs

Planned APIs:
- Food comparison API
- Recommendation engine API
- Wearable integration API
- CGM simulation API
- Long-term memory API

---

# Disclaimer

This project is intended for educational and wellness-support purposes only and should not replace professional medical advice.