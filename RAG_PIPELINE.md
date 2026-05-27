# RAG Pipeline

This document explains the Retrieval-Augmented Generation (RAG) pipeline used in the Diabetes RAG Chatbot.

---

# What is RAG?

RAG (Retrieval-Augmented Generation) is an AI architecture where the system retrieves trusted knowledge before generating a response.

Instead of relying only on generic LLM knowledge, the chatbot retrieves diabetes and food-related information from a healthcare knowledge base.

---

# Why RAG was used

Healthcare AI systems should provide:
- grounded responses
- explainable answers
- trusted information
- safer guidance

Without RAG:
- LLMs may hallucinate
- responses may become generic
- healthcare answers may become unreliable

With RAG:
- relevant healthcare knowledge is retrieved first
- Gemini generates responses using retrieved context

---

# RAG Architecture Flow

Knowledge Base
↓
Text Chunking
↓
Embedding Creation
↓
ChromaDB Storage
↓
User Query
↓
Query Embedding
↓
Similarity Search
↓
Prompt Augmentation
↓
Gemini Response
↓
Guardrails
↓
Final Response

---

# Step 1: Knowledge Base

Current knowledge sources:
- diabetes_rules.txt
- food_knowledge.txt
- USDA food datasets

The knowledge base contains:
- diabetes education
- food nutrition data
- carbohydrate information
- lifestyle guidance
- symptom-related information

---

# Step 2: Text Chunking

Large documents are split into smaller chunks before embedding generation.

Reason:
- improves retrieval quality
- improves semantic search
- reduces irrelevant retrieval

Current implementation:
- split_text()
- fixed chunk size approach

Example chunk:

Food: White rice
Carbohydrates: 28g
Glycemic impact: High

---

# Step 3: Embedding Generation

Technology:
- SentenceTransformers

Model:
- all-MiniLM-L6-v2

Purpose:
Convert text into numerical vector representations.

Example:

"Rice may increase glucose"

↓
Embedding Vector

[0.282, -0.771, 0.194, ...]

---

# Why Embeddings are Important

Embeddings help the system understand semantic meaning instead of exact keyword matching.

Example:

User Query:
"Can rice spike sugar?"

Retriever can still find:

"White rice may increase glucose levels"

even though wording differs.

This is semantic retrieval.

---

# Step 4: Vector Database Storage

Technology:
- ChromaDB

Purpose:
Store:
- embeddings
- chunk text
- semantic indexes

Storage Location:
- vector_store/

Main Responsibilities:
- vector similarity search
- nearest-neighbor retrieval
- fast semantic retrieval

---

# Step 5: User Query Processing

When a user asks a healthcare-related question:

Example:
"Can I eat rice if glucose is high?"

The query is:
- embedded
- converted into vector representation

---

# Step 6: Similarity Search

ChromaDB compares:
- user query embedding
with:
- stored knowledge embeddings

Then retrieves:
- top relevant chunks

Example retrieved chunks:
- rice carbohydrate information
- diabetes food guidance
- glucose spike education

---

# Step 7: Prompt Augmentation

Retrieved knowledge is injected into the Gemini prompt.

Prompt also includes:
- patient metrics
- conversational memory
- explainability instructions
- safety instructions

Prompt Inputs:
- user question
- retrieved knowledge
- recent memory
- patient health context

---

# Step 8: Gemini Response Generation

Technology:
- Gemini API

Gemini generates:
- contextual responses
- grounded answers
- explainable guidance

The model uses:
- retrieved healthcare knowledge
- user context
- conversational memory

---

# Step 9: Explainability Layer

Responses explain:
- why suggestions were given
- what patient context was used
- what retrieved knowledge supported the answer

Example:

Why This Suggestion:
- Glucose level was high after rice-based meal
- Retrieved food knowledge indicates rice is high in carbohydrates

---

# Step 10: Guardrails

After generation:
- healthcare safety checks are applied

Guardrails prevent:
- unsafe advice
- dosage recommendations
- misleading medical responses

Emergency escalation is also handled.

---

# Query Routing

Not every user query triggers RAG.

Generic questions:
- hello
- how are you

use normal conversational responses.

Healthcare questions:
- glucose
- food
- symptoms
- diabetes guidance

trigger RAG retrieval.

---

# Current RAG Features

- Semantic retrieval
- Food-aware intelligence
- Explainable AI
- Healthcare guardrails
- Source citations
- Conversational memory
- User-specific retrieval

---

# Current Limitations

- Basic chunking strategy
- No reranking model
- Limited long-term memory
- No hybrid search
- Limited nutrition dataset coverage

---

# Future Improvements

- Agentic RAG
- Hybrid retrieval
- Knowledge graph integration
- Better reranking
- Personalized retrieval
- Long-term memory retrieval
- CGM-aware retrieval