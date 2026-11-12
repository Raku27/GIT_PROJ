# API usage

From `02-matching-project`, install the locked environment and run `python -m src.api.main`. The default address is `http://127.0.0.1:8000`. Use `/docs` for generated schemas and interactive requests.

## Endpoints

- `GET /`: version and endpoint links.
- `GET /health`: process liveness, returning `{"status":"healthy"}`. This is not a capacity/readiness check.
- `POST /api/match`: one-to-one matching.

## Executable request

```bash
curl --fail-with-body http://127.0.0.1:8000/api/match \
  -H 'Content-Type: application/json' \
  -d '{
    "entities_a": [{"id":"candidate_1","entity_type":"candidate","attributes":{"skills":["Python","SQL"],"experience_years":5}}],
    "entities_b": [{"id":"job_1","entity_type":"job","attributes":{"required_skills":["Python"],"min_experience":3}}],
    "criteria": {
      "weights":{"skills":0.7,"experience_years":0.3},
      "required_attributes":["skills","experience_years"],
      "attribute_mappings":{"skills":"required_skills","experience_years":"min_experience"},
      "min_score":0.5
    },
    "algorithm":"hungarian"
  }'
```

Expected: one match `candidate_1 → job_1`, score `1.0`, no unmatched entities, total score `1.0`. Each match contains `details.attribute_scores`; responses also contain execution time and summary statistics. Execution time is measured with a monotonic performance clock.

## Rules

- Supported algorithms: `hungarian`, `gale_shapley` (case-sensitive).
- Entity types: `user`, `item`, `job`, `candidate`, `mentor`, `mentee`.
- Weights must be finite, nonnegative and sum to a positive value; they are normalized once.
- `min_score` is within `[0,1]`; only positive-score pairs at or above the threshold can match.
- Field mappings go from group A's attribute names to group B's names. Required attributes use group A's names.
- `required_attributes` means field presence and non-null values; it does not require equal values or make a particular weighted criterion mandatory.
- `optional_attributes` is descriptive metadata; weighted fields are selected by `weights`.
- `max_matches` must be `1`. Nonempty `constraints` are rejected.
- IDs must be nonblank and unique across both groups. Empty groups are valid and return all supplied entities unmatched.
- Explicit `preferences` must list unique opposite-group IDs. In Gale–Shapley, omitted partners are unacceptable; `[]` accepts nobody, while omitted/null preferences derive rankings from scores. Rankings are ignored by the assignment objective.
- Limits: 200 entities per group, 200 preferences per entity, 128 characters per ID, 50 attribute keys and 10,000 serialized JSON bytes of attributes per entity.

## Errors

Invalid input returns HTTP **422**, including unknown algorithms/types, duplicate IDs and unsupported constraints. Unexpected failures return HTTP **500** with a generic message and request ID; exception details are logged server-side.

## Local and public operation

The Python entry point binds only to localhost. For local development, `uvicorn src.api.main:app --reload --host 127.0.0.1` is also supported.

This demo has no authentication or rate limiter. Before public exposure configure gateway access/rate limits and a raw-body limit, bounded compute workers and execution timeouts. Request model limits are enforced after parsing. Thread-pool execution protects the event loop but does not isolate CPU or guarantee throughput.

See the [README](../README.md) for scoring semantics, limitations and tests.
