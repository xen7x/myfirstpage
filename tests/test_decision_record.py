import unittest
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
from causa_core.decision import determine_replay_decision_from_record


class TestReplayDecisionFromRecord(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2024, 1, 1, 12, 0, 0)

        self.anchor_case = AnchorCase(id="case1", user_intent="do thing", created_at=self.now, business_object_id="obj1")

        self.ui_snapshot = UISnapshot(
            id="snap1",
            anchor_case_id="case1",
            ax_tree_json="{'btn': 'click'}",
            image_hash="hash123",
            ui_fingerprint_hash="fp123"
        )

        self.proposal = LLMProposal(
            id="prop1",
            anchor_case_id="case1",
            action_sequence="click btn",
            risk_level=1,
            action_payload_hash="payload123"
        )

        self.approval = HumanApproval(
            id="app1",
            llm_proposal_id="prop1",
            approved_at=self.now
        )

        self.execution = ExecutionEvent(
            id="exec1",
            human_approval_id="app1",
            executed_at=self.now
        )

        self.outcome = OutcomeEvidence(
            id="out1",
            execution_event_id="exec1",
            success=True,
            post_execution_state="done"
        )

        self.policy = ReplayPolicy(
            id="pol1",
            anchor_case_id="case1",
            expires_at=self.now + timedelta(days=1),
            replay_allowed=True,
            max_auto_replay_risk_level=2
        )

        self.complete_record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=self.ui_snapshot,
            llm_proposal=self.proposal,
            human_approval=self.approval,
            execution_event=self.execution,
            outcome_evidence=self.outcome,
            replay_policy=self.policy
        )

    def test_complete_record_eligible(self):
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=self.complete_record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "replay_candidate")
        self.assertEqual(decision.reason_code, "REPLAY_ELIGIBLE")

    def test_missing_historical_record(self):
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=None,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "do_not_replay")
        self.assertEqual(decision.reason_code, "MISSING_ANCHOR_RECORD")
        self.assertIsNone(decision.anchor_case_id)

    def test_missing_outcome_evidence(self):
        record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=self.ui_snapshot,
            llm_proposal=self.proposal,
            human_approval=self.approval,
            execution_event=self.execution,
            outcome_evidence=None,
            replay_policy=self.policy
        )
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "do_not_replay")
        self.assertEqual(decision.reason_code, "MISSING_OUTCOME_EVIDENCE")

    def test_missing_execution_event(self):
        record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=self.ui_snapshot,
            llm_proposal=self.proposal,
            human_approval=self.approval,
            execution_event=None,
            outcome_evidence=self.outcome,
            replay_policy=self.policy
        )
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "do_not_replay")
        self.assertEqual(decision.reason_code, "MISSING_EXECUTION_EVENT")

    def test_missing_human_approval(self):
        record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=self.ui_snapshot,
            llm_proposal=self.proposal,
            human_approval=None,
            execution_event=self.execution,
            outcome_evidence=self.outcome,
            replay_policy=self.policy
        )
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "MISSING_HUMAN_APPROVAL")

    def test_missing_replay_policy(self):
        record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=self.ui_snapshot,
            llm_proposal=self.proposal,
            human_approval=self.approval,
            execution_event=self.execution,
            outcome_evidence=self.outcome,
            replay_policy=None
        )
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "MISSING_REPLAY_POLICY")

    def test_ui_fingerprint_mismatch(self):
        different_ui = UISnapshot(
            id="snap2",
            anchor_case_id="case1",
            ax_tree_json="{'btn': 'click'}",
            image_hash="hash123",
            ui_fingerprint_hash="fp456"
        )
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=different_ui,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_record=self.complete_record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "requires_llm_reasoning")
        self.assertEqual(decision.reason_code, "UI_FINGERPRINT_MISMATCH")

    def test_business_object_mismatch(self):
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj2",
            current_action_payload_hash="payload123",
            historical_record=self.complete_record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "BUSINESS_OBJECT_MISMATCH")

    def test_action_payload_mismatch(self):
        decision = determine_replay_decision_from_record(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload456",
            historical_record=self.complete_record,
            current_time=self.now,
        )
        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "ACTION_PAYLOAD_MISMATCH")


if __name__ == '__main__':
    unittest.main()
