"""
FastAPI REST API Server for Grade Evidence Certainty Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from grade_evidence_certainty_agent.certainty import CertaintyAssessment, assess_certainty
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Grade Evidence Certainty Agent API",
    description="Enterprise Distributed Component Platform (Legacy metric threshold demonstration)",
    version="3.0.0-ENTERPRISE",
)


class GradeRequest(BaseModel):
    study_design: str
    risk_of_bias: int = Field(default=0, ge=0, le=2, strict=True)
    inconsistency: int = Field(default=0, ge=0, le=2, strict=True)
    indirectness: int = Field(default=0, ge=0, le=2, strict=True)
    imprecision: int = Field(default=0, ge=0, le=2, strict=True)
    publication_bias: int = Field(default=0, ge=0, le=2, strict=True)
    large_effect: int = Field(default=0, ge=0, le=2, strict=True)
    dose_response: int = Field(default=0, ge=0, le=1, strict=True)
    plausible_confounding: int = Field(default=0, ge=0, le=1, strict=True)


@app.post("/api/grade")
def api_grade(req: GradeRequest):
    try:
        return assess_certainty(CertaintyAssessment(**req.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "grade-evidence-certainty-agent", "domain": "Legacy metric threshold demonstration", "standard": "Internal demonstration rules only", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
