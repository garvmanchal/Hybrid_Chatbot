   # 🤖 Hybrid Chatbot

A full-stack AI chatbot built with **FastAPI, React, RAG, hybrid retrieval, reranking, and multi-model LLM routing**.

The project is designed as a production-oriented GenAI application where the chatbot can answer questions from a knowledge base and from user-uploaded PDF documents. It also supports model fallback when the primary provider is unavailable.

> **Current development focus:** RAG + document ingestion + LLM orchestration.  
> **Planned next feature:** JWT-based authentication and a login/register flow.

---

## ✨ Features

### AI / RAG
- 📚 Retrieval-Augmented Generation (RAG)
- 📄 PDF text extraction with PyMuPDF
- ✂️ Document chunking with overlap
- 🔢 Lightweight text embeddings
- 🔎 Vector similarity search
- 🔤 BM25-style keyword retrieval
- 🔀 Reciprocal Rank Fusion (RRF) for hybrid search
- 🎯 Reranking of retrieved chunks
- 📝 Citation-aware prompts using labels such as `[C1]`
- 👤 Session-scoped uploaded documents

### LLM / Orchestration
- 🔀 Rule-based model routing
- ⚡ Fast model route for simple requests
- ⚖️ Balanced model route for normal requests
- 🧠 Long-context route
- 🔍 Strong/review route
- 🔁 Gemini → Groq fallback when Gemini is unavailable
- 📦 Structured JSON-style LLM responses
- 🚨 Human-review flag for unsupported/invalid RAG responses

### Backend
- 🚀 FastAPI
- ⚡ Async API endpoints
- 📤 Multipart file uploads
- 🔐 Environment-variable based API keys
- 🌐 CORS configuration
- 🧩 Modular RAG architecture

