from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class EvidenceItem(BaseModel):
    title: str
    url: str
    snippet: str
    source: str  # "tavily" | "brave" | "semantic-scholar"
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_type: str  # "pro" | "counter"


class SubClaim(BaseModel):
    id: int
    text: str
    original_claim: str


class ConfidenceBreakdown(BaseModel):
    pro_count: int
    counter_count: int
    pro_weight: float
    counter_weight: float
    final_score: float  # 0-100


class ResearchReport(BaseModel):
    job_id: str
    claim: str
    sub_claims: List[str]
    pro_evidence: List[EvidenceItem]
    counter_evidence: List[EvidenceItem]
    confidence: ConfidenceBreakdown
    verdict: str  # "STRONGLY SUPPORTED" | "SUPPORTED" | "CONTESTED" | "REFUTED" | "STRONGLY REFUTED"
    report_markdown: str
    created_at: datetime


class CreateJobRequest(BaseModel):
    claim: str = Field(..., min_length=10, max_length=2000)


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    claim: str
    created_at: datetime


class StreamEvent(BaseModel):
    event: str  # "agent_start" | "agent_done" | "evidence_found" | "score_update" | "complete" | "error"
    agent: Optional[str] = None
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
