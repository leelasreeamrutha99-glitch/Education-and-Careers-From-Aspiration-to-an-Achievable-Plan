import unittest

from main import assess_evidence


class TestAuditAssessment(unittest.TestCase):
    def test_present_export_is_incomplete(self):
        result = assess_evidence({"case_id": "CASE-1", "checks": [
            {"system": "database", "status": "deleted"},
            {"system": "export", "status": "present"},
        ]})
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("export: present", result["findings"])

    def test_all_deleted_is_complete_for_listed_checks(self):
        result = assess_evidence({"checks": [
            {"system": "database", "status": "deleted"}
        ]})
        self.assertEqual(result["status"], "COMPLETE")

    def test_empty_evidence_needs_review(self):
        self.assertEqual(assess_evidence({"checks": []})["status"], "NEEDS_REVIEW")

    def test_unknown_status_needs_review(self):
        result = assess_evidence({"checks": [
            {"system": "cache", "status": "maybe"}
        ]})
        self.assertEqual(result["status"], "NEEDS_REVIEW")


if __name__ == "__main__":
    unittest.main()
