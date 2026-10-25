# Integrating OpportunityLens with CareerPath AI

The existing CareerPath AI configuration includes a Learning Resource & Opportunity Navigator stage. OpportunityLens adds retrieval for named learning resources so the model can ground recommendations in a maintained catalog stored in Amazon S3.

Suggested update to that stage's instructions:

When recommending named learning resources, official URLs, format, or cost labels, call search_verified_learning_resources first. Use only returned catalog entries for specific resources. Preserve each resource ID and official URL. Do not infer prices from missing data. If no result matches, say the catalog has no match. If a resource is marked REVIEW_DUE, tell the learner to recheck the official page.

The tool is deliberately read-only and cannot create, update, or delete catalog objects. Catalog changes should go through a reviewed maintenance process.
