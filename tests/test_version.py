import unittest
import causa_core


class TestVersionAndExports(unittest.TestCase):
    def test_version(self):
        self.assertEqual(causa_core.__version__, "1.0.0-alpha.0")

    def test_public_imports(self):
        # Ensure all required classes and functions can be imported from the root package
        self.assertTrue(hasattr(causa_core, "AnchorCase"))
        self.assertTrue(hasattr(causa_core, "UISnapshot"))
        self.assertTrue(hasattr(causa_core, "LLMProposal"))
        self.assertTrue(hasattr(causa_core, "HumanApproval"))
        self.assertTrue(hasattr(causa_core, "ExecutionEvent"))
        self.assertTrue(hasattr(causa_core, "OutcomeEvidence"))
        self.assertTrue(hasattr(causa_core, "ReplayPolicy"))
        self.assertTrue(hasattr(causa_core, "ReplayDecision"))
        self.assertTrue(hasattr(causa_core, "AnchorRecord"))
        self.assertTrue(hasattr(causa_core, "AuditSummary"))
        self.assertTrue(hasattr(causa_core, "determine_replay_decision"))
        self.assertTrue(hasattr(causa_core, "determine_replay_decision_from_record"))
        self.assertTrue(hasattr(causa_core, "build_audit_summary"))
        self.assertTrue(hasattr(causa_core, "CausaRepository"))
        self.assertTrue(hasattr(causa_core, "InMemoryCausaRepository"))

if __name__ == '__main__':
    unittest.main()
