from sqlalchemy import Column, Integer, String, Text, Date, Float, DateTime
from sqlalchemy.sql import func
from .database import Base


class Complaint(Base):
    """
    Maps 1:1 to the 'Log Customer Complaint' form sections:
      1. Origin & Customer Details
      2. Product & Batch Identification
      3. Complaint Details
      4. Initial Assessment & Priority
    """
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # 1. Origin & Customer Details
    complaint_source = Column(String(120))
    customer_name = Column(String(200))

    # 2. Product & Batch Identification
    product_name = Column(String(200))
    product_strength_grade = Column(String(100))
    batch_lot_number = Column(String(100))
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity_affected = Column(Float, nullable=True)

    # 3. Complaint Details
    complaint_type = Column(String(120))
    complaint_date = Column(Date, nullable=True)
    detailed_complaint_description = Column(Text)

    # 4. Initial Assessment & Priority
    initial_severity = Column(String(50))
    priority = Column(String(50))

    # Bonus: AI Risk Classification
    ai_risk_level = Column(String(50), nullable=True)
    ai_risk_rationale = Column(Text, nullable=True)

    status = Column(String(50), default="Pending Triage")
    raw_source_text = Column(Text, nullable=True)  # original pasted/extracted text, for audit trail

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
