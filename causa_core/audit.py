from typing import Optional
from causa_core.models import ReplayDecision, AnchorRecord, AuditSummary


def build_audit_summary(
    decision: ReplayDecision,
    historical_record: Optional[AnchorRecord] = None,
) -> AuditSummary:
    """
    Builds a human-readable audit summary from a ReplayDecision and an optional AnchorRecord.
    """

    summary = ""
    if decision.status == "replay_candidate":
        summary = "Replay is eligible for this AnchorCase."
    elif decision.status == "requires_human_anchor":
        summary = "Human re-approval is required before replay."
    elif decision.status == "requires_llm_reasoning":
        summary = "LLM reasoning is required because the current context differs from the historical precedent."
    elif decision.status == "do_not_replay":
        summary = "Replay is not allowed for this historical case."

    details = [f"Decision Message: {decision.message}"]
    if decision.anchor_case_id:
        details.append(f"Anchor Case ID: {decision.anchor_case_id}")

    if historical_record:
        if historical_record.anchor_case:
            details.append(f"User Intent: {historical_record.anchor_case.user_intent}")
            if historical_record.anchor_case.business_object_id:
                details.append(f"Business Object ID: {historical_record.anchor_case.business_object_id}")

        if historical_record.llm_proposal:
            details.append(f"Historical Risk Level: {historical_record.llm_proposal.risk_level}")

        if historical_record.replay_policy:
            details.append(f"Policy Max Auto Replay Risk Level: {historical_record.replay_policy.max_auto_replay_risk_level}")

        details.append(f"Human Approval Exists: {'Yes' if historical_record.human_approval else 'No'}")
        details.append(f"Execution Event Exists: {'Yes' if historical_record.execution_event else 'No'}")

        if historical_record.outcome_evidence:
            details.append(f"Outcome Evidence Exists: Yes, Success: {historical_record.outcome_evidence.success}")
        else:
            details.append("Outcome Evidence Exists: No")

        details.append(f"Replay Policy Exists: {'Yes' if historical_record.replay_policy else 'No'}")

    return AuditSummary(
        status=decision.status,
        reason_code=decision.reason_code,
        anchor_case_id=decision.anchor_case_id,
        summary=summary,
        details=details
    )
