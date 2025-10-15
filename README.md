# Customer Bot - AI-Powered Support Assistant

A production-ready, AI-powered customer support bot with Retrieval-Augmented Generation (RAG), robust session management, multi-tier fallback, conversation summarization, contextual action suggestions, structured logging, monitoring, and comprehensive API docs.

---

## 1) What This Project Does (Plain English)

- Answers customer questions using your FAQ knowledge base (vector search + embeddings)
- Falls back to general LLM knowledge when FAQs don’t cover it
- Escalates to a human when needed (clear message to the user)
- Keeps conversation context across turns and can summarize it
- Suggests next actions the user might want to take
- Provides structured logs, metrics, and API documentation

---

## 2) Tech Stack at a Glance

- Frontend: Vanilla HTML/CSS/JS (single page) in `frontend/index.html`
- Backend: FastAPI (async), Python 3.11
- Database: SQLite (async via SQLAlchemy)
- Vector DB: Pinecone (semantic search)
- Embeddings: `intfloat/e5-base-v2` via sentence-transformers
- LLM: Google Gemini (configurable model name)

---

## 3) How to Run (Step-by-Step)

### A. Prerequisites
- Python 3.11+
- Pip
- Pinecone account + API key
- Google Gemini API key

### B. Environment Variables (.env)
Create a `.env` at repo root with at least:
```
GEMINI_API_KEY=your_gemini_api_key
CHAT_MODEL=models/gemini-2.5-flash
EMBEDDING_MODEL=intfloat/e5-base-v2
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=ai-customer-bot-faq
DB_URL=sqlite+aiosqlite:///./data/app.db
LOG_LEVEL=INFO
TOP_K=3
SCORE_THRESHOLD=0.75
MAX_CONTEXT_CHARS=1200
```

### C. Install Dependencies
```
pip install -r backend/requirements.txt
```

### D. Start the Backend
Use uvicorn directly (FastAPI app entry is `app.main:app`, main file is `backend/app/main.py`):
```
cd backend
uvicorn app.main:app --reload --port 8000
```
- API runs at `http://localhost:8000`
- Docs at `http://localhost:8000/docs` and `http://localhost:8000/redoc`

### E. Start the Frontend
Open `frontend/index.html` in your browser (double-click or serve with any static server).

---

## 4) Quick Test Flow

1) Seed FAQs (optional – or use scripts)
```
POST /api/ingest/faq
{
  "items": [
    {"question": "How do I reset my password?", "answer": "Click 'Forgot password' on the login page."},
    {"question": "What are your support hours?", "answer": "We’re available 9am–6pm UTC."}
  ]
}
```
2) Chat
```
POST /api/chat
{
  "message": "I can’t log in",
  "include_suggestions": true,
  "include_summary": true
}
```
3) Get summary later
```
POST /api/summarize { "session_id": "<from chat response>" }
```
4) Suggest actions
```
POST /api/suggest-actions { "session_id": "<from chat response>" }
```

Scripts to demo end-to-end:
```
python scripts/test_enhanced_features.py
python scripts/test_fallback_mechanism.py
python scripts/test_contextual_suggestions.py
```

---

## 4.1) End-to-End Flow (Exact Steps)

1) Install requirements (from repo root):
```
pip install -r backend/requirements.txt
```
2) Start the backend (FastAPI via uvicorn):
```
cd backend
uvicorn app.main:app --reload --port 8000
```
3) Ingest the 200 FAQs dataset from Hugging Face (new terminal, repo root):
```
python scripts/ingest_hf_dataset.py
```
4) Open the frontend:
```
open frontend/index.html  # or double-click the file
```
5) Ask questions in the UI. The bot will answer using the ingested FAQs first, then general knowledge, or escalate if needed.

---

## 5) Frontend Overview

Single-page app (`frontend/index.html`):
- Modern chat UI (user/assistant bubbles, status indicators)
- Buttons for “Get Summary” and “Suggest Actions”
- Auto-suggestions toggle; clickable suggestions
- Shows escalation and response source (FAQ / General / Escalated)

How it talks to backend:
- `POST /api/chat` for responses (optionally returns next actions + summary)
- `POST /api/summarize` to generate a summary on-demand
- `POST /api/suggest-actions` for contextual next steps

---

## 6) Backend Overview

