import json
from app.models.schemas import RetrievedEvidence


ALLOWED_ACTIONS = [
    "validate_mapping",
    "activate_supplier_site",
    "reprocess_receipt",
    "retry_shipment_confirmation",
    "retry_transaction",
    "release_hold",
    "review_configuration",
    "assign_printer",
    "rerun_allocation",
    "escalate_issue",
    None,
]


def build_system_instructions() -> str:
    return f"""
You are an enterprise SCM troubleshooting assistant.

Your job is to analyze supply-chain operational failures using only the evidence provided.
Do not invent root causes that are not supported by the evidence.
Do not recommend risky actions unless the evidence supports them.
If evidence is weak or conflicting, lower confidence and say so.
Always think like an enterprise support engineer, not a casual chatbot.

You must choose action_name only from this allowed list:
{ALLOWED_ACTIONS}

Choose:
- "validate_mapping" for mapping validation steps
- "activate_supplier_site" when supplier site activation is the key corrective action
- "reprocess_receipt" for receiving reprocessing
- "retry_shipment_confirmation" for shipment retry actions
- "retry_transaction" for generic safe retry
- "release_hold" for hold-related issues
- "review_configuration" for setup/config review
- "assign_printer" for label/printing issues
- "rerun_allocation" for allocation failures
- "escalate_issue" when retries failed, evidence is conflicting, or support intervention is needed
- null only if no action should be proposed

Return only the fields required by the schema.
""".strip()


def build_user_payload(
    raw_error_message: str,
    evidence: list[RetrievedEvidence],
    user_notes: str | None = None,
    transaction_id: str | None = None,
    transaction_snapshot: dict | None = None,
) -> str:
    payload = {
        "transaction_id": transaction_id,
        "transaction_snapshot": transaction_snapshot,
        "raw_error_message": raw_error_message,
        "user_notes": user_notes,
        "retrieved_evidence": [
            {
                "source_id": item.source_id,
                "source_type": item.source_type,
                "title": item.title,
                "snippet": item.snippet,
            }
            for item in evidence
        ],
        "task": (
            "Analyze the issue, identify the most likely issue type and root cause, "
            "estimate confidence, recommend next steps, choose exactly one allowed action_name or null, "
            "determine whether approval is required, and provide a concise reasoning summary grounded in the evidence."
        ),
    }
    return json.dumps(payload, indent=2)