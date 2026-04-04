from abc import ABC, abstractmethod
from app.models.schemas import RetrievedEvidence


class BaseLLMProvider(ABC):
    @abstractmethod
    def analyze_issue(
        self,
        raw_error_message: str,
        evidence: list[RetrievedEvidence],
        user_notes: str | None = None,
        transaction_id: str | None = None,
    ) -> dict:
        raise NotImplementedError