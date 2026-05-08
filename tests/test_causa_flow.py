import unittest

from causa_core.storage.memory import InMemoryCausaRepository
from causa_core.decision import determine_replay_decision_from_record
from causa_core.audit import build_audit_summary
from tests.fixtures import (
    FIXED_NOW,
    build_successful_anchor_record,
    build_failed_anchor_record,
    build_risk3_anchor_record,
    build_expired_policy_anchor_record,
)


class TestCausaFlow(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryCausaRepository()

    def test_successful_replay_candidate_flow(self):
        record = build_successful_anchor_record()
        self.repo.save_anchor_record(record)

        retrieved_record = self.repo.get_anchor_record(record.anchor_case.id)

        decision = determine_replay_decision_from_record(
            current_ui_snapshot=record.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="pay123",
            historical_record=retrieved_record,
            current_time=FIXED_NOW,
        )

        audit = build_audit_summary(decision, retrieved_record)

        self.assertEqual(decision.status, "replay_candidate")
        self.assertEqual(decision.reason_code, "REPLAY_ELIGIBLE")
        self.assertEqual(audit.status, "replay_candidate")
        self.assertEqual(audit.reason_code, "REPLAY_ELIGIBLE")

    def test_failed_prior_outcome_flow(self):
        record = build_failed_anchor_record()
        self.repo.save_anchor_record(record)

        retrieved_record = self.repo.get_anchor_record(record.anchor_case.id)

        decision = determine_replay_decision_from_record(
            current_ui_snapshot=record.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="pay123",
            historical_record=retrieved_record,
            current_time=FIXED_NOW,
        )

        audit = build_audit_summary(decision, retrieved_record)

        self.assertEqual(decision.status, "do_not_replay")
        self.assertEqual(decision.reason_code, "FAILED_PRIOR_OUTCOME")
        self.assertEqual(audit.status, "do_not_replay")
        self.assertEqual(audit.reason_code, "FAILED_PRIOR_OUTCOME")

    def test_risk3_flow(self):
        record = build_risk3_anchor_record()
        self.repo.save_anchor_record(record)

        retrieved_record = self.repo.get_anchor_record(record.anchor_case.id)

        decision = determine_replay_decision_from_record(
            current_ui_snapshot=record.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="pay123",
            historical_record=retrieved_record,
            current_time=FIXED_NOW,
        )

        audit = build_audit_summary(decision, retrieved_record)

        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "RISK_REQUIRES_HUMAN_ANCHOR")
        self.assertEqual(audit.status, "requires_human_anchor")
        self.assertEqual(audit.reason_code, "RISK_REQUIRES_HUMAN_ANCHOR")

    def test_expired_policy_flow(self):
        record = build_expired_policy_anchor_record()
        self.repo.save_anchor_record(record)

        retrieved_record = self.repo.get_anchor_record(record.anchor_case.id)

        decision = determine_replay_decision_from_record(
            current_ui_snapshot=record.ui_snapshot,
            current_risk_level=1,
            current_business_object_id="obj1",
            current_action_payload_hash="pay123",
            historical_record=retrieved_record,
            current_time=FIXED_NOW,
        )

        audit = build_audit_summary(decision, retrieved_record)

        self.assertEqual(decision.status, "requires_human_anchor")
        self.assertEqual(decision.reason_code, "EXPIRED_REPLAY_POLICY")
        self.assertEqual(audit.status, "requires_human_anchor")
        self.assertEqual(audit.reason_code, "EXPIRED_REPLAY_POLICY")


if __name__ == '__main__':
    unittest.main()
