"""S3-backed verified-learning-catalog tool for CareerPath AI."""
from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import date
from typing import Any
from urllib.parse import urlparse
import boto3
from botocore.exceptions import BotoCoreError, ClientError

try:
    from strands import tool
except ImportError:
    def tool(func):
        """No-op decorator used only when Strands is absent during offline tests."""
        return func

MAX_CATALOG_BYTES = 2 * 1024 * 1024
MAX_RESOURCES = 300
MAX_QUERY_LENGTH = 160
VALID_FORMATS = {"documentation", "interactive", "course", "video", "lab", "any"}
VALID_LEVELS = {"beginner", "intermediate", "advanced", "all-levels"}
TRUSTED_HOSTS = {"docs.python.org", "www.postgresql.org", "pandas.pydata.org", "scikit-learn.org", "docs.aws.amazon.com"}
RESOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,79}$")


class CatalogValidationError(ValueError):
    """Raised when the catalog is malformed or unsafe to use."""


def _valid_date(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise CatalogValidationError(f"{field} must be an ISO-8601 date (YYYY-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CatalogValidationError(f"{field} must be an ISO-8601 date (YYYY-MM-DD)") from exc


def validate_catalog(payload: Any) -> dict[str, Any]:
    """Validate the catalog contract, HTTPS URLs, enumerated values, and unique IDs."""
    if not isinstance(payload, dict):
        raise CatalogValidationError("Catalog must be a JSON object")
    if payload.get("schema_version") != "1.0":
        raise CatalogValidationError("schema_version must be '1.0'")
    catalog_id = payload.get("catalog_id")
    if not isinstance(catalog_id, str) or not catalog_id.strip() or len(catalog_id) > 100:
        raise CatalogValidationError("catalog_id must be a non-empty string up to 100 characters")
    publisher = payload.get("publisher")
    if not isinstance(publisher, str) or not publisher.strip() or len(publisher) > 160:
        raise CatalogValidationError("publisher must be a non-empty string up to 160 characters")
    updated = _valid_date(payload.get("catalog_updated_on"), "catalog_updated_on")
    if updated > date.today():
        raise CatalogValidationError("catalog_updated_on cannot be in the future")
    resources = payload.get("resources")
    if not isinstance(resources, list) or not resources or len(resources) > MAX_RESOURCES:
        raise CatalogValidationError(f"resources must contain between 1 and {MAX_RESOURCES} entries")

    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(resources):
        prefix = f"resources[{index}]"
        if not isinstance(item, dict):
            raise CatalogValidationError(f"{prefix} must be an object")
        resource_id = item.get("id")
        if not isinstance(resource_id, str) or not RESOURCE_ID_RE.fullmatch(resource_id):
            raise CatalogValidationError(f"{prefix}.id must be lowercase letters, digits, and hyphens")
        if resource_id in seen_ids:
            raise CatalogValidationError(f"Duplicate resource ID: {resource_id}")
        seen_ids.add(resource_id)
        for name in ("title", "provider", "cost_label", "learning_outcome"):
            value = item.get(name)
            limit = 500 if name == "learning_outcome" else 180
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise CatalogValidationError(f"{prefix}.{name} must be a non-empty string up to {limit} characters")
        url = item.get("official_url")
        parsed_url = urlparse(url) if isinstance(url, str) else None
        if not parsed_url or parsed_url.scheme != "https" or not parsed_url.netloc:
            raise CatalogValidationError(f"{prefix}.official_url must be an absolute HTTPS URL")
        if parsed_url.username or parsed_url.password:
            raise CatalogValidationError(f"{prefix}.official_url must not contain embedded credentials")
        approved_host = item.get("approved_host")
        if not isinstance(approved_host, str) or approved_host not in TRUSTED_HOSTS or parsed_url.hostname != approved_host:
            raise CatalogValidationError(f"{prefix}.official_url host must exactly match an approved host: {', '.join(sorted(TRUSTED_HOSTS))}")
        level = item.get("level")
        if not isinstance(level, str) or level not in VALID_LEVELS:
            raise CatalogValidationError(f"{prefix}.level must be one of {', '.join(sorted(VALID_LEVELS))}")
        learning_format = item.get("format")
        if not isinstance(learning_format, str) or learning_format not in VALID_FORMATS - {"any"}:
            raise CatalogValidationError(f"{prefix}.format must be one of {', '.join(sorted(VALID_FORMATS - {'any'}))}")
        skills = item.get("skills")
        if (not isinstance(skills, list) or not skills or len(skills) > 30 or
                any(not isinstance(skill, str) or not skill.strip() or len(skill) > 60 for skill in skills)):
            raise CatalogValidationError(f"{prefix}.skills must be a list of 1–30 non-empty strings")
        if len({skill.strip().casefold() for skill in skills}) != len(skills):
            raise CatalogValidationError(f"{prefix}.skills contains duplicates")
        reviewed = _valid_date(item.get("reviewed_on"), f"{prefix}.reviewed_on")
        if reviewed > date.today():
            raise CatalogValidationError(f"{prefix}.reviewed_on cannot be in the future")
        normalized.append({
            "id": resource_id, "title": item["title"].strip(), "provider": item["provider"].strip(),
            "official_url": url, "approved_host": approved_host, "skills": [skill.strip() for skill in skills],
            "level": level, "format": learning_format, "cost_label": item["cost_label"].strip(),
            "learning_outcome": item["learning_outcome"].strip(), "reviewed_on": reviewed.isoformat(),
        })
    return {
        "schema_version": "1.0", "catalog_id": catalog_id, "publisher": publisher,
        "catalog_updated_on": updated.isoformat(), "resources": normalized,
    }


def search_catalog(catalog: Any, *, skill_query: str, budget_preference: str = "any",
                   format_preference: str = "any", max_results: int = 5,
                   today: date | None = None) -> dict[str, Any]:
    """Filter curated entries; never invent missing records or change catalog claims."""
    data = validate_catalog(catalog)
    if not isinstance(skill_query, str) or not skill_query.strip() or len(skill_query) > MAX_QUERY_LENGTH:
        raise ValueError(f"skill_query must be 1–{MAX_QUERY_LENGTH} characters")
    if not isinstance(budget_preference, str) or budget_preference.casefold() not in {"any", "free"}:
        raise ValueError("budget_preference must be 'any' or 'free'")
    if not isinstance(format_preference, str) or format_preference.casefold() not in VALID_FORMATS:
        raise ValueError(f"format_preference must be one of {', '.join(sorted(VALID_FORMATS))}")
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 10:
        raise ValueError("max_results must be an integer from 1 to 10")
    as_of = today or date.today()
    query_terms = [term for term in re.findall(r"[a-z0-9+#.]+", skill_query.casefold().strip()) if term]
    if not query_terms:
        raise ValueError("skill_query must contain at least one searchable character")
    ranked = []
    for resource in data["resources"]:
        skill_text = " ".join(resource["skills"]).casefold()
        title = resource["title"].casefold()
        haystack = f"{title} {skill_text} {resource['learning_outcome'].casefold()}"
        if not all(term in haystack for term in query_terms):
            continue
        if budget_preference.casefold() == "free":
            cost = resource["cost_label"].casefold()
            free_claim = any(token in cost for token in ("free", "no-cost", "open access"))
            caveat = any(token in cost for token in ("may incur charge", "usage may incur", "paid component", "subscription required"))
            if not free_claim or caveat:
                continue
        chosen_format = format_preference.casefold()
        if chosen_format != "any" and resource["format"] != chosen_format:
            continue
        item = dict(resource)
        age = (as_of - date.fromisoformat(resource["reviewed_on"])).days
        item["review_age_days"] = age
        item["review_status"] = "REVIEW_DUE" if age > 180 else "REVIEWED_WITHIN_180_DAYS"
        score = sum(3 if term in skill_text else 2 if term in title else 1 for term in query_terms)
        ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    results = [item for _, item in ranked[:max_results]]
    return {
        "catalog_id": data["catalog_id"], "catalog_updated_on": data["catalog_updated_on"],
        "query": skill_query.strip(), "budget_preference": budget_preference.casefold(),
        "format_preference": format_preference.casefold(), "result_count": len(results),
        "results": results,
        "message": ("Matches come only from the S3 catalog. Review-due entries should be rechecked before relying on them."
                    if results else "No matching resource was found in the catalog. Do not invent a substitute; expand or update the catalog."),
        "scope_note": "The tool filters catalog metadata. It does not live-check URLs, certify course quality, or guarantee current price/access terms.",
    }


def load_catalog_from_s3(*, s3_client=None, env: dict[str, str] | None = None) -> dict[str, Any]:
    """Fetch one deployment-configured catalog object using bounded, read-only access."""
    settings = os.environ if env is None else env
    bucket = settings.get("LEARNING_CATALOG_BUCKET", "").strip()
    key = settings.get("LEARNING_CATALOG_KEY", "catalog/learning_resources.json").strip()
    region = settings.get("AWS_REGION", "").strip() or None
    expected_owner = settings.get("LEARNING_CATALOG_EXPECTED_BUCKET_OWNER", "").strip()
    if not bucket:
        raise RuntimeError("Set LEARNING_CATALOG_BUCKET to a private S3 bucket containing the learning catalog.")
    if not key:
        raise RuntimeError("LEARNING_CATALOG_KEY must identify one JSON catalog object.")
    client = s3_client or (boto3.client("s3", region_name=region) if region else boto3.client("s3"))
    params = {"Bucket": bucket, "Key": key}
    if expected_owner:
        params["ExpectedBucketOwner"] = expected_owner
    try:
        response = client.get_object(**params)
        length = response.get("ContentLength")
        if isinstance(length, int) and length > MAX_CATALOG_BYTES:
            response["Body"].close()
            raise CatalogValidationError(f"Catalog exceeds the {MAX_CATALOG_BYTES}-byte size limit")
        stream = response["Body"]
        raw = stream.read(MAX_CATALOG_BYTES + 1)
        stream.close()
    except CatalogValidationError:
        raise
    except (ClientError, BotoCoreError, OSError) as exc:
        raise RuntimeError(f"S3 catalog retrieval failed ({type(exc).__name__}); check bucket/key, region, credentials, and s3:GetObject access.") from exc
    if len(raw) > MAX_CATALOG_BYTES:
        raise CatalogValidationError(f"Catalog exceeds the {MAX_CATALOG_BYTES}-byte size limit")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogValidationError("S3 catalog must be valid UTF-8 JSON") from exc
    return {
        "catalog": validate_catalog(payload),
        "source": {
            "service": "Amazon S3", "bucket": bucket, "key": key,
            "version_id": response.get("VersionId"), "etag": response.get("ETag"),
            "last_modified": response.get("LastModified").isoformat() if response.get("LastModified") else None,
            "bytes_read": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "integrity_note": "SHA-256 fingerprints the bytes retrieved; it does not prove catalog authorship or current URL availability.",
        },
    }


@tool
def search_verified_learning_resources(skill_query: str, budget_preference: str = "any",
                                       format_preference: str = "any", max_results: int = 5) -> str:
    """Search the curated learning-resource catalog stored in the configured S3 object.

    Use this tool before recommending named learning resources, official URLs, cost
    labels, levels, or formats. It returns catalog entries only; never invent missing
    entries. The S3 bucket/key are fixed by deployment environment, not supplied by
    the model. The tool is read-only and needs s3:GetObject on the configured object.

    Args:
        skill_query: Topic or skill, for example Python, SQL, data science, or machine learning.
        budget_preference: 'any' or 'free'. Ambiguous or charge-caveat entries do not match 'free'.
        format_preference: 'any', 'documentation', 'interactive', 'course', 'video', or 'lab'.
        max_results: Number of results from 1 to 10.
    """
    loaded = load_catalog_from_s3()
    filtered = search_catalog(loaded["catalog"], skill_query=skill_query,
                              budget_preference=budget_preference,
                              format_preference=format_preference, max_results=max_results)
    return json.dumps({"source": loaded["source"], **filtered}, indent=2, sort_keys=True)
