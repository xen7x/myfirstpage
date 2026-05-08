from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnchorCase:
    id: str
    user_intent: str
    created_at: datetime
    business_object_id: Optional[str]


@dataclass
class UISnapshot:
    id: str
    anchor_case_id: str
    ax_tree_json: str
    image_hash: str
    ui_fingerprint_hash: str


@dataclass
class LLMProposal:
    id: str
    anchor_case_id: str
    action_sequence: str
    risk_level: int
    action_payload_hash: str


@dataclass
class HumanApproval:
    id: str
    llm_proposal_id: str
    approved_at: datetime


@dataclass
class ExecutionEvent:
    id: str
    human_approval_id: str
    executed_at: datetime


@dataclass
class OutcomeEvidence:
    id: str
    execution_event_id: str
    success: bool
    post_execution_state: Optional[str]


@dataclass
class ReplayPolicy:
    id: str
    anchor_case_id: str
    expires_at: datetime
    replay_allowed: bool
    max_auto_replay_risk_level: int


@dataclass
class ReplayDecision:
    status: str
    reason_code: str
    message: str
    anchor_case_id: Optional[str]


@dataclass
class AnchorRecord:
    anchor_case: AnchorCase
    ui_snapshot: Optional[UISnapshot]
    llm_proposal: Optional[LLMProposal]
    human_approval: Optional[HumanApproval]
    execution_event: Optional[ExecutionEvent]
    outcome_evidence: Optional[OutcomeEvidence]
    replay_policy: Optional[ReplayPolicy]


@dataclass
class AuditSummary:
    status: str
    reason_code: str
    anchor_case_id: Optional[str]
    summary: str
    details: list[str]
