from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, ai_agent, doc_parser
from .database import engine, get_db, Base

# Creates tables on startup if they don't exist yet (fine for an assignment;
# use Alembic migrations in a real production system).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA.AI — Customer Complaint Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# AI Complaint Intake Assistant
# ---------------------------------------------------------------------------

@app.post("/api/extract/text", response_model=schemas.ExtractedComplaint)
def extract_from_text(payload: schemas.PasteTextRequest):
    """User pasted complaint text/email directly into the assistant panel."""
    if not payload.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    result = ai_agent.run_extraction(payload.text)
    return result


@app.post("/api/extract/file", response_model=schemas.ExtractedComplaint)
async def extract_from_file(file: UploadFile = File(...)):
    """User dragged & dropped a PDF/DOCX/TXT/EML complaint document."""
    allowed = ("pdf", "docx", "txt", "eml")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported format. Allowed: {allowed}")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "Max file size is 10MB")

    raw_text = doc_parser.extract_text_from_upload(file.filename, content)
    if not raw_text.strip():
        raise HTTPException(422, "Could not extract any text from the document")

    result = ai_agent.run_extraction(raw_text)
    return result


@app.post("/api/chat")
def chat_with_assistant(payload: schemas.ChatRequest):
    reply = ai_agent.run_chat(payload.message, payload.current_form_state)
    return {"reply": reply}


# ---------------------------------------------------------------------------
# Log Customer Complaint (form CRUD)
# ---------------------------------------------------------------------------

@app.post("/api/complaints", response_model=schemas.ComplaintOut)
def save_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    complaint = models.Complaint(**data)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@app.get("/api/complaints", response_model=list[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@app.get("/api/complaints/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    return complaint
