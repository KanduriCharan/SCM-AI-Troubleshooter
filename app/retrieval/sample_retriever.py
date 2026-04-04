from app.models.schemas import RetrievedEvidence

SAMPLE_KNOWLEDGE = [
    {
        "source_id": "RUNBOOK-001",
        "source_type": "runbook",
        "title": "Receiving Validation Failures",
        "snippet": "Receiving failures often occur due to supplier site mapping issues, invalid item codes, quantity mismatches, or duplicate receipts."
    },
    {
        "source_id": "RUNBOOK-002",
        "source_type": "runbook",
        "title": "Shipment Confirmation Failures",
        "snippet": "Shipment confirmation may fail due to invalid warehouse codes, ineligible order line status, missing carrier setup, or interface timeouts."
    },
    {
        "source_id": "INCIDENT-101",
        "source_type": "incident_memory",
        "title": "Resolved Supplier Site Mapping Error",
        "snippet": "A previous receiving failure was resolved by activating the correct supplier site mapping and reprocessing the receipt transaction."
    },
    {
        "source_id": "POLICY-001",
        "source_type": "policy",
        "title": "Approval Policy",
        "snippet": "High-risk or uncertain actions must require human approval before any corrective action is executed."
    },
]


def retrieve_evidence(raw_error_message: str) -> list[RetrievedEvidence]:
    text = raw_error_message.lower()
    results: list[RetrievedEvidence] = []

    if "supplier" in text or "receiving" in text or "receipt" in text:
        results.append(RetrievedEvidence(**SAMPLE_KNOWLEDGE[0]))
        results.append(RetrievedEvidence(**SAMPLE_KNOWLEDGE[2]))

    if "shipment" in text or "warehouse" in text or "carrier" in text:
        results.append(RetrievedEvidence(**SAMPLE_KNOWLEDGE[1]))

    results.append(RetrievedEvidence(**SAMPLE_KNOWLEDGE[3]))
    return results