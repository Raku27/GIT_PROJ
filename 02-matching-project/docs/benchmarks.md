# Matching benchmarks

Measured locally on 2026-11-11. Raw samples and environment metadata are in [results.json](../benchmarks/results.json).

Hardware: **Apple M1 Pro**, 10 logical CPUs. OS: `macOS-27.2-arm64-arm-64bit-Mach-O`. Python 3.13.7, NumPy 2.5.4, SciPy 1.18.1.

## Method

Five independent fresh-process runs for each algorithm and size. Seeds 27–31 generate the same inputs for both algorithms. Each entity has experience, skills and location; weights are 0.3/0.5/0.2, with min_score=0.3. Gale–Shapley derives rankings from scores.

Latency measures only `match()`, including scoring, validation and assignment; it excludes interpreter startup, imports and input generation. No warm-up. Memory is the maximum observed **whole-process peak RSS**, including imports and input generation, rather than incremental algorithm allocation. It is sampled after the match and normalized from macOS/Linux platform units.

| Entities per group | Algorithm | Median latency (ms) | Min–max (ms) | Max peak RSS (MiB) |
|---|---|---:|---:|---:|
| 10 | hungarian | 0.46 | 0.44–0.48 | 74.5 |
| 10 | gale_shapley | 0.47 | 0.46–0.50 | 74.8 |
| 50 | hungarian | 8.90 | 8.83–9.26 | 74.8 |
| 50 | gale_shapley | 10.08 | 9.80–10.62 | 74.7 |
| 100 | hungarian | 35.05 | 34.03–36.63 | 77.4 |
| 100 | gale_shapley | 40.30 | 39.13–41.17 | 79.4 |
| 200 | hungarian | 140.23 | 135.15–141.24 | 90.0 |
| 200 | gale_shapley | 166.61 | 163.94–170.50 | 98.0 |

## Reproduce

From `02-matching-project` in the locked Python 3.13 environment on macOS or Linux:

```bash
python -m benchmarks.run
# Quick smoke run, writing outside the tracked result:
python -m benchmarks.run --sizes 2 --repeats 1 --output /tmp/matching-benchmark.json
```

## Interpretation and limits

Both implementations materialize all pair scores, so scoring and memory grow with the product of group sizes. These are single-process synthetic algorithm measurements, not API throughput, concurrency, worst-case Gale–Shapley complexity or a production capacity guarantee. Each trial uses a different seeded dataset; min–max captures both dataset and machine variability. Peak RSS includes shared interpreter/library overhead and should not be read as incremental memory per matching request.

The 200-per-group size is the API limit, not a demonstrated safe concurrency level. Five samples are descriptive; they do not support tail-latency guarantees. No conclusions about real recruitment quality follow from these timings.
