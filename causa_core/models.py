from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnchorCase:
    id: str
    user_intent: str
    created_at: datetime


@dataclass
class UISnapshot:
    id: str
    anchor_case_id: str
    ax_tree_json: str
    image_hash: str


@dataclass
class LLMProposal:
    id: str
    anchor_case_id: str
    action_sequence: str
    risk_level: int


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
