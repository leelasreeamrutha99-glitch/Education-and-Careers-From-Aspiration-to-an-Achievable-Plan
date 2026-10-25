from __future__ import annotations
import hashlib
import io
import json
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock
from catalog_tool import CatalogValidationError, MAX_CATALOG_BYTES, load_catalog_from_s3, search_catalog, validate_catalog

class FakeBody(io.BytesIO):
    def close(self):
        self.was_closed = True
        super().close()

class TestCatalogSearch(unittest.TestCase):
    def setUp(self):
        with open("data/learning_resources.json", encoding="utf-8") as handle:
            self.catalog = json.load(handle)

    def test_python_search_returns_https_official_reference(self):
        result = search_catalog(self.catalog, skill_query="Python", budget_preference="free")
        self.assertGreater(result["result_count"], 0)
        self.assertTrue(all(item["official_url"].startswith("https://") for item in result["results"]))
        self.assertIn("python-tutorial", [item["id"] for item in result["results"]])

    def test_data_science_query_matches_pandas_and_python(self):
        result = search_catalog(self.catalog, skill_query="data science", today=date(2026, 10, 25))
        ids = {item["id"] for item in result["results"]}
        self.assertIn("pandas-getting-started", ids)
        self.assertIn("python-tutorial", ids)

    def test_format_filter(self):
        self.assertEqual(search_catalog(self.catalog, skill_query="python", format_preference="video")["result_count"], 0)

    def test_charge_caveat_does_not_match_free_only_filter(self):
        self.assertEqual(search_catalog(self.catalog, skill_query="aws", budget_preference="free")["result_count"], 0)

    def test_unknown_resource_not_invented(self):
        result = search_catalog(self.catalog, skill_query="quantum underwater basket weaving")
        self.assertEqual(result["results"], [])
        self.assertIn("No matching resource", result["message"])

    def test_max_results_bounded(self):
        self.assertEqual(len(search_catalog(self.catalog, skill_query="python", max_results=1)["results"]), 1)

    def test_review_due_is_reported(self):
        result = search_catalog(self.catalog, skill_query="python", today=date(2027, 6, 1))
        self.assertTrue(any(item["review_status"] == "REVIEW_DUE" for item in result["results"]))

    def test_reject_non_https_url(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["resources"][0]["official_url"] = "http://example.com"
        with self.assertRaisesRegex(CatalogValidationError, "HTTPS"):
            validate_catalog(bad)

    def test_reject_duplicate_ids(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["resources"].append(dict(bad["resources"][0]))
        with self.assertRaisesRegex(CatalogValidationError, "Duplicate resource ID"):
            validate_catalog(bad)

    def test_punctuation_only_query_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "searchable character"):
            search_catalog(self.catalog, skill_query="!!!")

    def test_reject_unapproved_host(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["resources"][0]["official_url"] = "https://attacker.example/learn"
        bad["resources"][0]["approved_host"] = "attacker.example"
        with self.assertRaisesRegex(CatalogValidationError, "approved host"):
            validate_catalog(bad)

    def test_reject_future_review_date(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["resources"][0]["reviewed_on"] = "2099-01-01"
        with self.assertRaisesRegex(CatalogValidationError, "future"):
            validate_catalog(bad)

    def test_reject_future_catalog_date(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["catalog_updated_on"] = "2099-01-01"
        with self.assertRaisesRegex(CatalogValidationError, "future"):
            validate_catalog(bad)

    def test_reject_wrong_version(self):
        bad = json.loads(json.dumps(self.catalog))
        bad["schema_version"] = "3.0"
        with self.assertRaisesRegex(CatalogValidationError, "schema_version"):
            validate_catalog(bad)

    def test_query_validation(self):
        with self.assertRaises(ValueError):
            search_catalog(self.catalog, skill_query=" ")
        with self.assertRaises(ValueError):
            search_catalog(self.catalog, skill_query="python", max_results=1000)
        with self.assertRaises(ValueError):
            search_catalog(self.catalog, skill_query="python", budget_preference="cheap")

class TestS3Retrieval(unittest.TestCase):
    def setUp(self):
        with open("data/learning_resources.json", encoding="utf-8") as handle:
            self.raw = handle.read().encode()

    def test_mocked_s3_read_has_hash_and_version(self):
        body = FakeBody(self.raw)
        client = Mock()
        client.get_object.return_value = {"Body": body, "ContentLength": len(self.raw),
            "VersionId": "version-demo-1", "ETag": '"etag-demo"',
            "LastModified": datetime(2026, 10, 25, tzinfo=timezone.utc)}
        result = load_catalog_from_s3(s3_client=client, env={
            "LEARNING_CATALOG_BUCKET": "private-catalog-demo",
            "LEARNING_CATALOG_KEY": "catalog/learning_resources.json", "AWS_REGION": "ap-south-1"})
        client.get_object.assert_called_once_with(Bucket="private-catalog-demo", Key="catalog/learning_resources.json")
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(result["source"]["version_id"], "version-demo-1")
        self.assertTrue(body.was_closed)

    def test_expected_owner_passed_when_configured(self):
        body = FakeBody(self.raw)
        client = Mock()
        client.get_object.return_value = {"Body": body, "ContentLength": len(self.raw)}
        load_catalog_from_s3(s3_client=client, env={
            "LEARNING_CATALOG_BUCKET": "catalog", "LEARNING_CATALOG_EXPECTED_BUCKET_OWNER": "123456789012"})
        client.get_object.assert_called_once_with(Bucket="catalog", Key="catalog/learning_resources.json",
            ExpectedBucketOwner="123456789012")

    def test_missing_bucket_fails_before_call(self):
        client = Mock()
        with self.assertRaisesRegex(RuntimeError, "LEARNING_CATALOG_BUCKET"):
            load_catalog_from_s3(s3_client=client, env={})
        client.get_object.assert_not_called()

    def test_oversize_rejected_and_body_closed(self):
        body = FakeBody(b"x")
        client = Mock()
        client.get_object.return_value = {"Body": body, "ContentLength": MAX_CATALOG_BYTES + 1}
        with self.assertRaisesRegex(CatalogValidationError, "size limit"):
            load_catalog_from_s3(s3_client=client, env={"LEARNING_CATALOG_BUCKET": "catalog"})
        self.assertTrue(body.was_closed)

    def test_invalid_json_rejected(self):
        client = Mock()
        client.get_object.return_value = {"Body": FakeBody(b"not-json"), "ContentLength": 8}
        with self.assertRaisesRegex(CatalogValidationError, "valid UTF-8 JSON"):
            load_catalog_from_s3(s3_client=client, env={"LEARNING_CATALOG_BUCKET": "catalog"})

if __name__ == "__main__":
    unittest.main()
