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

    # 1. Check for missing critical outcome data indicating failure
    if historical_outcome is not None and not historical_outcome.success:
        return "do_not_replay"

    if historical_outcome is None:
        return "do_not_replay"

    # 2. Check UI match (if not exact, need LLM reasoning to map new UI)
    if (
        current_ui_snapshot.ax_tree_json != historical_ui_snapshot.ax_tree_json
        or current_ui_snapshot.image_hash != historical_ui_snapshot.image_hash
    ):
        return "requires_llm_reasoning"

    # 3. Check for missing approval
    if historical_approval is None:
        return "requires_human_anchor"

    # 4. Check for expired replay policy
    if historical_policy is None or current_time > historical_policy.expires_at:
        return "requires_human_anchor"

    # 5. Check risk level thresholds (Risk 3 or higher strictly requires human anchor)
    if current_risk_level >= 3:
        return "requires_human_anchor"

    # 6. If all constraints pass, it's eligible for replay
    return "replay_candidate"
