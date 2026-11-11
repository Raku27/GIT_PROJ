# Two-minute matching demo

## 1. Reproduce the candidate/job outcome

From `02-matching-project` in the installed Python 3.13 environment:

```bash
python example_usage.py
```

Both methods pair candidate_1/job_1, candidate_2/job_2 and candidate_3/job_3, with scores 0.80, 1.00 and 1.00. Total: 2.80. Field mappings connect candidate skills/experience to job requirements. The first education comparison is unequal, explaining the first score of 0.80.

## 2. Inspect an API request

```bash
python -m src.api.main
```

Open [Swagger UI](http://127.0.0.1:8000/docs) and use the complete request from the [API guide](api_usage_guide.md). Expected: one match with total score 1.0. Expand `details.attribute_scores` to see the skills and experience contributions. Remove the candidate's required skills field and repeat: that candidate and job are unmatched because the required field is missing.

## 3. Explain the algorithm tradeoff

```bash
python -m examples.algorithm_tradeoff
```

| Pair | Shared similarity score |
|---|---:|
| a1 / b1 | 1.0 |
| a1 / b2 | 0.1 |
| a2 / b1 | 0.1 |
| a2 / b2 | 1.0 |

Explicit rankings: a1 prefers b2, a2 prefers b1, b1 prefers a2, and b2 prefers a1.

Assignment chooses a1/b1 and a2/b2, total **2.0**. Gale–Shapley chooses a1/b2 and a2/b1, total **0.2**, giving everyone their first choice. The maximum-score assignment has blocking pairs under the supplied rankings; the preference-based result is stable. Stability and aggregate similarity answer different questions.

For an interview: explain why scoring, eligibility and optimization are separate concerns, how incomplete preferences define unacceptable partners, and why an illustrative similarity score should not be called validated hiring suitability.

See [benchmarks](benchmarks.md) for measurements and limitations. The demo runs locally; no hosted deployment is claimed.
