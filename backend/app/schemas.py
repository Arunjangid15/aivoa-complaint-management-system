from pydantic import BaseModel
from typing import Optional


class ExtractedComplaint(BaseModel):
    """What the AI agent returns after reading a document/email/pasted text."""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[str] = None   # ISO string, frontend/date-picker parses it
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    ai_risk_level: Optional[str] = None
    ai_risk_rationale: Optional[str] = None


class ComplaintCreate(ExtractedComplaint):
    raw_source_text: Optional[str] = None


class ComplaintOut(ComplaintCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class PasteTextRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    message: str
    current_form_state: Optional[dict] = None  # so the assistant can answer "why did you pick X"
