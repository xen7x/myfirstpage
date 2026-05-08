from datetime import datetime
from typing import Optional

from causa_core.models import (
    UISnapshot,
    AnchorCase,
    LLMProposal,
    HumanApproval,
    ExecutionEvent,
    OutcomeEvidence,
    ReplayPolicy,
    ReplayDecision,
    AnchorRecord,
)


def determine_replay_decision(
    current_ui_snapshot: UISnapshot,
    current_risk_level: int,
    current_business_object_id: Optional[str],
    current_action_payload_hash: str,
    historical_case: AnchorCase,
    historical_ui_snapshot: UISnapshot,
    historical_proposal: LLMProposal,
    historical_approval: Optional[HumanApproval],
    historical_execution: Optional[ExecutionEvent],
    historical_outcome: Optional[OutcomeEvidence],
    historical_policy: Optional[ReplayPolicy],
    current_time: datetime,
) -> ReplayDecision:
    """
    Returns a ReplayDecision object containing the status, reason code, message, and anchor_case_id.
    """

    anchor_id = historical_case.id if historical_case else None

    def make_decision(status: str, reason_code: str, message: str) -> ReplayDecision:
        return ReplayDecision(
            status=status,
            reason_code=reason_code,
            message=message,
            anchor_case_id=anchor_id
        )

    # Check for execution/outcome failures
    if historical_outcome is None:
        return make_decision("do_not_replay", "MISSING_OUTCOME_EVIDENCE", "Historical outcome evidence is missing.")
    if historical_execution is None:
        return make_decision("do_not_replay", "MISSING_EXECUTION_EVENT", "Historical execution event is missing.")
    if not historical_outcome.success:
        return make_decision("do_not_replay", "FAILED_PRIOR_OUTCOME", "The historical execution failed.")

    # Check for missing approvals or policies
    if historical_approval is None:
        return make_decision("requires_human_anchor", "MISSING_HUMAN_APPROVAL", "Historical human approval is missing.")
    if historical_policy is None:
        return make_decision("requires_human_anchor", "MISSING_REPLAY_POLICY", "Historical replay policy is missing.")
    if current_time > historical_policy.expires_at:
        return make_decision("requires_human_anchor", "EXPIRED_REPLAY_POLICY", "The replay policy has expired.")
    if not historical_policy.replay_allowed:
        return make_decision("requires_human_anchor", "REPLAY_NOT_ALLOWED", "Replay is not allowed by the policy.")

    # Check risk thresholds
    effective_risk_level = max(current_risk_level, historical_proposal.risk_level)
    if effective_risk_level >= 3:
        return make_decision("requires_human_anchor", "RISK_REQUIRES_HUMAN_ANCHOR", "Risk level is 3 or higher, requiring human anchor.")
    if effective_risk_level > historical_policy.max_auto_replay_risk_level:
        return make_decision("requires_human_anchor", "RISK_ABOVE_POLICY_THRESHOLD", "Risk level exceeds the policy threshold.")

    # Check UI Match
    if (
        current_ui_snapshot.ui_fingerprint_hash != historical_ui_snapshot.ui_fingerprint_hash
        or current_ui_snapshot.ax_tree_json != historical_ui_snapshot.ax_tree_json
        or current_ui_snapshot.image_hash != historical_ui_snapshot.image_hash
    ):
        return make_decision("requires_llm_reasoning", "UI_FINGERPRINT_MISMATCH", "Current UI fingerprint does not exactly match the historical UI.")

    # Check object and payload matches
    if current_business_object_id != historical_case.business_object_id:
        return make_decision("requires_human_anchor", "BUSINESS_OBJECT_MISMATCH", "Business object ID does not match.")
    if current_action_payload_hash != historical_proposal.action_payload_hash:
        return make_decision("requires_human_anchor", "ACTION_PAYLOAD_MISMATCH", "Action payload hash does not match.")

    return make_decision("replay_candidate", "REPLAY_ELIGIBLE", "All checks passed. Replay is eligible.")


def determine_replay_decision_from_record(
    current_ui_snapshot: UISnapshot,
    current_risk_level: int,
    current_business_object_id: Optional[str],
    current_action_payload_hash: str,
    historical_record: Optional[AnchorRecord],
    current_time: datetime,
) -> ReplayDecision:
    if historical_record is None:
        return ReplayDecision(
            status="do_not_replay",
            reason_code="MISSING_ANCHOR_RECORD",
            message="No historical AnchorRecord was found.",
            anchor_case_id=None,
        )

    return determine_replay_decision(
        current_ui_snapshot=current_ui_snapshot,
        current_risk_level=current_risk_level,
        current_business_object_id=current_business_object_id,
        current_action_payload_hash=current_action_payload_hash,
        historical_case=historical_record.anchor_case,
        historical_ui_snapshot=historical_record.ui_snapshot,
        historical_proposal=historical_record.llm_proposal,
        historical_approval=historical_record.human_approval,
        historical_execution=historical_record.execution_event,
        historical_outcome=historical_record.outcome_evidence,
        historical_policy=historical_record.replay_policy,
        current_time=current_time,
    )
