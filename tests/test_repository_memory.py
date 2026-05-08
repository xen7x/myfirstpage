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
from causa_core.storage.memory import InMemoryCausaRepository


class TestInMemoryCausaRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryCausaRepository()
        self.now = datetime(2024, 1, 1, 12, 0, 0)

    def test_anchor_case_storage(self):
        case = AnchorCase(id="case1", user_intent="intent", created_at=self.now, business_object_id="obj1")
        self.assertIsNone(self.repo.get_anchor_case("case1"))

        self.repo.save_anchor_case(case)

        saved_case = self.repo.get_anchor_case("case1")
        self.assertEqual(saved_case, case)

        cases = self.repo.list_anchor_cases()
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0], case)

    def test_ui_snapshot_storage(self):
        snap = UISnapshot(id="snap1", anchor_case_id="case1", ax_tree_json="{}", image_hash="img", ui_fingerprint_hash="fp")
        self.assertIsNone(self.repo.get_ui_snapshot("snap1"))

        self.repo.save_ui_snapshot(snap)

        saved_snap = self.repo.get_ui_snapshot("snap1")
        self.assertEqual(saved_snap, snap)

    def test_llm_proposal_storage(self):
        prop = LLMProposal(id="prop1", anchor_case_id="case1", action_sequence="act", risk_level=1, action_payload_hash="pay")
        self.assertIsNone(self.repo.get_llm_proposal("prop1"))

        self.repo.save_llm_proposal(prop)

        saved_prop = self.repo.get_llm_proposal("prop1")
        self.assertEqual(saved_prop, prop)

    def test_human_approval_storage(self):
        app = HumanApproval(id="app1", llm_proposal_id="prop1", approved_at=self.now)
        self.assertIsNone(self.repo.get_human_approval("app1"))

        self.repo.save_human_approval(app)

        saved_app = self.repo.get_human_approval("app1")
        self.assertEqual(saved_app, app)

    def test_execution_event_storage(self):
        exec_ev = ExecutionEvent(id="exec1", human_approval_id="app1", executed_at=self.now)
        self.assertIsNone(self.repo.get_execution_event("exec1"))

        self.repo.save_execution_event(exec_ev)

        saved_exec = self.repo.get_execution_event("exec1")
        self.assertEqual(saved_exec, exec_ev)

    def test_outcome_evidence_storage(self):
        out = OutcomeEvidence(id="out1", execution_event_id="exec1", success=True, post_execution_state="done")
        self.assertIsNone(self.repo.get_outcome_evidence("out1"))

        self.repo.save_outcome_evidence(out)

        saved_out = self.repo.get_outcome_evidence("out1")
        self.assertEqual(saved_out, out)

    def test_replay_policy_storage(self):
        pol = ReplayPolicy(id="pol1", anchor_case_id="case1", expires_at=self.now + timedelta(days=1), replay_allowed=True, max_auto_replay_risk_level=2)
        self.assertIsNone(self.repo.get_replay_policy("pol1"))

        self.repo.save_replay_policy(pol)

        saved_pol = self.repo.get_replay_policy("pol1")
        self.assertEqual(saved_pol, pol)

    def test_anchor_record_storage_complete(self):
        case = AnchorCase(id="case1", user_intent="intent", created_at=self.now, business_object_id="obj1")
        snap = UISnapshot(id="snap1", anchor_case_id="case1", ax_tree_json="{}", image_hash="img", ui_fingerprint_hash="fp")
        prop = LLMProposal(id="prop1", anchor_case_id="case1", action_sequence="act", risk_level=1, action_payload_hash="pay")
        app = HumanApproval(id="app1", llm_proposal_id="prop1", approved_at=self.now)
        exec_ev = ExecutionEvent(id="exec1", human_approval_id="app1", executed_at=self.now)
        out = OutcomeEvidence(id="out1", execution_event_id="exec1", success=True, post_execution_state="done")
        pol = ReplayPolicy(id="pol1", anchor_case_id="case1", expires_at=self.now + timedelta(days=1), replay_allowed=True, max_auto_replay_risk_level=2)

        record = AnchorRecord(
            anchor_case=case,
            ui_snapshot=snap,
            llm_proposal=prop,
            human_approval=app,
            execution_event=exec_ev,
            outcome_evidence=out,
            replay_policy=pol
        )

        self.repo.save_anchor_record(record)

        saved_record = self.repo.get_anchor_record("case1")
        self.assertIsNotNone(saved_record)
        self.assertEqual(saved_record.anchor_case, case)
        self.assertEqual(saved_record.ui_snapshot, snap)
        self.assertEqual(saved_record.llm_proposal, prop)
        self.assertEqual(saved_record.human_approval, app)
        self.assertEqual(saved_record.execution_event, exec_ev)
        self.assertEqual(saved_record.outcome_evidence, out)
        self.assertEqual(saved_record.replay_policy, pol)

        # Verify individual components are stored
        self.assertEqual(self.repo.get_ui_snapshot("snap1"), snap)
        self.assertEqual(self.repo.get_outcome_evidence("out1"), out)

    def test_anchor_record_storage_partial(self):
        case = AnchorCase(id="case2", user_intent="intent", created_at=self.now, business_object_id="obj2")
        snap = UISnapshot(id="snap2", anchor_case_id="case2", ax_tree_json="{}", image_hash="img", ui_fingerprint_hash="fp")

        record = AnchorRecord(
            anchor_case=case,
            ui_snapshot=snap,
            llm_proposal=None,
            human_approval=None,
            execution_event=None,
            outcome_evidence=None,
            replay_policy=None
        )

        self.repo.save_anchor_record(record)

        saved_record = self.repo.get_anchor_record("case2")
        self.assertIsNotNone(saved_record)
        self.assertEqual(saved_record.anchor_case, case)
        self.assertEqual(saved_record.ui_snapshot, snap)
        self.assertIsNone(saved_record.llm_proposal)
        self.assertIsNone(saved_record.outcome_evidence)

        # Verify list works
        cases = self.repo.list_anchor_cases()
        self.assertIn(case, cases)

    def test_anchor_record_missing_case(self):
        self.assertIsNone(self.repo.get_anchor_record("missing_case"))

if __name__ == '__main__':
    unittest.main()
