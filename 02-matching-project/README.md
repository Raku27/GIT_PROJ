# Matching Optimization API

A Python/FastAPI portfolio project comparing maximum-total-score assignment with stable preference matching. The included scenario pairs candidates with jobs using skills, experience, education and location.

## Implemented

- One-to-one assignment through SciPy's `linear_sum_assignment` (modified Jonker–Volgenant solver).
- Gale–Shapley matching with explicit or score-derived rankings, including incomplete preference lists.
- Shared normalized scoring, configurable field mappings and per-attribute explanations.
- Validated REST API, Swagger UI, regression tests and GitHub Actions checks.

This is a local demonstration. Custom constraints, multiple matches per entity, persistence, dashboards, Greedy and Linear Programming algorithms are not implemented. No production capacity or recruitment outcome claims are made.

## Run locally

Tested runtime: **Python 3.13**.

```bash
git clone https://github.com/Raku27/GIT_PROJ.git
cd GIT_PROJ/02-matching-project
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
python example_usage.py
python -m src.api.main
```

The server binds to `127.0.0.1:8000`. Open [Swagger UI](http://127.0.0.1:8000/docs) or [ReDoc](http://127.0.0.1:8000/redoc).

`requirements.txt` pins direct runtime dependencies; `requirements-dev.txt` adds test tools; `requirements-lock.txt` pins the complete tested runtime and test environment.

## Example result

The supplied example maps `skills → required_skills`, `experience_years → min_experience` and `education → education_level`. Both algorithms return:

| Candidate | Job | Score |
|---|---|---|
| candidate_1 | job_1 | 0.80 |
| candidate_2 | job_2 | 1.00 |
| candidate_3 | job_3 | 1.00 |

Total score: **2.80**. Runtime depends on the machine; these results are not a performance benchmark.

## Algorithm tradeoffs

| Mode | Objective | Preferences |
|---|---|---|
| `hungarian` | Maximize the sum of eligible pair scores | Explicit rankings do not influence assignment |
| `gale_shapley` | No blocking pair among mutually acceptable ranked partners | Explicit rankings take precedence; otherwise derive rankings from scores |

Both modes use the same scoring policy. Stability does not imply maximum total score. Proposers are group A; score ties use input order. Positive scores meeting `min_score` are eligible. Required fields must exist and be non-null on both mapped sides. Missing fields contribute zero; remaining weights are not renormalized per pair.

For job matching, `required_skills` uses coverage of the job's skills, and `min_experience` uses a binary meets-minimum score. These are weighted comparisons, not mandatory skill/experience constraints. Other lists use Jaccard overlap, strings use normalized exact equality, and numeric similarity uses relative difference. Education strings are exact comparisons, not an ordered qualification hierarchy. These rules are illustrative and have not been validated for real hiring decisions.

## Verify

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Tests cover startup/imports, empty and rectangular inputs, invalid requests, example results, missing fields, explicit preferences, exhaustive small-case assignment optimality and randomized blocking-pair checks for stable matching. CI runs on Python 3.13.

## Architecture

```text
src/api/main.py              Request validation, error handling and response schemas
src/models/entities.py      Domain objects and normalized criteria
src/algorithms/scoring.py    Shared scoring, eligibility and ID validation
src/algorithms/hungarian.py  Maximum-score assignment
src/algorithms/gale_shapley.py Stable preference matching
example_usage.py             Reproducible candidate/job example
tests/                       Algorithm and API regression tests
```

The service is stateless. Synchronous API handlers run in FastAPI's worker thread pool. This keeps computation off the event loop; threads do not provide CPU isolation or unlimited concurrency. Both methods materialize all candidate pairs (O(nm) memory); derived rankings require sorting, and Gale–Shapley uses constant-time ranking lookups during proposals.

## Deployment limits and next improvements

The API permits at most 200 entities per group, 50 attribute keys per entity and 10,000 serialized attribute bytes per entity. IDs must be unique across both groups. Unsupported custom constraints and `max_matches != 1` are rejected.

There is no application authentication or rate limiting. Before exposing publicly, add gateway access controls, rate limits, a raw request-body size limit, execution timeouts and bounded worker capacity. Model bounds apply after JSON parsing and are not a network-body limit.

## Evidence and demo

- [Measured benchmarks](docs/benchmarks.md): seeded runs at 10, 50, 100 and 200 entities per group, with raw samples, latency and process memory.
- [Two-minute walkthrough](docs/demo.md): run the service, inspect score explanations, and compare competing objectives.
- Run `python -m examples.algorithm_tradeoff` to see maximum-score assignment achieve **2.0** while preference-stable matching achieves **0.2** on the same pair scores. Both results are correct for their different objectives.

Next milestones: a labeled evaluation dataset, controlled concurrent API load tests, and a bounded public deployment. See the [API guide](docs/api_usage_guide.md).

## Author and license

Rahul Kumaar Subramani · [GitHub](https://github.com/Raku27) · [MIT license](../LICENSE) · [Contributing](../CONTRIBUTING.md)
