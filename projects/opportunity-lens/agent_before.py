"""Text-only baseline for the existing CareerPath AI learning-resource flow."""
from __future__ import annotations
import os
import sys
from strands import Agent
from strands.models import BedrockModel

SYSTEM_PROMPT = """
You are CareerPath AI, a supportive career and learning navigator. Help the learner
identify skills and create achievable next steps. This baseline has no retrieval tool
for a curated resource catalog. Do not invent exact course URLs, prices, availability,
or certification claims. When named resources are requested, explain that this baseline
cannot look them up and recommend checking official sources. Do not promise employment.
""".strip()

def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or "I want to start data science. Suggest a learning plan and resources."
    region = os.getenv("AWS_REGION", "us-west-2")
    model_id = os.getenv("BEDROCK_MODEL_ID")
    model = BedrockModel(model_id=model_id, region_name=region, temperature=0.2) if model_id else BedrockModel(region_name=region, temperature=0.2)
    Agent(model=model, system_prompt=SYSTEM_PROMPT)(prompt)

if __name__ == "__main__":
    main()
