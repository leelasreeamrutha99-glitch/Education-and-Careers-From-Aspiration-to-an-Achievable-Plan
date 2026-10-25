# OpportunityLens — S3-Grounded CareerPath AI

AWS Builder Center Weekend Challenge: Give Your Agent a Tool

OpportunityLens extends the existing CareerPath AI learning-resource workflow with one new tool: a curated learning-resource catalog reader backed by Amazon S3. CareerPath AI can already help with career discovery, skill-gap analysis, and planning. The gap is making named learning resources and URLs traceable to maintained data instead of relying only on model memory.

Honest status: the source and offline tests are implemented in this branch. The live S3/Bedrock flow requires your AWS bucket, credentials, and Bedrock model access; it has not been run against your AWS account here. The sample catalog contains official documentation links and curator review dates. The tool does not make live HTTP requests, so review dates do not prove a URL or access terms remain unchanged.

## Before vs. after

- Before: CareerPath AI can explain a learning plan, but without a retrieval tool it should avoid inventing exact links, costs, formats, or availability.
- After: the agent calls search_verified_learning_resources. That single tool reads a bounded JSON catalog from one preconfigured S3 object, validates it, filters by skill, budget, and format, and returns matches with source URL, review date, S3 version/ETag when available, and SHA-256 fingerprint.

## Why this matters

Learners need actionable, inspectable resources—not plausible but fabricated course links. OpportunityLens makes source data explicit, marks old reviewed entries, returns no invented fallback when no catalog entry matches, and keeps catalog updates under human review.

## Architecture

CareerPath AI question -> Strands Agents + Amazon Bedrock -> search_verified_learning_resources -> private S3 JSON catalog -> size limit, schema and HTTPS validation, deterministic filtering -> source metadata and SHA-256 -> response with resource IDs and URLs.

## Files

- agent_before.py: text-only baseline harness representing resource recommendations before the new tool.
- agent.py: CareerPath AI using the S3-backed resource tool.
- catalog_tool.py: the one new tool plus validation and deterministic search.
- main.py: local no-AWS demo.
- data/learning_resources.json: sample catalog seed.
- tests/test_catalog_tool.py: unit and mocked-S3 tests.
- docs/iam-policy-example.json: least-privilege policy template.
- docs/CAREERPATH_INTEGRATION.md: how the tool plugs into the existing CareerPath AI resource-navigation stage.
- docs/DEMO_SCRIPT.md: a short challenge-video storyboard.

## Run locally without AWS calls

Requires Python 3.10 or later.

Windows PowerShell:
    python -m venv .venv
    .venv\Scripts\Activate.ps1

macOS/Linux:
    python -m venv .venv
    source .venv/bin/activate

Then run:
    python -m pip install -r requirements.txt
    python main.py --skill "data science" --budget free
    python main.py --skill "Python" --format documentation
    python main.py --skill "quantum underwater basket weaving"
    python -m unittest discover -s tests -v

The last query intentionally returns no matches instead of inventing resources. The tests mock S3 and need no AWS credentials.

## Configure S3 for a live tool call

1. Create a private S3 bucket and keep Block Public Access enabled.
2. Upload data/learning_resources.json to the key catalog/learning_resources.json.
3. Copy docs/iam-policy-example.json and replace the bucket placeholder. Give the demo identity only s3:GetObject on that exact object. Do not grant list, write, or delete permissions to this tool.
4. Configure AWS credentials using an IAM role or AWS CLI profile. Never commit keys or paste them into ChatGPT.
5. Set AWS_REGION, LEARNING_CATALOG_BUCKET, and LEARNING_CATALOG_KEY=catalog/learning_resources.json. Optionally set LEARNING_CATALOG_EXPECTED_BUCKET_OWNER to the bucket owner's account ID.
6. Enable a supported Amazon Bedrock model and grant the role permission to invoke it.
7. Run: python agent.py "I am a beginner learning Python for data science. Recommend free documentation resources."
8. Confirm the agent actually invokes the tool and reports returned catalog IDs and official links. A local test is not proof of a live S3 call.

The model cannot choose the bucket/key. The tool reads one environment-configured object with GetObject, validates a 2 MiB size limit, checks schema and HTTPS URLs, filters results deterministically, and performs no S3 writes.

## Data contract and safeguards

- Versioned JSON schema, unique IDs, bounded entry count and bounded query/result sizes.
- HTTPS URLs only; embedded URL credentials are rejected, and each entry's approved host must match a small code-level allowlist of official domains.
- Enumerated learning levels/formats, non-empty skills, and ISO dates are validated.
- Catalog items older than 180 days from reviewed_on are marked REVIEW_DUE.
- SHA-256 fingerprints the exact bytes retrieved; it does not establish who authored the catalog.
- The agent cannot create, update, or delete catalog objects.
- The model is instructed to preserve source URLs and not invent substitutes for unmatched queries.

The reviewed_on date is a curator-maintained annotation, not an automated live URL check. The project does not claim current price, availability, course quality, accreditation, or job outcomes.

## Tests

The offline suite covers successful filters, no-match behavior, free-budget handling, result limits, review-age marking, duplicate IDs, invalid HTTPS URLs, unapproved domains, punctuation-only queries, future review dates, unsupported schema versions, mocked S3 retrieval, SHA-256/version metadata, expected bucket owner, missing configuration, oversized objects, and invalid JSON. No real AWS resource is needed for tests.

## Required challenge demo video

AWS Builder Center requires a public video under 3 minutes in the project's demo field. Follow docs/DEMO_SCRIPT.md. Show the actual S3 tool call in your AWS account; do not present the offline demo as live AWS access. Hide credentials and personal data.

## Copy-ready Builder Center project fields

Title: OpportunityLens: S3-Grounded Learning Resource Tool for CareerPath AI

Description: OpportunityLens extends the existing CareerPath AI learning-resource workflow with one read-only Amazon S3 tool. The Strands agent retrieves a curated JSON catalog, validates entries, filters by skill, budget, and format, and returns source-linked resources with review dates and S3 integrity metadata. It avoids inventing substitute resource links when no catalog match exists. The project includes offline tests and a live S3/Bedrock walkthrough after AWS setup; review dates are not a guarantee of current URL availability or price terms.

Technology: Amazon S3, Amazon Bedrock, Strands Agents SDK, Python, boto3.
Suggested tags: Artificial Intelligence, Generative AI, Amazon S3, Amazon Bedrock, Python.

## Official references

Strands Python quickstart: https://strandsagents.com/docs/user-guide/sdk/quickstart/python/
Strands tools guide: https://strandsagents.com/docs/user-guide/sdk/tools/
S3 GetObject API: https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
Amazon Bedrock quickstart: https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html
Python Tutorial: https://docs.python.org/3/tutorial/index.html
PostgreSQL Tutorial: https://www.postgresql.org/docs/current/tutorial.html
pandas Getting Started: https://pandas.pydata.org/docs/getting_started/
scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
