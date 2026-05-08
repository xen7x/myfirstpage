from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List

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


class CausaRepository(ABC):
    @abstractmethod
    def save_anchor_case(self, anchor_case: AnchorCase) -> None:
        pass

    @abstractmethod
    def get_anchor_case(self, anchor_case_id: str) -> Optional[AnchorCase]:
        pass

    @abstractmethod
    def list_anchor_cases(self) -> List[AnchorCase]:
        pass

    @abstractmethod
    def save_ui_snapshot(self, ui_snapshot: UISnapshot) -> None:
        pass

    @abstractmethod
    def get_ui_snapshot(self, ui_snapshot_id: str) -> Optional[UISnapshot]:
        pass

    @abstractmethod
    def save_llm_proposal(self, llm_proposal: LLMProposal) -> None:
        pass

    @abstractmethod
    def get_llm_proposal(self, llm_proposal_id: str) -> Optional[LLMProposal]:
        pass

    @abstractmethod
    def save_human_approval(self, human_approval: HumanApproval) -> None:
        pass

    @abstractmethod
    def get_human_approval(self, human_approval_id: str) -> Optional[HumanApproval]:
        pass

    @abstractmethod
    def save_execution_event(self, execution_event: ExecutionEvent) -> None:
        pass

    @abstractmethod
    def get_execution_event(self, execution_event_id: str) -> Optional[ExecutionEvent]:
        pass

    @abstractmethod
    def save_outcome_evidence(self, outcome_evidence: OutcomeEvidence) -> None:
        pass

    @abstractmethod
    def get_outcome_evidence(self, outcome_evidence_id: str) -> Optional[OutcomeEvidence]:
        pass

    @abstractmethod
    def save_replay_policy(self, replay_policy: ReplayPolicy) -> None:
        pass

    @abstractmethod
    def get_replay_policy(self, replay_policy_id: str) -> Optional[ReplayPolicy]:
        pass

    @abstractmethod
    def save_anchor_record(self, anchor_record: AnchorRecord) -> None:
        pass

    @abstractmethod
    def get_anchor_record(self, anchor_case_id: str) -> Optional[AnchorRecord]:
        pass
