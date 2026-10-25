# Ghost Data Still Exists 👻

**AWS Builder Center Weekend Challenge: Give Your Agent a Tool**

This project demonstrates the addition of one focused tool to a deletion-audit agent: a **read-only Amazon S3 evidence reader**. The Strands Agents integration can call this tool to retrieve a synthetic audit record, inspect reported system states, and explain whether the *available evidence* suggests remaining data.

> **Important implementation note:** This branch is a self-contained demonstration addition, not a copy of the user's earlier local agent source (that source was not available in the connected repositories). The local rule-based demo uses synthetic data. The Strands/Bedrock path performs a real S3 read only after you configure AWS credentials, a bucket, and an object. No real S3 bucket was queried while preparing these files. Do not claim the live AWS path was tested until you run it successfully in your own AWS account.

## The new capability

- **Before:** the local example assesses evidence already supplied as a JSON file.
- **After:** the Strands agent has a `read_s3_evidence` tool that reads a JSON object from the configured S3 bucket and can reason over that retrieved evidence.

The example data reports a customer export that is still present, so the expected result is `INCOMPLETE`.

## Quick start: local synthetic demo

Python 3.10+ is recommended.

```bash
cd projects/ghost-data-still-exists
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python main.py --demo
python -m unittest discover -s tests -v
```

The local demo does not contact AWS and does not require credentials.

## Configure a real S3 read

1. In your AWS account, create an S3 bucket.
2. Upload `data/sample_evidence.json` to it (use synthetic data only).
3. Set the following environment variables:
   - `AWS_REGION` — the bucket's region, for example `ap-south-1`
   - `AUDIT_S3_BUCKET` — your bucket name
   - `AUDIT_S3_KEY` — object key, for example `sample_evidence.json`
4. Configure AWS credentials using an IAM role or AWS CLI profile. Do not put access keys in source code or commit them.
5. Grant the identity only `s3:GetObject` access to the target evidence object.
6. Ensure your account has access to an Amazon Bedrock model in your selected region, because Strands uses Bedrock for agent inference.
7. Run `python agent.py` and watch the tool invocation. The tool reads; it does not delete or modify objects.

The Strands agent is intentionally limited to the configured object; the model does not get to choose arbitrary bucket names or keys.

## Evidence format

```json
{
  "case_id": "CASE-1042",
  "subject_ref": "customer-demo-1042",
  "checks": [
    {"system": "primary_database", "status": "deleted"},
    {"system": "search_index", "status": "deleted"},
    {"system": "customer_export", "status": "present"}
  ]
}
```

Use synthetic IDs and records in all public demonstrations.

## Status rules in the local example

- `INCOMPLETE`: any listed check reports `present` or `pending`.
- `COMPLETE`: every listed check reports `deleted`.
- `NEEDS_REVIEW`: evidence is empty, malformed, or includes an unrecognized status.

These are findings about the evidence that was retrieved; they are not proof that every copy, backup, replica, or downstream processor has been checked.

## Repository contents

- `main.py` — local deterministic demonstration and assessment rules.
- `s3_tool.py` — read-only S3 evidence retrieval.
- `agent.py` — Strands Agents integration that can call the S3 tool.
- `data/sample_evidence.json` — synthetic audit record.
- `tests/test_audit.py` — offline unit tests.
- `requirements.txt` — Python dependencies.

## Demo video outline (under 3 minutes)

1. **Before (20 seconds):** show the local demo reading a supplied JSON file.
2. **Tool (30 seconds):** show `s3_tool.py` and explain least-privilege `s3:GetObject`.
3. **After (45 seconds):** run `agent.py` in your configured AWS environment and show the agent invoking the tool to retrieve evidence.
4. **Finding (30 seconds):** highlight the export marked `present` and the resulting `INCOMPLETE` assessment.
5. **Limits (15 seconds):** state that results only reflect retrieved evidence.

If the real AWS path is not configured and tested, show the local synthetic demo and describe the intended S3 integration as a setup step—not as a completed live call. The challenge requires a public video shorter than 3 minutes in the Builder Center project's `demo` field.

## Security checklist

- Never commit AWS credentials, private audit logs, or real customer information.
- Use IAM roles or temporary credentials and least-privilege permissions.
- Keep the tool read-only.
- Explain evidence coverage and uncertainty rather than claiming guaranteed erasure.
