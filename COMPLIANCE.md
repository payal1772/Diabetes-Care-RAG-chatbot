# Compliance

This document explains the compliance considerations for the Diabetes RAG Chatbot.

---

# Purpose

The Diabetes RAG Chatbot is an educational and wellness-support system. It is designed to provide general diabetes-related lifestyle guidance, food awareness, glucose tracking insights, and safe conversational support.

It is not designed to diagnose, prescribe medication, replace doctors, or make emergency medical decisions.

---

# Compliance Scope

This project considers healthcare AI compliance principles related to:

- Patient data privacy
- Secure authentication
- User-specific data isolation
- Safe AI responses
- Medical advice limitations
- Emergency escalation
- Data protection awareness
- Explainability and transparency

---

# Healthcare Disclaimer

The chatbot provides educational guidance only.

It should not be used for:

- Medical diagnosis
- Medication prescription
- Insulin dosage decisions
- Emergency treatment
- Replacing professional healthcare consultation

Users should consult a qualified healthcare professional for medical decisions.

---

# HIPAA Awareness

HIPAA is a healthcare privacy and security framework used in the United States.

This project is not claiming full HIPAA compliance, but it follows HIPAA-inspired practices such as:

- Protecting patient health data
- Using authentication
- Restricting access to user-specific data
- Avoiding unnecessary exposure of health information
- Keeping API keys and secrets in environment variables
- Applying safety controls around medical responses

Healthcare-related data handled by the system includes:

- Glucose readings
- Meal information
- Sleep data
- Water intake
- Steps/activity data
- Symptoms
- Chat history

---

# GDPR Awareness

GDPR is a data protection regulation used in the European Union.

This project is not claiming full GDPR compliance, but it follows GDPR-inspired practices such as:

- Collecting only relevant user data
- Using authentication before accessing personal data
- Storing user-specific data separately
- Supporting the idea of user data deletion in future versions
- Avoiding unnecessary storage of sensitive data

Future improvements may include:

- Delete account option
- Export user data
- Consent management
- Data retention policy
- User-controlled memory deletion

---

# Data Privacy Measures

The system protects user data using:

- JWT authentication
- Protected API routes
- MongoDB user-specific filtering
- Environment variables for secrets
- Separate user-specific glucose logs
- Separate user-specific chat memory

Each user should only access their own:

- Health metrics
- Chat history
- Dashboard analytics
- Profile information

---

# Authentication and Access Control

The system uses JWT authentication.

Flow:

```text
User Login
↓
JWT Token Generated
↓
Frontend stores token
↓
Token sent with API requests
↓
Backend validates token
↓
User-specific data is returned
```

Protected APIs include:

- `/api/chat`
- `/api/dashboard`
- `/api/analytics`
- `/api/profile`

---

# User Data Isolation

Each health log and chat memory entry is linked with a `user_id`.

This prevents one user from viewing another user's:

- Glucose logs
- Chat history
- Dashboard insights
- Profile data

This is important for healthcare privacy.

---

# AI Safety Compliance

The chatbot includes safety layers to reduce the risk of harmful medical responses.

Safety controls include:

- Emergency detection
- Medical guardrails
- No dosage recommendations
- No diagnosis claims
- No medication changes
- Educational-only response style
- Doctor consultation recommendation when needed

---

# Emergency Escalation

If the system detects emergency-related symptoms, it bypasses normal RAG response generation and returns an urgent warning.

Emergency symptoms include:

- Chest pain
- Breathing difficulty
- Severe dizziness
- Confusion
- Fainting
- Unconsciousness
- Vomiting
- Extreme weakness

Emergency responses instruct users to seek professional medical help immediately.

---

# Medical Guardrails

The system blocks or avoids unsafe advice such as:

- Take insulin
- Increase insulin
- Decrease insulin
- Stop medication
- Change your dose
- Ignore symptoms
- You definitely have a disease

If unsafe advice is detected, the system returns a safer response recommending professional medical consultation.

---

# RAG and Trusted Knowledge

The chatbot uses Retrieval-Augmented Generation to reduce hallucination risk.

Instead of relying only on generic LLM knowledge, the system retrieves information from:

- Diabetes knowledge base
- Food knowledge base
- USDA nutrition dataset

This improves:

- Grounding
- Explainability
- Consistency
- Safety

---

# Explainability

The system includes explainable AI behavior.

Responses may explain:

- Why the suggestion was given
- Which patient context was used
- Which retrieved knowledge supported the answer
- What safety limitations apply

This helps users understand the reasoning behind chatbot guidance.

---

# Data Storage

MongoDB stores:

- User accounts
- Glucose logs
- Chat history
- Health metrics
- Dashboard analytics data

Sensitive secrets such as API keys and database URIs are stored in `.env` and should not be committed to GitHub.

---

# Environment Variables

The following values should be stored securely:

```env
GEMINI_API_KEY=
MONGO_URI=
JWT_SECRET=
```

The `.env` file should be added to `.gitignore`.

---

# Limitations

This project does not currently implement full legal compliance.

Current limitations include:

- No formal HIPAA certification
- No formal GDPR compliance workflow
- No consent management system
- No data deletion workflow
- No audit log dashboard
- No clinical validation
- No medical professional review workflow

---

# Future Compliance Improvements

Planned improvements:

- User consent screen
- Delete account and data option
- Export personal data
- Audit logs
- Role-based access control
- Doctor/admin review workflow
- Data retention policy
- Encryption improvements
- Clinical review of knowledge base
- Compliance checklist for deployment

---

# Compliance Statement

This project is a student/portfolio healthcare AI system built for educational purposes. It follows privacy-aware and safety-aware design principles, but it should not be considered legally compliant for real clinical deployment without professional legal, medical, and security review.