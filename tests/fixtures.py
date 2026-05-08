from datetime import datetime, timedelta
from causa_core.models import (
    AnchorCase,
    UISnapshot,
    LLMProposal,
    HumanApproval,
    ExecutionEvent,
    OutcomeEvidence,
    ReplayPolicy,
    AnchorRecord,
)

FIXED_NOW = datetime(2024, 1, 1, 12, 0, 0)


def _build_base_record(case_id: str, risk_level: int, success: bool, policy_expires_at: datetime) -> AnchorRecord:
    anchor_case = AnchorCase(id=case_id, user_intent="test intent", created_at=FIXED_NOW, business_object_id="obj1")
    ui_snapshot = UISnapshot(id=f"snap_{case_id}", anchor_case_id=case_id, ax_tree_json="{}", image_hash="img", ui_fingerprint_hash="fp123")
    llm_proposal = LLMProposal(id=f"prop_{case_id}", anchor_case_id=case_id, action_sequence="act", risk_level=risk_level, action_payload_hash="pay123")
    human_approval = HumanApproval(id=f"app_{case_id}", llm_proposal_id=f"prop_{case_id}", approved_at=FIXED_NOW)
    execution_event = ExecutionEvent(id=f"exec_{case_id}", human_approval_id=f"app_{case_id}", executed_at=FIXED_NOW)
    outcome_evidence = OutcomeEvidence(id=f"out_{case_id}", execution_event_id=f"exec_{case_id}", success=success, post_execution_state="state")
    replay_policy = ReplayPolicy(id=f"pol_{case_id}", anchor_case_id=case_id, expires_at=policy_expires_at, replay_allowed=True, max_auto_replay_risk_level=2)

    return AnchorRecord(
        anchor_case=anchor_case,
        ui_snapshot=ui_snapshot,
        llm_proposal=llm_proposal,
        human_approval=human_approval,
        execution_event=execution_event,
        outcome_evidence=outcome_evidence,
        replay_policy=replay_policy,
    )


def build_successful_anchor_record() -> AnchorRecord:
    return _build_base_record(
        case_id="case_success",
        risk_level=1,
        success=True,
        policy_expires_at=FIXED_NOW + timedelta(days=1)
    )


def build_failed_anchor_record() -> AnchorRecord:
    return _build_base_record(
        case_id="case_fail",
        risk_level=1,
        success=False,
        policy_expires_at=FIXED_NOW + timedelta(days=1)
    )


def build_risk3_anchor_record() -> AnchorRecord:
    return _build_base_record(
        case_id="case_risk3",
        risk_level=3,
        success=True,
        policy_expires_at=FIXED_NOW + timedelta(days=1)
    )


def build_expired_policy_anchor_record() -> AnchorRecord:
    return _build_base_record(
        case_id="case_expired",
        risk_level=1,
        success=True,
        policy_expires_at=FIXED_NOW - timedelta(days=1)
    )
