import unittest
from datetime import datetime

from causa_core.models import (
    AnchorCase,
    UISnapshot,
    LLMProposal,
    HumanApproval,
    ExecutionEvent,
    OutcomeEvidence,
    ReplayPolicy,
    AnchorRecord,
    ReplayDecision,
)
from causa_core.audit import build_audit_summary


class TestAuditSummary(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2024, 1, 1, 12, 0, 0)
        self.anchor_case = AnchorCase(id="case1", user_intent="do thing", created_at=self.now, business_object_id="obj1")
        self.proposal = LLMProposal(id="prop1", anchor_case_id="case1", action_sequence="act", risk_level=2, action_payload_hash="pay")
        self.policy = ReplayPolicy(id="pol1", anchor_case_id="case1", expires_at=self.now, replay_allowed=True, max_auto_replay_risk_level=3)
        self.approval = HumanApproval(id="app1", llm_proposal_id="prop1", approved_at=self.now)
        self.execution = ExecutionEvent(id="exec1", human_approval_id="app1", executed_at=self.now)
        self.outcome = OutcomeEvidence(id="out1", execution_event_id="exec1", success=True, post_execution_state="ok")

        self.record = AnchorRecord(
            anchor_case=self.anchor_case,
            ui_snapshot=None,
            llm_proposal=self.proposal,
            human_approval=self.approval,
            execution_event=self.execution,
            outcome_evidence=self.outcome,
            replay_policy=self.policy
        )

    def test_summary_replay_candidate(self):
        decision = ReplayDecision(
            status="replay_candidate",
            reason_code="REPLAY_ELIGIBLE",
            message="All checks passed. Replay is eligible.",
            anchor_case_id="case1"
        )
        audit = build_audit_summary(decision, self.record)
        self.assertEqual(audit.status, "replay_candidate")
        self.assertEqual(audit.reason_code, "REPLAY_ELIGIBLE")
        self.assertEqual(audit.summary, "Replay is eligible for this AnchorCase.")
        self.assertIn("Decision Message: All checks passed. Replay is eligible.", audit.details)
        self.assertIn("Anchor Case ID: case1", audit.details)
        self.assertIn("User Intent: do thing", audit.details)
        self.assertIn("Historical Risk Level: 2", audit.details)
        self.assertIn("Human Approval Exists: Yes", audit.details)

    def test_summary_requires_human_anchor(self):
        decision = ReplayDecision(
            status="requires_human_anchor",
            reason_code="RISK_ABOVE_POLICY_THRESHOLD",
            message="Risk level exceeds the policy threshold.",
            anchor_case_id="case1"
        )
        audit = build_audit_summary(decision, self.record)
        self.assertEqual(audit.summary, "Human re-approval is required before replay.")

    def test_summary_requires_llm_reasoning(self):
        decision = ReplayDecision(
            status="requires_llm_reasoning",
            reason_code="UI_FINGERPRINT_MISMATCH",
            message="Current UI fingerprint does not exactly match the historical UI.",
            anchor_case_id="case1"
        )
        audit = build_audit_summary(decision, self.record)
        self.assertEqual(audit.summary, "LLM reasoning is required because the current context differs from the historical precedent.")

    def test_summary_do_not_replay(self):
        decision = ReplayDecision(
            status="do_not_replay",
            reason_code="FAILED_PRIOR_OUTCOME",
            message="The historical execution failed.",
            anchor_case_id="case1"
        )
        audit = build_audit_summary(decision, self.record)
        self.assertEqual(audit.summary, "Replay is not allowed for this historical case.")

    def test_summary_none_historical_record(self):
        decision = ReplayDecision(
            status="do_not_replay",
            reason_code="MISSING_ANCHOR_RECORD",
            message="No historical AnchorRecord was found.",
            anchor_case_id=None
        )
        audit = build_audit_summary(decision, None)
        self.assertEqual(audit.summary, "Replay is not allowed for this historical case.")
        self.assertIn("Decision Message: No historical AnchorRecord was found.", audit.details)
        self.assertNotIn("Anchor Case ID", [d for d in audit.details if d.startswith("Anchor Case ID")])
        self.assertNotIn("User Intent", "".join(audit.details))

if __name__ == '__main__':
    unittest.main()
