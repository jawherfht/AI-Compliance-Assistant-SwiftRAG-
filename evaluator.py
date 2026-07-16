import json, re
import ollama
from pydantic import BaseModel, Field
from rag_client import CHAT_MODEL
from vectorstore import search

class AuditResult(BaseModel):
    control_id: str
    coverage: str = Field(description="Covered or Partially or Not Covered")
    gap_summary: list[str]
    risk: str
    recommendation: list[str]
    confidence: float

SYSTEM_PROMPT = """You are a security auditor.
Use only the provided evidence. If evidence is insufficient, return Not Covered.
Respond ONLY with a JSON object with the exact keys:
control_id, coverage (Covered|Partially|Not Covered),
gap_summary (array of up to 3 short strings),
risk (short string),
recommendation (array of up to 2 short strings),
confidence (number 0-1).
Do not include any extra text before or after the JSON.
"""

def evaluate_control(control_id: str, control_name: str, question: str, k: int = 5) -> dict:
    hits = search(question, k=k)
    docs = hits.get("documents", [[]])[0]

    if not docs:
        return {
            "control_id": control_id,
            "coverage": "Not Covered",
            "gap_summary": ["No relevant evidence was found in uploaded documents."],
            "risk": "Control cannot be verified from available evidence.",
            "recommendation": ["Provide policy/SOP sections that address this control."],
            "confidence": 0.3,
        }

    evidence = "\n---\n".join(docs)

    resp = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content":
                f"CONTROL: {control_id} - {control_name}\n"
                f"QUESTION: {question}\n"
                f"EVIDENCE:\n{evidence}"
            },
        ],
        format="json",
        options={"temperature": 0.2},
    )

    txt = resp["message"]["content"].strip()

    try:
        data = json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                data = json.loads(m.group(0))
            except Exception:
                data = None
        else:
            data = None

        if not data:
            data = {
                "control_id": control_id,
                "coverage": "Not Covered",
                "gap_summary": ["Could not parse model output"],
                "risk": "Unclear",
                "recommendation": ["Re-run analysis with more evidence"],
                "confidence": 0.0,
            }

    data.setdefault("control_id", control_id)
    return data