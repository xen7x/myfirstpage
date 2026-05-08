from typing import Optional, List, Dict

from causa_core.models import (
    AnchorCase,
    UISnapshot,
    LLMProposal,
    HumanApproval,
    ExecutionEvent,
    OutcomeEvidence,
    ReplayPolicy,
)
from causa_core.repository import CausaRepository


class InMemoryCausaRepository(CausaRepository):
    def __init__(self):
        self._anchor_cases: Dict[str, AnchorCase] = {}
        self._ui_snapshots: Dict[str, UISnapshot] = {}
        self._llm_proposals: Dict[str, LLMProposal] = {}
        self._human_approvals: Dict[str, HumanApproval] = {}
        self._execution_events: Dict[str, ExecutionEvent] = {}
        self._outcome_evidences: Dict[str, OutcomeEvidence] = {}
        self._replay_policies: Dict[str, ReplayPolicy] = {}

    def save_anchor_case(self, anchor_case: AnchorCase) -> None:
        self._anchor_cases[anchor_case.id] = anchor_case

    def get_anchor_case(self, anchor_case_id: str) -> Optional[AnchorCase]:
        return self._anchor_cases.get(anchor_case_id)

    def list_anchor_cases(self) -> List[AnchorCase]:
        return list(self._anchor_cases.values())

    def save_ui_snapshot(self, ui_snapshot: UISnapshot) -> None:
        self._ui_snapshots[ui_snapshot.id] = ui_snapshot

    def get_ui_snapshot(self, ui_snapshot_id: str) -> Optional[UISnapshot]:
        return self._ui_snapshots.get(ui_snapshot_id)

    def save_llm_proposal(self, llm_proposal: LLMProposal) -> None:
        self._llm_proposals[llm_proposal.id] = llm_proposal

    def get_llm_proposal(self, llm_proposal_id: str) -> Optional[LLMProposal]:
        return self._llm_proposals.get(llm_proposal_id)

    def save_human_approval(self, human_approval: HumanApproval) -> None:
        self._human_approvals[human_approval.id] = human_approval

    def get_human_approval(self, human_approval_id: str) -> Optional[HumanApproval]:
        return self._human_approvals.get(human_approval_id)

    def save_execution_event(self, execution_event: ExecutionEvent) -> None:
        self._execution_events[execution_event.id] = execution_event

    def get_execution_event(self, execution_event_id: str) -> Optional[ExecutionEvent]:
        return self._execution_events.get(execution_event_id)

    def save_outcome_evidence(self, outcome_evidence: OutcomeEvidence) -> None:
        self._outcome_evidences[outcome_evidence.id] = outcome_evidence

    def get_outcome_evidence(self, outcome_evidence_id: str) -> Optional[OutcomeEvidence]:
        return self._outcome_evidences.get(outcome_evidence_id)

    def save_replay_policy(self, replay_policy: ReplayPolicy) -> None:
        self._replay_policies[replay_policy.id] = replay_policy

    def get_replay_policy(self, replay_policy_id: str) -> Optional[ReplayPolicy]:
        return self._replay_policies.get(replay_policy_id)
