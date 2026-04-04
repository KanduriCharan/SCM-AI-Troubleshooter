from app.models.schemas import AnalyzeIssueResponse


HIGH_RISK_ACTION_KEYWORDS = {
    "reprocess",
    "retry",
    "release",
    "change",
    "update",
    "activate",
    "deactivate",
    "resubmit",
    "rerun",
    "reassign",
    "correct",
}

LOW_CONFIDENCE_THRESHOLD = 0.75
MEDIUM_CONFIDENCE_THRESHOLD = 0.85
RETRY_ESCALATION_THRESHOLD = 2


def _contains_high_risk_action(response: AnalyzeIssueResponse) -> bool:
    text_parts = []

    if response.action_name:
        text_parts.append(response.action_name.lower())

    for step in response.recommended_steps:
        text_parts.append(step.lower())

    combined_text = " ".join(text_parts)

    return any(keyword in combined_text for keyword in HIGH_RISK_ACTION_KEYWORDS)


def _is_medium_or_high_severity(response: AnalyzeIssueResponse) -> bool:
    if not response.transaction_snapshot:
        return False

    severity = response.transaction_snapshot.severity.lower()
    return severity in {"medium", "high", "critical"}


def _has_multiple_retries(response: AnalyzeIssueResponse) -> bool:
    if not response.transaction_snapshot:
        return False

    return response.transaction_snapshot.retry_count >= RETRY_ESCALATION_THRESHOLD


def _is_unknown_or_ambiguous(response: AnalyzeIssueResponse) -> bool:
    issue_type = response.issue_type.lower()
    root_cause = response.root_cause.lower()
    reasoning = response.reasoning_summary.lower()

    ambiguous_phrases = [
        "not strong enough",
        "uncertain",
        "ambiguous",
        "not enough evidence",
        "conflicting evidence",
    ]

    return (
        "unknown" in issue_type
        or "unknown" in root_cause
        or any(phrase in reasoning for phrase in ambiguous_phrases)
    )


def apply_guardrails(response: AnalyzeIssueResponse) -> AnalyzeIssueResponse:
    # 1. Low confidence should always require approval.
    if response.confidence < LOW_CONFIDENCE_THRESHOLD:
        response.approval_required = True

    # 2. Unknown or ambiguous diagnosis should never propose an action.
    if _is_unknown_or_ambiguous(response):
        response.action_name = None
        response.approval_required = True

    # 3. Medium/high severity + risky action should require approval.
    if _is_medium_or_high_severity(response) and _contains_high_risk_action(response):
        response.approval_required = True

    # 4. Repeated retries should force escalation behavior.
    if _has_multiple_retries(response):
        response.approval_required = True

        if response.action_name and "escalate" not in response.action_name.lower():
            response.action_name = "escalate_issue"

        if "Escalate to support for deeper investigation." not in response.recommended_steps:
            response.recommended_steps.append(
                "Escalate to support for deeper investigation."
            )

    # 5. Medium-confidence answers should not auto-approve risky actions.
    if (
        response.confidence < MEDIUM_CONFIDENCE_THRESHOLD
        and _contains_high_risk_action(response)
    ):
        response.approval_required = True
    # 6. If the diagnosis is strong but action_name is missing, apply a conservative fallback.
    if response.action_name is None and response.confidence >= 0.85:
        issue_type = response.issue_type.lower()
        reasoning = response.reasoning_summary.lower()
        steps = " ".join(response.recommended_steps).lower()

        if "mapping" in issue_type or "mapping" in reasoning or "mapping" in steps:
            response.action_name = "validate_mapping"
        elif "receiving" in issue_type or "receipt" in steps:
            response.action_name = "reprocess_receipt"
        elif "shipment" in issue_type:
            response.action_name = "retry_shipment_confirmation"
        elif "allocation" in issue_type:
            response.action_name = "rerun_allocation"

    return response