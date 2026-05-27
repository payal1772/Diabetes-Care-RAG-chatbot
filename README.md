#Diabetes RAG Chatbot

An AI-Powered diabetes wellness assistant that uses Retrieval-augmented-Generation(RAG),Gemini AI.ChromaDB,MongoDB,and healthcare guardrails to provide safe educational glucose analytics.

---

#Features

-Diabetes-Focused RAG Chatbot
-Food-aware nutrition guidance
-Explainable AI responses
-Healthcare guardrails
-Emergency detection
-JWT authentication
-User-specific memory
-MongoDB health memory
-Echarts analytics dashboard
-Query routing system
-Food intelligence system

---

#Techstack

## Frontend
-HTML
-CSS
-JavaScript
-Apache Echarts

##Backend
-Flask
-MongoDB Atlas
-ChromaDB
-SentenceTransfromers
-Gemini API
-JWT authentication

---

#Architecture Overview

Frontend
↓
JWT Authentication
↓
Flask APIs
↓
MongoDB
↓
Query Router
↓
RAG Pipeline
↓
ChromaDB
↓
Gemini
↓
Healthcare Guardrails
↓
Final Response

---

#AI Features

##Retrieval-Augmented-Generation (RAG)
The chatbot retrieves trusted diabetes and food-related knowledge before genrating responses.

##Explainable AI
Responses explain:
-why advice was given 
-what patient context was used
-what retrieved knowledge supported the answer

##Conversational Memory
Recent user conversation are stored in MongoDB and injected into propts for contextual responses.

##Food Intelligence
The chatbot uses food nutrition datasets and diabetes knowledge to provide:
-meal insights
-carbohydrate-aware glucose
-food comparisons

---

#Healthcare Safety Features
-Emergency symptom detection
-Unsafe advice prevention
-No dosage recommendation
-Educational-only healthcare guidance
-Query routing
-Guardrail layer

---

#Dashboard Features

-Glucose trend visualisation
-Sleep tracking
-water intake tracking
-Activity metrics
-Time in range analytics
-Risky meal detection
-Low sleep correlation insights

---

#Authentication Features

-User registration
-User login
_JWT authentication
-Protected APIs
-User-specific dashboard and memory

---

#knowledge Sources

-diabetes_rules.txt
-USDA food nutrition datasets
-food_knowledge.txt

---

#Setup Instructions

## Clone Repository

'''bash
git clone <repository-url>
