from typing import List, Optional
from pydantic import BaseModel, Field


class AnalyzeIssueRequest(BaseModel):
    transaction_id: Optional[str] = None
    raw_error_message: str = Field(..., min_length=5)
    user_notes: Optional[str] = None


class RetrievedEvidence(BaseModel):
    source_id: str
    source_type: str
    title: str
    snippet: str


class TransactionSnapshot(BaseModel):
    transaction_id: str
    module: str
    status: str
    severity: str
    retry_count: int
    error_message: str


class AnalyzeIssueResponse(BaseModel):
    issue_type: str
    root_cause: str
    confidence: float
    recommended_steps: List[str]
    approval_required: bool
    action_name: Optional[str] = None
    evidence: List[RetrievedEvidence] = Field(default_factory=list)
    reasoning_summary: str
    transaction_snapshot: Optional[TransactionSnapshot] = None