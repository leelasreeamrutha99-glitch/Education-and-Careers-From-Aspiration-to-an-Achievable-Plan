"""Read-only Amazon S3 evidence retrieval tool."""
import json
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from strands import tool


@tool
def read_s3_evidence() -> str:
    """Fetch the configured JSON audit-evidence object from Amazon S3.

    Uses AWS_REGION, AUDIT_S3_BUCKET and AUDIT_S3_KEY environment variables.
    Authentication uses the AWS SDK credential chain (for example, an IAM role).
    This tool is read-only and never deletes or modifies S3 objects.
    """
    bucket = os.getenv("AUDIT_S3_BUCKET")
    key = os.getenv("AUDIT_S3_KEY", "sample_evidence.json")
    region = os.getenv("AWS_REGION")

    if not bucket:
        return "Configuration error: AUDIT_S3_BUCKET is not set."
    if not key:
        return "Configuration error: AUDIT_S3_KEY is empty."

    client = boto3.client("s3", region_name=region) if region else boto3.client("s3")
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
    except (ClientError, BotoCoreError) as exc:
        return (
            "S3 evidence read failed. Check the configured bucket/key, region, "
            "AWS credentials, network access, and least-privilege s3:GetObject permission. "
            f"Error type: {type(exc).__name__}."
        )

    try:
        evidence = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "Evidence object is not valid UTF-8 JSON."
    if not isinstance(evidence, dict):
        return "Evidence JSON must contain a single JSON object."
    return json.dumps(evidence, indent=2)