Structure:
- `backend/app/main.py`: FastAPI app, middleware, docs, health/metrics endpoints
- `backend/app/api/chat.py`: Chat, summarize, suggest-actions endpoints
- `backend/app/services/rag.py`: RAG pipeline, LLM calls, suggestions, summaries
- `backend/app/services/session_manager.py`: Session lifecycle, counters, cleanup
- `backend/app/services/embeddings.py`: Sentence-transformers client
- `backend/app/services/vector_store.py`: Pinecone index ops
- `backend/app/db/models.py`: `ChatSession`, `ChatMessage`
- `backend/app/db/session.py`: Async engine/session
- `backend/app/schemas.py`: Pydantic schemas
- `backend/app/utils/logger.py`: Structured logging
- `backend/app/middleware/error_handler.py`: Error + performance middleware
- `backend/app/prompts/templates.py`: Prompt templates
- `backend/app/monitoring/metrics.py`: In-memory metrics collector

Key endpoints:
- `POST /api/ingest/faq`
- `POST /api/chat`
- `POST /api/summarize`
- `POST /api/suggest-actions`
- `GET /health`
- `GET /api/metrics`

---

## 7) Enhanced Features (Merged Summary)

### Enhanced Response Generation
- Uses Gemini with trimmed conversation context and FAQ context
- Confidence scored retrieval; fast-path bypass when score ≥ 0.90
- Clear response types: `faq`, `general`, `escalated`

### Conversation Summarization
- Summarizes multi-turn conversations (< 200 words)
- Available inline with chat or separate API

### Next Action Suggestions
- Topic analysis + context to propose 4–5 relevant follow-ups
- Clickable in frontend; available via endpoint

### API Examples
- `POST /api/chat`, `POST /api/summarize`, `POST /api/suggest-actions` (see Quick Test Flow)

### Frontend Enhancements
- Buttons, toggles, loading states, error messages
- Visual distinction for response types and escalation

### Testing
- `scripts/test_enhanced_features.py` end-to-end validation

---

## 8) Enhanced Improvements (Merged Summary)

### Logging
- JSON logs; separate app/errors/performance files; contextual fields

### Error Handling
- Custom exceptions; centralized middleware; graceful JSON errors

### Session Management
- UUID sessions, message history, last activity, expiration + cleanup

### Prompt Engineering
- Centralized templates for FAQ/general/summary/actions/topic

### Performance Monitoring
- Request/system/session metrics; simple export at `/api/metrics`

### API Documentation
- Swagger and ReDoc enabled with feature descriptions

---

## 9) Fallback Mechanism (Merged Summary)

Three tiers:
1. FAQ Knowledge Base (high-confidence matches → `faq`)
2. Gemini General Knowledge (when FAQ isn’t sufficient → `general`)
3. Human Escalation (when LLM can’t help or needs internal data → `escalated`)

Smart escalation:
- Prompts instruct LLM to return `ESCALATE_TO_HUMAN` when necessary
- Confidence threshold configurable via `.env`

UI markers:
- FAQ: blue, General: green, Escalated: yellow (clearly indicated in UI)

Testing:
```
python scripts/test_fallback_mechanism.py
```

---

## 9.1) Dataset Used (Training/Knowledge Ingestion)

- Hugging Face dataset: `MakTek/Customer_support_faqs_dataset` (200 FAQs)
- This dataset is loaded and embedded via the script:
```
python scripts/ingest_hf_dataset.py
```
- After ingestion completes, the bot can answer questions based on these FAQs (via RAG), then fall back to general LLM knowledge, and escalate when necessary.

---

## 10) How Recruiters Can Evaluate Quickly

- Open `frontend/index.html`, start chatting
- Watch response type badges and suggestions
- Toggle auto-suggestions; click “Get Summary”
- Inspect logs in `logs/`; open `/docs` for API
- Review code by layers: `api/`, `services/`, `db/`, `prompts/`, `middleware/`

---

## 11) Performance Tips

- We limit history and context for faster prompts
- Retrieval uses `TOP_K=3`; high-confidence bypass avoids LLM call
- Pinecone index is created automatically if missing

---

## 12) Troubleshooting

- DB schema errors after update: remove `backend/data/app.db` (or let startup auto-migration add columns) and restart
- Missing APIs: check `.env` values; ensure keys are valid
- Slow responses: verify network latency to Gemini/Pinecone; reduce `TOP_K`, `MAX_CONTEXT_CHARS`

---

## 13) License

For recruitment demo and evaluation purposes.
