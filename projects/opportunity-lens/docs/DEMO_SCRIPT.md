# Public demo script — target length 2 minutes 30 seconds

Record only what actually ran in your AWS account. Do not claim a live S3/Bedrock call if you only ran the local demo.

## 0:00–0:20 — The gap
Show the existing CareerPath AI learning-resource navigator. Explain that it can build career plans, but named resource links and cost details should be grounded in data.

## 0:20–0:45 — Before
Run python main.py --skill "data science" --budget free as a deterministic local demo. Show that results come from the catalog. Then run python main.py --skill "quantum underwater basket weaving" and show the explicit empty result instead of a fabricated recommendation. If you have working Bedrock access, you may also show agent_before.py.

## 0:45–1:15 — The one new tool
Show search_verified_learning_resources in catalog_tool.py. Explain that it reads one fixed, environment-configured S3 object, validates entries, filters by skill/budget/format and returns source metadata. The model cannot choose an arbitrary bucket/key; it has no write or delete access.

## 1:15–2:05 — After (live AWS required)
After configuring S3 and Bedrock, run python agent.py "I am a beginner learning Python for data science. Recommend free documentation resources." Show the actual tool invocation, resource IDs and official URLs, and the returned S3 version/ETag/hash if available.

## 2:05–2:30 — Impact and limits
Show a REVIEW_DUE example or explain that it advises rechecking old catalog entries. State that catalog metadata does not live-check URLs, prices, course quality, or learning outcomes.

Before uploading, check that the recording is public and under 3 minutes, and paste its URL into the Builder Center project's demo field. Never show keys or personal data.
