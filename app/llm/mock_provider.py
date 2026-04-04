from app.llm.base import BaseLLMProvider
from app.models.schemas import RetrievedEvidence


class MockLLMProvider(BaseLLMProvider):
    def analyze_issue(
        self,
        raw_error_message: str,
        evidence: list[RetrievedEvidence],
        user_notes: str | None = None,
        transaction_id: str | None = None,
    ) -> dict:
        text = raw_error_message.lower()

        if "supplier" in text or "mapping" in text:
            return {
                "issue_type": "Receiving Failure",
                "root_cause": "Supplier site mapping issue is the most likely cause.",
                "confidence": 0.83,
                "recommended_steps": [
                    "Validate the supplier site mapping in master data.",
                    "Correct any inactive or missing supplier site configuration.",
                    "Reprocess the receiving transaction after validation."
                ],
                "approval_required": True,
                "action_name": "reprocess_receipt",
                "reasoning_summary": "The issue was classified as a receiving failure because the error mentions supplier or mapping-related receiving context, and the retrieved evidence includes a matching runbook and similar resolved incident."
            }

        if "warehouse" in text or "shipment" in text:
            return {
                "issue_type": "Shipping Failure",
                "root_cause": "Invalid warehouse or shipment configuration is the most likely cause.",
                "confidence": 0.79,
                "recommended_steps": [
                    "Validate the warehouse code against active master data.",
                    "Check the shipment status and carrier setup.",
                    "Retry shipment confirmation after correcting setup."
                ],
                "approval_required": True,
                "action_name": "retry_shipment_confirmation",
                "reasoning_summary": "The issue was classified as shipping-related because the message mentions shipment or warehouse context, and the runbook evidence suggests configuration-driven failure."
            }

        return {
            "issue_type": "Unknown Operational Failure",
            "root_cause": "The current evidence is not strong enough to determine a single root cause.",
            "confidence": 0.45,
            "recommended_steps": [
                "Review the transaction details.",
                "Inspect recent incident history for similar failures.",
                "Escalate to support if the issue repeats."
            ],
            "approval_required": True,
            "action_name": None,
            "reasoning_summary": "The available evidence is weak or ambiguous, so the system is returning a low-confidence recommendation."
        }