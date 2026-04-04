from app.core.config import settings
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.models.schemas import AnalyzeIssueRequest, AnalyzeIssueResponse, TransactionSnapshot
from app.policies.guardrails import apply_guardrails
from app.retrieval.hybrid_retriever import retrieve_evidence
from app.retrieval.transaction_lookup import get_transaction_by_id
from app.RAG.document_retriever import retrieve_document_evidence
from app.orchestration.evidence_ranker import rerank_evidence

class ReasoningService:
    def __init__(self) -> None:
        if settings.openai_api_key:
            self.llm_provider = OpenAIProvider()
        else:
            self.llm_provider = MockLLMProvider()

    def analyze_issue(self, request: AnalyzeIssueRequest) -> AnalyzeIssueResponse:
        transaction_data = get_transaction_by_id(request.transaction_id)

        csv_evidence = retrieve_evidence(
            raw_error_message=request.raw_error_message,
            transaction_snapshot=transaction_data,
        )
        rag_evidence = retrieve_document_evidence(
            query=request.raw_error_message,
            k=8,
        )
        raw_evidence = csv_evidence + rag_evidence
        evidence = rerank_evidence(
            query=request.raw_error_message,
            evidence_list=raw_evidence,
            transaction_snapshot=transaction_data,
            top_k=6,
        )


        llm_result = self.llm_provider.analyze_issue(
            raw_error_message=request.raw_error_message,
            evidence=evidence,
            user_notes=request.user_notes,
            transaction_id=request.transaction_id,
        )

        transaction_snapshot = (
            TransactionSnapshot(**transaction_data) if transaction_data else None
        )

        response = AnalyzeIssueResponse(
            issue_type=llm_result["issue_type"],
            root_cause=llm_result["root_cause"],
            confidence=llm_result["confidence"],
            recommended_steps=llm_result["recommended_steps"],
            approval_required=llm_result["approval_required"],
            action_name=llm_result["action_name"],
            evidence=evidence,
            reasoning_summary=llm_result["reasoning_summary"],
            transaction_snapshot=transaction_snapshot,
        )

        return apply_guardrails(response)