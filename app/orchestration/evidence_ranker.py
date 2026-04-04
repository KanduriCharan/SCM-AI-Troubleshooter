import re
from rapidfuzz import fuzz

from app.models.schemas import RetrievedEvidence


SOURCE_WEIGHTS = {
    "uploaded_manual": 18,
    "canonical_doc": 12,
    "incident_memory": 11,
    "policy": 10,
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with",
    "due", "because", "please", "check", "need", "from", "this", "that",
    "is", "are", "was", "were", "be", "been", "it", "as", "by", "at",
}

DOMAIN_KEYWORDS = {
    "label", "printing", "printer", "template", "barcode",
    "receiving", "receipt", "supplier", "mapping", "site",
    "shipment", "shipping", "warehouse", "carrier",
    "inventory", "allocation", "stock", "reservation",
    "timeout", "integration", "hold", "approval",
}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _extract_query_terms(query: str, transaction_snapshot: dict | None = None) -> set[str]:
    terms = set(_tokenize(query))
    filtered_terms = {term for term in terms if term in DOMAIN_KEYWORDS or len(term) > 4}

    if transaction_snapshot:
        module = transaction_snapshot.get("module", "").lower()
        if module:
            filtered_terms.add(module)

    return filtered_terms


def _score_evidence(
    query: str,
    evidence: RetrievedEvidence,
    query_terms: set[str],
    transaction_snapshot: dict | None = None,
) -> float:
    text = f"{evidence.title} {evidence.snippet}".lower()
    title = evidence.title.lower()

    fuzzy_score = fuzz.token_set_ratio(query.lower(), text)
    partial_score = fuzz.partial_ratio(query.lower(), text)

    overlap_terms = {term for term in query_terms if term in text}
    overlap_count = len(overlap_terms)

    score = 0.0
    score += SOURCE_WEIGHTS.get(evidence.source_type, 5)
    score += fuzzy_score * 0.35
    score += partial_score * 0.15
    score += overlap_count * 8

    title_matches = sum(1 for term in query_terms if term in title)
    score += title_matches * 5

    if transaction_snapshot:
        module = transaction_snapshot.get("module", "").lower()
        if module and module in text:
            score += 10

    label_terms = {"label", "printer", "template", "barcode", "printing"}
    receiving_terms = {"receiving", "receipt", "supplier", "mapping", "site"}
    shipping_terms = {"shipment", "shipping", "warehouse", "carrier"}
    inventory_terms = {"inventory", "allocation", "stock", "reservation"}

    if query_terms & label_terms:
        score += 12 if any(term in text for term in label_terms) else -18

    if query_terms & receiving_terms:
        score += 10 if any(term in text for term in receiving_terms) else -12

    if query_terms & shipping_terms:
        score += 10 if any(term in text for term in shipping_terms) else -12

    if query_terms & inventory_terms:
        score += 10 if any(term in text for term in inventory_terms) else -12

    return score


def rerank_evidence(
    query: str,
    evidence_list: list[RetrievedEvidence],
    transaction_snapshot: dict | None = None,
    top_k: int = 6,
) -> list[RetrievedEvidence]:
    query_terms = _extract_query_terms(query, transaction_snapshot)

    scored_items: list[tuple[float, RetrievedEvidence]] = []
    for evidence in evidence_list:
        score = _score_evidence(
            query=query,
            evidence=evidence,
            query_terms=query_terms,
            transaction_snapshot=transaction_snapshot,
        )
        if score >= 28:
            scored_items.append((score, evidence))

    best_by_source: dict[str, tuple[float, RetrievedEvidence]] = {}
    for score, evidence in scored_items:
        existing = best_by_source.get(evidence.source_id)
        if existing is None or score > existing[0]:
            best_by_source[evidence.source_id] = (score, evidence)

    ranked = sorted(best_by_source.values(), key=lambda x: x[0], reverse=True)
    return [item[1] for item in ranked[:top_k]]