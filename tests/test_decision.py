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
)
from causa_core.decision import determine_replay_decision


class TestReplayDecision(unittest.TestCase):
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

    def test_exact_ui_match_risk_1_successful_outcome(self):
        # exact UI match + Risk 1 + successful outcome => replay_candidate
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "replay_candidate")

    def test_exact_ui_match_risk_3(self):
        # exact UI match + Risk 3 => requires_human_anchor
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=3,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_failed_prior_outcome(self):
        # failed prior outcome => do_not_replay
        failed_outcome = OutcomeEvidence(
            id="out1", execution_event_id="exec1", success=False, post_execution_state="error"
        )
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=failed_outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "do_not_replay")

    def test_partial_ui_match(self):
        # partial UI match => requires_llm_reasoning
        different_ui = UISnapshot(
            id="snap2",
            anchor_case_id="case1",
            ax_tree_json="{'btn': 'click', 'extra': 'stuff'}",
            image_hash="hash456",
            ui_fingerprint_hash="fp123"
        )
        decision = determine_replay_decision(
            current_ui_snapshot=different_ui,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_llm_reasoning")

    def test_expired_replay_policy(self):
        # expired ReplayPolicy => requires_human_anchor
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now + timedelta(days=2), # current time is past expiry
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_missing_human_approval(self):
        # missing HumanApproval => requires_human_anchor
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=None,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_missing_outcome_evidence(self):
        # missing OutcomeEvidence => do_not_replay
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=None,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "do_not_replay")

    def test_missing_execution_event(self):
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=None,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "do_not_replay")

    def test_business_object_mismatch(self):
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj2",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_action_payload_mismatch(self):
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload456",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_replay_allowed_false(self):
        self.policy.replay_allowed = False
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_current_risk_level_above_policy_threshold(self):
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=3,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_historical_proposal_risk_higher_than_current_risk(self):
        self.proposal.risk_level = 3
        decision = determine_replay_decision(
            current_ui_snapshot=self.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_human_anchor")

    def test_ui_fingerprint_hash_mismatch(self):
        different_ui = UISnapshot(
            id="snap2",
            anchor_case_id="case1",
            ax_tree_json="{'btn': 'click'}",
            image_hash="hash123",
            ui_fingerprint_hash="fp456"
        )
        decision = determine_replay_decision(
            current_ui_snapshot=different_ui,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="payload123",
            historical_case=self.anchor_case,
            historical_ui_snapshot=self.ui_snapshot,
            historical_proposal=self.proposal,
            historical_approval=self.approval,
            historical_execution=self.execution,
            historical_outcome=self.outcome,
            historical_policy=self.policy,
            current_time=self.now,
        )
        self.assertEqual(decision, "requires_llm_reasoning")

if __name__ == '__main__':
    unittest.main()
