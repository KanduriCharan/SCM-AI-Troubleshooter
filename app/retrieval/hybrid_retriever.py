from rapidfuzz import fuzz

from app.models.schemas import RetrievedEvidence
from app.retrieval.data_loader import (
    load_canonical_docs,
    load_incidents,
    load_policies,
)


def _score_text(query: str, text: str) -> int:
    return fuzz.partial_ratio(query.lower(), text.lower())


def _convert_to_evidence(record: dict) -> RetrievedEvidence:
    return RetrievedEvidence(
        source_id=record["source_id"],
        source_type=record["source_type"],
        title=record["title"],
        snippet=record["content"],
    )


def retrieve_evidence(
    raw_error_message: str,
    transaction_snapshot: dict | None = None,
) -> list[RetrievedEvidence]:
    candidates: list[tuple[int, dict]] = []

    for doc in load_canonical_docs():
        score = _score_text(raw_error_message, doc["content"] + " " + doc["title"])
        candidates.append((score, doc))

    for incident in load_incidents():
        score = _score_text(raw_error_message, incident["content"] + " " + incident["title"])
        candidates.append((score, incident))

    for policy in load_policies():
        score = _score_text(raw_error_message, policy["content"] + " " + policy["title"])
        candidates.append((score, policy))

    if transaction_snapshot:
        module = transaction_snapshot.get("module", "").lower()
        boosted: list[tuple[int, dict]] = []

        for score, record in candidates:
            record_module = record.get("module", "").lower()
            if record_module and record_module == module:
                score += 10
            boosted.append((score, record))

        candidates = boosted

    ranked = sorted(candidates, key=lambda x: x[0], reverse=True)

    top_records = []
    seen_ids = set()

    for score, record in ranked:
        if record["source_id"] in seen_ids:
            continue
        if score < 35:
            continue
        top_records.append(record)
        seen_ids.add(record["source_id"])
        if len(top_records) == 5:
            break

    return [_convert_to_evidence(record) for record in top_records]