# AIVOA.AI — AI-Powered Customer Complaint Management System

Pharmaceutical (API & FDF) Customer Complaint intake system: an AI copilot
extracts structured fields from a pasted email/document and auto-fills the
"Log Customer Complaint" QMS form.

## Architecture

```
User uploads/pastes complaint
        │
        ▼
Frontend (React + Redux)  ──POST /api/extract/file or /text──▶  FastAPI
        │                                                          │
        │                                                          ▼
        │                                              doc_parser.py (pdf/docx/eml/txt → text)
        │                                                          │
        │                                                          ▼
        │                                        LangGraph pipeline (ai_agent.py):
        │                                        extract_fields → validate_fields → risk_classify
        │                                        (Groq gemma2-9b-it)
        │                                                          │
        ◀────────────── JSON matching form schema ─────────────────┘
        │
Redux populateFromExtraction() fills the form
        │
        ▼
User reviews/edits → Save Complaint → POST /api/complaints → Postgres/MySQL
```

## Backend setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY + DATABASE_URL
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`. Set `VITE_API_BASE_URL` in a `.env` file
if the backend isn't on `localhost:8000`.

## Key design decisions

- **LangGraph** models the AI pipeline as an explicit graph
  (`extract_fields → validate_fields → risk_classify`) instead of one
  giant prompt — makes each step independently testable and easy to
  extend (e.g. add a "duplicate detection" node later).
- **gemma2-9b-it** does the structured JSON extraction (fast, cheap,
  good enough for field extraction); **llama-3.3-70b-versatile** powers
  the free-form "ask me anything" chat where more reasoning helps.
- **Redux** holds the single source of truth for form state so both the
  manual-edit path and the AI-extraction path write through the same
  reducer (`populateFromExtraction`), avoiding two competing state trees.
- Document parsing (`doc_parser.py`) is intentionally simple — the
  assignment explicitly waives production-grade OCR.

## Bonus feature implemented

- **AI Risk Classification** — after extraction, a second Groq call
  classifies the complaint as Critical / Major / Minor with a short
  rationale, shown in the "AI Copilot Risk Assessment" box on the form.

## Not implemented (documented as future work)

- Complaint Completeness Checker, Root Cause Recommendation, Duplicate
  Detection, CAPA Recommendation, Complaint Summary — same LangGraph
  pattern can be extended with additional nodes/routes for these.
