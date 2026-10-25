"""Offline demo for OpportunityLens; it does not contact AWS."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from catalog_tool import search_catalog

def main() -> int:
    parser = argparse.ArgumentParser(description="Search the local learning-resource catalog.")
    parser.add_argument("--skill", default="data science", help="Skill or topic")
    parser.add_argument("--budget", choices=("any", "free"), default="free")
    parser.add_argument("--format", dest="learning_format", choices=("any", "documentation", "interactive", "course", "video", "lab"), default="any")
    parser.add_argument("--max-results", type=int, default=5)
    args = parser.parse_args()
    path = Path(__file__).parent / "data" / "learning_resources.json"
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
        result = search_catalog(catalog, skill_query=args.skill, budget_preference=args.budget,
                                format_preference=args.learning_format, max_results=args.max_results)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
