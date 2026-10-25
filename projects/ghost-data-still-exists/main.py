"""Offline demonstration of the deletion-evidence assessment rules."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from s3_tool import assess_evidence

def main() -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic audit against synthetic evidence.")
    parser.add_argument("--evidence", type=Path, default=Path(__file__).parent / "data" / "sample_evidence.json")
    args = parser.parse_args()
    try:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = assess_evidence(evidence)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "NEEDS_REVIEW", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
