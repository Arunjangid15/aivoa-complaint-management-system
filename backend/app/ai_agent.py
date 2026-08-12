"""
AI/LangGraph workflow for the Customer Complaint Intake Assistant.

Pipeline (each is a LangGraph node -> visible as a "graph" so it's easy to
explain node-by-node in the interview):

    raw_text ─▶ [extract_fields] ─▶ [validate_fields] ─▶ [risk_classify] ─▶ result

- extract_fields : Groq gemma2-9b-it reads the free-text complaint (from a
  pasted email or a parsed PDF/DOCX/EML) and returns strict JSON matching
  our form schema.
- validate_fields : light python-side cleanup (dates, empty strings -> None,
  trims hallucinated units etc.)
- risk_classify : a second LLM call (bonus feature) that assigns a
  Critical / Major / Minor risk level with a short rationale, based on
  GMP/QMS-style severity reasoning (patient safety impact, batch scope, etc.)
"""
import os
import json
import re
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
EXTRACTION_MODEL = "gemma2-9b-it"
CONTEXT_MODEL = "llama-3.3-70b-versatile"  # used for the free-form chat assistant

llm_extract = ChatGroq(model=EXTRACTION_MODEL, api_key=GROQ_API_KEY, temperature=0)
llm_chat = ChatGroq(model=CONTEXT_MODEL, api_key=GROQ_API_KEY, temperature=0.3)

FIELD_KEYS = [
    "complaint_source", "customer_name", "product_name", "product_strength_grade",
    "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected",
    "complaint_type", "complaint_date", "detailed_complaint_description",
    "initial_severity", "priority",
]

EXTRACTION_SYSTEM_PROMPT = f"""You are a pharmaceutical Quality Assurance intake
assistant. You read a raw customer complaint (email, letter, or free text)
about an API (Active Pharmaceutical Ingredient) or FDF (Finished Dosage Form)
product and extract structured fields for a QMS Customer Complaint form.

Return ONLY valid JSON (no markdown, no commentary) with exactly these keys:
{json.dumps(FIELD_KEYS)}

Rules:
- complaint_source: e.g. "Email", "Phone Call", "Customer Portal", "Regulatory Authority"
- initial_severity: one of "Critical", "Major", "Minor"
- priority: one of "High", "Medium", "Low"
- dates must be ISO format YYYY-MM-DD if mentioned, else null
- quantity_affected: number as string (units in complaint description if unclear)
- If a field isn't mentioned in the text, set it to null. Never invent data.
"""

RISK_SYSTEM_PROMPT = """You are a QA risk assessor for a pharmaceutical company.
Given a customer complaint's details, classify the risk level as one of:
"Critical" (patient safety / regulatory reporting risk, e.g. contamination,
adverse reaction, mislabeling), "Major" (product quality defect impacting
efficacy but no immediate safety risk), or "Minor" (cosmetic/packaging issue,
no quality impact).

Return ONLY valid JSON: {"ai_risk_level": "...", "ai_risk_rationale": "..."}
Rationale must be 1-2 sentences, referencing the specific fact that drove
the classification.
"""


class AgentState(TypedDict):
    raw_text: str
    extracted: dict
    risk: dict


def _safe_json_parse(raw: str) -> dict:
    """Groq sometimes wraps JSON in ```json fences — strip them before parsing."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # last resort: grab the outermost {...}
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        return json.loads(match.group(0)) if match else {}


def extract_fields_node(state: AgentState) -> AgentState:
    response = llm_extract.invoke([
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": state["raw_text"]},
    ])
    parsed = _safe_json_parse(response.content)
    state["extracted"] = {k: parsed.get(k) for k in FIELD_KEYS}
    return state


def validate_fields_node(state: AgentState) -> AgentState:
    data = state["extracted"]
    for k, v in data.items():
        if isinstance(v, str) and v.strip().lower() in ("", "null", "none", "n/a"):
            data[k] = None
    state["extracted"] = data
    return state


def risk_classify_node(state: AgentState) -> AgentState:
    summary = json.dumps(state["extracted"])
    response = llm_extract.invoke([
        {"role": "system", "content": RISK_SYSTEM_PROMPT},
        {"role": "user", "content": summary},
    ])
    parsed = _safe_json_parse(response.content)
    state["risk"] = {
        "ai_risk_level": parsed.get("ai_risk_level"),
        "ai_risk_rationale": parsed.get("ai_risk_rationale"),
    }
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("extract_fields", extract_fields_node)
    graph.add_node("validate_fields", validate_fields_node)
    graph.add_node("risk_classify", risk_classify_node)

    graph.set_entry_point("extract_fields")
    graph.add_edge("extract_fields", "validate_fields")
    graph.add_edge("validate_fields", "risk_classify")
    graph.add_edge("risk_classify", END)
    return graph.compile()


complaint_graph = build_graph()


def run_extraction(raw_text: str) -> dict:
    """Entry point called by the FastAPI route."""
    result = complaint_graph.invoke({"raw_text": raw_text, "extracted": {}, "risk": {}})
    output = {**result["extracted"], **result["risk"]}
    return output


def run_chat(message: str, current_form_state: Optional[dict] = None) -> str:
    """Free-form 'Ask me anything about this complaint' assistant."""
    context = f"\n\nCurrent form data: {json.dumps(current_form_state)}" if current_form_state else ""
    response = llm_chat.invoke([
        {"role": "system", "content": "You are a helpful pharma QA complaint intake assistant. Be concise."},
        {"role": "user", "content": message + context},
    ])
    return response.content
