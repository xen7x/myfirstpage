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
) -> str:
    """
    Returns one of:
    - 'replay_candidate'
    - 'requires_llm_reasoning'
    - 'requires_human_anchor'
    - 'do_not_replay'
    """

    # Check for execution/outcome failures
    if historical_outcome is None or historical_execution is None:
        return "do_not_replay"
    if not historical_outcome.success:
        return "do_not_replay"

    # Check for missing approvals or policies
    if historical_approval is None:
        return "requires_human_anchor"
    if historical_policy is None or current_time > historical_policy.expires_at:
        return "requires_human_anchor"
    if not historical_policy.replay_allowed:
        return "requires_human_anchor"

    # Check risk thresholds
    effective_risk_level = max(current_risk_level, historical_proposal.risk_level)
    if effective_risk_level >= 3:
        return "requires_human_anchor"
    if effective_risk_level > historical_policy.max_auto_replay_risk_level:
        return "requires_human_anchor"

    # Check UI Match
    if (
        current_ui_snapshot.ui_fingerprint_hash != historical_ui_snapshot.ui_fingerprint_hash
        or current_ui_snapshot.ax_tree_json != historical_ui_snapshot.ax_tree_json
        or current_ui_snapshot.image_hash != historical_ui_snapshot.image_hash
    ):
        return "requires_llm_reasoning"

    # Check object and payload matches
    if current_business_object_id != historical_case.business_object_id:
        return "requires_human_anchor"
    if current_action_payload_hash != historical_proposal.action_payload_hash:
        return "requires_human_anchor"

    return "replay_candidate"
