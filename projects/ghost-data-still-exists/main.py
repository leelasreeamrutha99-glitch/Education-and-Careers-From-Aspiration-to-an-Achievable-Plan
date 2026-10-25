"""Local synthetic demo for deletion-audit evidence assessment."""
import argparse
import json
from pathlib import Path


def assess_evidence(evidence: dict) -> dict:
    """Assess listed checks only; this is not proof of total erasure."""
    checks = evidence.get("checks")
    if not isinstance(checks, list) or not checks:
        return {
            "case_id": evidence.get("case_id", "unknown"),
            "status": "NEEDS_REVIEW",
            "findings": ["No usable evidence checks were provided."],
            "scope_note": "Assessment covers only the evidence supplied."
        }

    findings = []
    known_statuses = {"deleted", "present", "pending"}
    for check in checks:
        if not isinstance(check, dict):
            return {
                "case_id": evidence.get("case_id", "unknown"),
                "status": "NEEDS_REVIEW",
                "findings": ["An evidence check is malformed."],
                "scope_note": "Assessment covers only the evidence supplied."
            }
        system = str(check.get("system", "unknown"))
        status = str(check.get("status", "unknown")).lower()
        if status not in known_statuses:
            return {
                "case_id": evidence.get("case_id", "unknown"),
                "status": "NEEDS_REVIEW",
                "findings": [f"Unrecognized status for system '{system}': {status}"],
                "scope_note": "Assessment covers only the evidence supplied."
            }
        if status in {"present", "pending"}:
            findings.append(f"{system}: {status}")

    status = "INCOMPLETE" if findings else "COMPLETE"
    if not findings:
        findings = ["All listed evidence checks report deleted."]

    return {
        "case_id": evidence.get("case_id", "unknown"),
        "status": status,
        "findings": findings,
        "recommended_action": (
            "Investigate the remaining or pending items, remediate them, and verify again."
            if status == "INCOMPLETE"
            else "Review the evidence scope and verify systems not represented in these checks."
        ),
        "scope_note": (
            "Assessment covers only the evidence supplied; it does not prove every copy or backup is erased."
        )
    }


def load_local_evidence() -> dict:
    path = Path(__file__).parent / "data" / "sample_evidence.json"
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def main():
    parser = argparse.ArgumentParser(description="Deletion audit evidence demo")
    parser.add_argument("--demo", action="store_true", help="Run the local synthetic example")
    args = parser.parse_args()
    result = assess_evidence(load_local_evidence())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"COMPLETE", "INCOMPLETE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
