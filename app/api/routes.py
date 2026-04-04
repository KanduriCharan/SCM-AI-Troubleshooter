from fastapi import APIRouter
from app.models.schemas import AnalyzeIssueRequest, AnalyzeIssueResponse
from app.orchestration.reasoning_service import ReasoningService

router = APIRouter()
reasoning_service = ReasoningService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalyzeIssueResponse)
def analyze_issue(payload: AnalyzeIssueRequest) -> AnalyzeIssueResponse:
    return reasoning_service.analyze_issue(payload)