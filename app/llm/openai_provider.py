import json
from openai import OpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.prompt_builder import build_system_instructions, build_user_payload
from app.models.schemas import RetrievedEvidence


class OpenAIProvider(BaseLLMProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env")

        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze_issue(
        self,
        raw_error_message: str,
        evidence: list[RetrievedEvidence],
        user_notes: str | None = None,
        transaction_id: str | None = None,
    ) -> dict:
        system_instructions = build_system_instructions()
        user_payload = build_user_payload(
            raw_error_message=raw_error_message,
            evidence=evidence,
            user_notes=user_notes,
            transaction_id=transaction_id,
        )

        response = self.client.responses.create(
            model=settings.model_name,
            input=[
                {
                    "role": "system",
                    "content": system_instructions,
                },
                {
                    "role": "user",
                    "content": user_payload,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "issue_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "issue_type": {
                                "type": "string"
                            },
                            "root_cause": {
                                "type": "string"
                            },
                            "confidence": {
                                "type": "number"
                            },
                            "recommended_steps": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "approval_required": {
                                "type": "boolean"
                            },
                            "action_name": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                        "enum": [
                                            "validate_mapping",
                                            "activate_supplier_site",
                                            "reprocess_receipt",
                                            "retry_shipment_confirmation",
                                            "retry_transaction",
                                            "release_hold",
                                            "review_configuration",
                                            "assign_printer",
                                            "rerun_allocation",
                                            "escalate_issue"
                                        ]
                                    },
                                    {
                                        "type": "null"
                                    }
                                ]
                            },
                            "reasoning_summary": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "issue_type",
                            "root_cause",
                            "confidence",
                            "recommended_steps",
                            "approval_required",
                            "action_name",
                            "reasoning_summary"
                        ],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )

        return json.loads(response.output_text)