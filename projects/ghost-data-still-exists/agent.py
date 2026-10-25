"""Strands agent that can call the read-only S3 evidence tool."""
import os

from strands import Agent
from s3_tool import read_s3_evidence


SYSTEM_PROMPT = """
You are a careful deletion-audit assistant. When asked to audit the configured case,
call the read_s3_evidence tool to retrieve the audit record from Amazon S3.
Use only the retrieved evidence. Report case_id, each system and status, an overall
assessment, and a recommended next step. Classify as INCOMPLETE if any check is
present or pending; COMPLETE only if all listed checks say deleted; otherwise
NEEDS_REVIEW. Explain that these findings cover only the evidence provided and do
not prove deletion from every backup, replica, or downstream system. Never claim
that you deleted data; this tool is read-only. If the tool reports an error, explain
the configuration or permission issue without inventing evidence.
"""


def main():
    if not os.getenv("AUDIT_S3_BUCKET"):
        raise SystemExit("Set AUDIT_S3_BUCKET before running the live Strands agent.")
    agent = Agent(system_prompt=SYSTEM_PROMPT, tools=[read_s3_evidence])
    agent("Read the configured S3 audit evidence and provide a concise deletion audit.")


if __name__ == "__main__":
    main()