### Frontend
- ⚛️ React 19
- 🟦 TypeScript
- ⚡ Vite
- 🧭 React Router
- 💬 WhatsApp-style chat interface
- 📎 PDF/image attachment UI
- ⏳ Loading / typing state
- 🧾 Attachment status messages

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │     React Client    │
                    │  TypeScript + Vite  │
                    └──────────┬──────────┘
                               │
                     question + session_id
                               │
                         optional file
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI /chat/   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Document Ingest   │
                    │                     │
                    │ PDF → Text → Chunks │
                    │       → Embeddings  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    In-Memory DB     │
                    │  chunks + vectors   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Hybrid Search     │
                    │                     │
                    │ Vector Search       │
                    │       +             │
                    │ BM25 Search         │
                    │       ↓             │
                    │ RRF Fusion           │
                    └──────────┬──────────┘
                               │
                          top candidates
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Reranker       │
                    └──────────┬──────────┘
                               │
                          top chunks
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Prompt Builder    │
                    │  Evidence + [C#]    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    LLM Router       │
                    │                     │
                    │ Gemini / Groq       │
                    │ + fallback          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Structured Response │
                    │ answer + citations  │
                    │ + review flag       │
                    └─────────────────────┘
```

---

# 📂 Project Structure

```text
Hybrid Chatbot/
│
├── backend/
│   ├── main.py
│   │
│   ├── chat/
│   │   └── routes.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embedding.py
│   │   ├── ingest.py
│   │   ├── pdf_loader.py
│   │   ├── prompt.py
│   │   ├── reranker.py
│   │   ├── search.py
│   │   ├── seed_index.py
│   │   └── vector_db.py
│   │
│   └── services/
│       ├── chat_service.py
│       └── llm_client.py
│
├── frontend_react/
│   └── react-app/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── package.json
│       └── vite.config.ts
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 🔄 RAG Pipeline

The current RAG pipeline follows:

```text
PDF Upload
    ↓
PyMuPDF
    ↓
Page Text
    ↓
Chunking
    ↓
Embedding
    ↓
In-Memory Vector DB
    ↓
       ┌───────────────┐
       │               │
       ▼               ▼
 Vector Search      BM25 Search
       │               │
       └───────┬───────┘
               ▼
          RRF Fusion
               ↓
          Top 30 chunks
               ↓
            Rerank
               ↓
          Top 15 chunks
               ↓
       Citation Prompt
               ↓
             LLM
               ↓
          Final Answer
```

## Chunking

Documents are split into approximately **60-word chunks** with **15-word overlap**.

The overlap helps preserve context between adjacent chunks.

---

# 📄 File Upload Flow

The React frontend sends:

```text
question
session_id
file
```

using `multipart/form-data`.

The backend validates:

- PDF
- JPG
- PNG
- WEBP
- Maximum size: 10 MB

Currently:

- **PDF text** is extracted and indexed.
- **Images** are accepted but are not searchable yet because an OCR/vision ingestion pipeline has not been implemented.

Uploaded PDF chunks receive a session-specific permission scope:

```text
session:<session_id>
```

This allows the retrieval layer to search the uploaded document only within the relevant chat session.

---

# 🔎 Hybrid Search

The project combines two retrieval strategies.

### 1. Vector Search

The query is converted into a vector and compared with stored chunk vectors using cosine similarity.

### 2. Keyword Search

A lightweight BM25-style keyword overlap implementation retrieves chunks containing terms from the query.

### 3. Reciprocal Rank Fusion

The two ranked lists are combined using RRF:

```text
BM25 results
      +
Vector results
      ↓
RRF
      ↓
Combined ranking
```

This gives the system both semantic and keyword-based retrieval behavior.

---

# 🎯 Reranking

After hybrid search retrieves up to 30 candidates, the reranker calculates semantic similarity again and keeps the best 15 chunks.

```text
30 candidates
      ↓
Reranker
      ↓
15 chunks
```

These chunks are then supplied to the LLM.

---

# 📝 Citation-Aware Generation

The prompt builder labels retrieved evidence:

```text
[C1]
[C2]
[C3]
...
```

The model is instructed to cite factual statements using those labels.

Example:

```text
The company's working hours are 9:00 AM to 6:00 PM [C2].
```

The backend extracts citation labels from the final answer and returns them to the frontend.

---

# 🤖 LLM Routing

The current router selects a model route based on the prompt.

| Route | Purpose |
|---|---|
| `fast_model` | Simple / quick requests |
| `balanced_model` | Default route |
| `long_context_model` | Large prompts |
| `strong_model_with_review` | Debug / analyze / code-review style prompts |

Current model configuration is defined in:

```text
backend/services/llm_client.py
```

The application currently uses Google Gemini and Groq-hosted models.

---

# 🔁 Provider Fallback

If the selected Gemini model returns a server-side error, the application switches to the Groq fallback model.

```text
Gemini
  │
  ├── Success → return Gemini response
  │
  └── Server error
          ↓
       Groq fallback
          ↓
       return response
```

This allows the chatbot to continue working when the primary provider is temporarily unavailable.

---

# 🧠 Casual Conversation Routing

Simple conversational messages such as:

```text
hi
hello
hey
thanks
how are you
what's up
```

are detected before RAG retrieval.

They follow a lighter path:

```text
User message
     ↓
Casual detection
     ↓
LLM
     ↓
Response
```

A casual message does not need document retrieval or citations.

---

# 🌐 API

## Health / Root

```http
GET /
```

Example response:

```json
{
  "message": "This is my chatbot"
}
```

## Chat

```http
POST /chat/
```

The current endpoint accepts multipart form data.

### Fields

```text
question
session_id
file (optional)
```

Example conceptual request:

```text
question = "What are the working hours?"
session_id = "unique-session-id"
file = employee-handbook.pdf
```

### Example response

```json
{
  "answer": "The working hours are ... [C2].",
  "citations": ["[C2]"],
  "needs_human_review": false,
  "model_routing": "balanced_model",
  "attachment": {
    "filename": "employee-handbook.pdf",
    "indexed": true,
    "chunks_indexed": 12,
    "note": null
  }
}
```

> The exact response fields can evolve as the API is developed.

---

# ⚛️ Frontend

The frontend is located at:

```text
frontend_react/react-app/
```

Run it with:

```bash
cd frontend_react/react-app
npm install
npm run dev
```

The Vite development server normally runs at:

```text
http://localhost:5173
```

The backend CORS configuration currently allows:

```text
http://localhost:5173
```

---

# 🐍 Backend Setup

From the project root:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install fastapi groq google-genai python-dotenv uvicorn pydantic pymupdf python-multipart
```

Then start the backend:

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Never commit real API keys.

The repository already contains `.gitignore` rules for:

```text
.env
venv/
__pycache__/
*.pyc
node_modules/
dist/
```

If an API key is ever exposed publicly, revoke/rotate it immediately.

---

# 🔐 Planned Authentication: JWT + Login

Authentication is the next major frontend/backend feature.

The planned architecture is:

```text
                  User
                   │
                   ▼
              Login Page
                   │
                   ▼
            POST /auth/login
                   │
                   ▼
        Backend verifies credentials
                   │
                   ▼
             JWT issued
                   │
                   ▼
        React authenticated state
                   │
                   ▼
        Protected /chat/ request
                   │
                   ▼
       Backend validates JWT
                   │
                   ▼
              Chat / RAG
```

### Important

JWT authentication should **not be implemented only in React**.

The frontend should provide the login UI and send authentication credentials/token, but the **backend must verify the JWT** before allowing access to protected endpoints.

The planned backend pieces are:

```text
backend/
├── auth/
│   ├── routes.py
│   ├── jwt.py
│   └── dependencies.py
│
└── ...
```

The planned frontend pieces are:

```text
frontend_react/react-app/src/
├── pages/
│   ├── Login.tsx
│   └── ...
│
├── auth/
│   ├── AuthContext.tsx
│   └── ...
│
└── ...
```

After authentication is implemented, the authenticated user's identity can also be connected to document permissions instead of relying only on the current client-generated session ID.

---

# 🔒 Planned Security Model

The long-term architecture should move from:

```text
session_id → document scope
```

toward:

```text
authenticated user
        ↓
user_id
        ↓
chat/session
        ↓
document permissions
        ↓
RAG retrieval
```

This allows the backend to enforce document isolation independently of the frontend.

---

# ⚠️ Current Limitations

- The vector database is currently **in-memory**.
- Restarting the backend clears the in-memory uploaded-document index.
- The current embedding implementation is lightweight and intended for learning/prototyping rather than production semantic retrieval.
- Image uploads are accepted but are not currently indexed.
- There is no persistent user/database layer yet.
- JWT authentication/login is planned but not yet implemented in this version.
- There is no production-grade authorization system yet.
- Human review is represented by a flag; there is no actual review dashboard/workflow.
- LLM cost tracking is currently simplified.
- Model routing is rule-based.
- The current application is intended primarily for development/learning and needs additional hardening before production deployment.

---

# 🚀 Roadmap

### Phase 1 — Core RAG
- [x] PDF text extraction
- [x] Chunking
- [x] Embeddings
- [x] Vector search
- [x] Keyword search
- [x] Hybrid search
- [x] RRF
- [x] Reranking
- [x] Citation-aware prompting

### Phase 2 — AI Application
- [x] LLM routing
- [x] Gemini integration
- [x] Groq integration
- [x] Provider fallback
- [x] Casual-message routing
- [x] PDF upload
- [x] Session-scoped document ingestion

### Phase 3 — Authentication
- [ ] Login page
- [ ] User registration
- [ ] JWT generation
- [ ] JWT verification middleware/dependency
- [ ] Protected chat endpoint
- [ ] User-specific document permissions
- [ ] Logout / token handling

### Phase 4 — Production RAG
- [ ] Persistent vector database
- [ ] Better embedding model
- [ ] OCR / vision ingestion
- [ ] Document management
- [ ] Persistent conversation history
- [ ] Better retrieval evaluation
- [ ] Automated RAG evaluation
- [ ] Monitoring and structured logging

### Phase 5 — Advanced AI Orchestration
- [ ] Tool calling
- [ ] Workflow/state management
- [ ] Retry policies
- [ ] Model fallback chains
- [ ] Human-in-the-loop workflow
- [ ] Agentic workflows
- [ ] Evaluation and reliability layer

---

# 🧰 Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- PyMuPDF
- Google GenAI SDK
- Groq SDK
- python-dotenv

## Frontend

- React 19
- TypeScript
- Vite
- React Router

## AI / RAG

- Embeddings
- Vector similarity search
- BM25-style retrieval
- Reciprocal Rank Fusion
- Reranking
- Citation-aware RAG
- LLM routing
- Provider fallback

---

# 🎯 What This Project Demonstrates

This project demonstrates practical implementation of a modern GenAI application:

```text
Frontend
   ↓
API
   ↓
Authentication [planned]
   ↓
Document ingestion
   ↓
RAG retrieval
   ↓
Hybrid search
   ↓
Reranking
   ↓
Prompt engineering
   ↓
LLM routing
   ↓
Fallback handling
   ↓
Structured response
```

It is therefore more than a basic chatbot: it combines **backend engineering, RAG, LLM integration, retrieval, orchestration, and frontend development** in one application.

---

# 📌 Development Notes

The repository currently contains some legacy/unused code from earlier versions of the project, including older request/response schemas and a commented-out seed-index implementation.

The active chat flow is centered around:

```text
backend/chat/routes.py
backend/rag/ingest.py
backend/services/chat_service.py
backend/rag/search.py
backend/rag/reranker.py
backend/rag/prompt.py
backend/services/llm_client.py
```

When extending the application, prefer the active upload/ingestion flow instead of reactivating the older commented-out route/seed code without reviewing the current architecture.

---

## 📄 License

This project is currently intended for learning, portfolio development, and experimentation. Add an appropriate open-source license before distributing it publicly.
