"""The project's single new AWS tool: retrieve and assess one S3 audit-evidence object."""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime
from typing import Any
import boto3
from botocore.exceptions import BotoCoreError, ClientError

try:
    from strands import tool
except ImportError:  # lets offline unit tests run without installing the agent SDK
    def tool(func):
        """No-op decorator used only when Strands is absent in a test environment."""
        return func

MAX_EVIDENCE_BYTES = 1_048_576
ALLOWED_STATUSES = {"DELETED", "PRESENT", "PENDING", "UNKNOWN"}
ALLOWED_SYSTEMS = {"primary_database", "search_index", "object_storage", "customer_exports"}

class EvidenceValidationError(ValueError):
    """Raised when an evidence record cannot safely support an audit assessment."""

def _parse_utc(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceValidationError(f"{field_name} must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceValidationError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvidenceValidationError(f"{field_name} must include a timezone")
    return parsed

def validate_evidence(evidence: Any) -> dict[str, Any]:
    """Validate and normalize the versioned evidence contract before reasoning over it."""
    if not isinstance(evidence, dict):
        raise EvidenceValidationError("Evidence must be a JSON object")
    if evidence.get("schema_version") != "1.0":
        raise EvidenceValidationError("schema_version must be '1.0'")
    case_id = evidence.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 100:
        raise EvidenceValidationError("case_id must be a non-empty string up to 100 characters")
    subject_ref = evidence.get("subject_ref")
    if not isinstance(subject_ref, str) or not subject_ref.strip() or len(subject_ref) > 160:
        raise EvidenceValidationError("subject_ref must be a non-empty reference string up to 160 characters")
    _parse_utc(evidence.get("requested_at"), "requested_at")
    required = evidence.get("required_systems")
    if not isinstance(required, list) or not required:
        raise EvidenceValidationError("required_systems must be a non-empty list")
    if any(not isinstance(s, str) or s not in ALLOWED_SYSTEMS for s in required):
        raise EvidenceValidationError(f"required_systems may contain only: {', '.join(sorted(ALLOWED_SYSTEMS))}")
    if len(set(required)) != len(required):
        raise EvidenceValidationError("required_systems contains duplicates")
    checks = evidence.get("checks")
    if not isinstance(checks, list):
        raise EvidenceValidationError("checks must be a list")
    normalized_checks = []
    seen = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise EvidenceValidationError(f"checks[{index}] must be an object")
        system = check.get("system")
        status = check.get("status")
        if not isinstance(system, str) or system not in ALLOWED_SYSTEMS:
            raise EvidenceValidationError(f"checks[{index}].system is not an allowed system")
        if system in seen:
            raise EvidenceValidationError(f"Duplicate check for system: {system}")
        seen.add(system)
        if not isinstance(status, str) or status.upper() not in ALLOWED_STATUSES:
            raise EvidenceValidationError(f"checks[{index}].status must be one of {', '.join(sorted(ALLOWED_STATUSES))}")
        checked_at = _parse_utc(check.get("checked_at"), f"checks[{index}].checked_at")
        evidence_ref = check.get("evidence_ref", "")
        if not isinstance(evidence_ref, str) or len(evidence_ref) > 500:
            raise EvidenceValidationError(f"checks[{index}].evidence_ref must be a string up to 500 characters")
        normalized_checks.append({
            "system": system, "status": status.upper(),
            "checked_at": checked_at.isoformat(), "evidence_ref": evidence_ref,
        })
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "subject_ref": subject_ref,
        "requested_at": _parse_utc(evidence["requested_at"], "requested_at").isoformat(),
        "required_systems": list(required),
        "checks": normalized_checks,
    }

def assess_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Produce a deterministic assessment; unknown or missing evidence never becomes COMPLETE."""
    record = validate_evidence(evidence)
    by_system = {check["system"]: check for check in record["checks"]}
    required = record["required_systems"]
    missing = [system for system in required if system not in by_system]
    present = [s for s in required if s in by_system and by_system[s]["status"] == "PRESENT"]
    pending = [s for s in required if s in by_system and by_system[s]["status"] == "PENDING"]
    unknown = [s for s in required if s in by_system and by_system[s]["status"] == "UNKNOWN"]
    if present:
        status = "INCOMPLETE"
        findings = [f"Evidence reports data still present in: {', '.join(present)}."]
    elif pending:
        status = "IN_PROGRESS"
        findings = [f"Deletion is still pending in: {', '.join(pending)}."]
    elif missing or unknown:
        status = "NEEDS_REVIEW"
        findings = []
        if missing:
            findings.append(f"Missing required system checks: {', '.join(missing)}.")
        if unknown:
            findings.append(f"Unknown state reported for: {', '.join(unknown)}.")
    else:
        status = "COMPLETE"
        findings = ["All declared required systems report DELETED."]
    next_steps = {
        "INCOMPLETE": "Investigate present-data locations, remediate using the owning system's approved process, then re-run verification.",
        "IN_PROGRESS": "Wait for the pending deletion workflow to complete, then collect fresh evidence.",
        "NEEDS_REVIEW": "Collect valid, current evidence for every required system and resolve unknown states.",
        "COMPLETE": "Retain this evidence and review coverage limits; independently confirm backups and downstream processors if in scope.",
    }
    return {
        "case_id": record["case_id"], "status": status,
        "required_systems": required, "checks_received": len(record["checks"]),
        "missing_required_systems": missing, "findings": findings,
        "recommended_next_step": next_steps[status],
        "scope_warning": "Assessment applies only to the required systems and evidence supplied; it does not prove erasure from unreported backups, replicas, or downstream processors.",
    }

def fetch_and_assess_s3_evidence(*, s3_client=None, env: dict[str, str] | None = None) -> dict[str, Any]:
    """Read one configured S3 object, validate it, and return an integrity summary.

    The bucket and key are deployment configuration, not model-supplied parameters.
    """
    settings = os.environ if env is None else env
    bucket = settings.get("AUDIT_S3_BUCKET", "").strip()
    key = settings.get("AUDIT_S3_KEY", "deletion-evidence/sample_evidence.json").strip()
    region = settings.get("AWS_REGION", "").strip() or None
    if not bucket:
        raise RuntimeError("Set AUDIT_S3_BUCKET to the private bucket containing the audit evidence JSON.")
    if not key:
        raise RuntimeError("AUDIT_S3_KEY must identify one configured JSON evidence object.")
    client = s3_client or (boto3.client("s3", region_name=region) if region else boto3.client("s3"))
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        declared_length = response.get("ContentLength")
        if isinstance(declared_length, int) and declared_length > MAX_EVIDENCE_BYTES:
            response["Body"].close()
            raise EvidenceValidationError(f"Evidence object exceeds the {MAX_EVIDENCE_BYTES}-byte safety limit")
        body_stream = response["Body"]
        raw = body_stream.read(MAX_EVIDENCE_BYTES + 1)
        body_stream.close()
    except EvidenceValidationError:
        raise
    except (ClientError, BotoCoreError, OSError) as exc:
        raise RuntimeError(f"S3 evidence retrieval failed ({type(exc).__name__}); check bucket/key, region, credentials, and s3:GetObject access.") from exc
    if len(raw) > MAX_EVIDENCE_BYTES:
        raise EvidenceValidationError(f"Evidence object exceeds the {MAX_EVIDENCE_BYTES}-byte safety limit")
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceValidationError("S3 evidence object must contain valid UTF-8 JSON") from exc
    record = validate_evidence(parsed)
    return {
        "source": {
            "service": "Amazon S3", "bucket": bucket, "key": key,
            "version_id": response.get("VersionId"), "etag": response.get("ETag"),
            "last_modified": response.get("LastModified").isoformat() if response.get("LastModified") else None,
            "bytes_read": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "integrity_note": "SHA-256 fingerprints the exact bytes read; it does not establish who authored the object or independently prove that deletion occurred.",
        },
        "evidence": record, "assessment": assess_evidence(record),
    }

@tool
def read_s3_deletion_evidence() -> str:
    """Read and assess the single configured deletion-evidence JSON object from Amazon S3.

    Retrieves only AUDIT_S3_BUCKET/AUDIT_S3_KEY using GetObject. It validates the
    required-system evidence contract, calculates SHA-256 for the exact returned
    bytes, and reports S3 version/ETag metadata when available. It cannot delete,
    modify, list, or enumerate objects. Requires s3:GetObject on the configured object.
    """
    return json.dumps(fetch_and_assess_s3_evidence(), indent=2, sort_keys=True)
