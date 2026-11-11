"""Seeded algorithm benchmarks; isolated workers report latency and peak process RSS."""

import argparse
import importlib.metadata
import json
import os
import platform
import random
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter


def sample(size, algorithm, seed):
    import resource

    from src.algorithms.gale_shapley import GaleShapleyMatcher
    from src.algorithms.hungarian import HungarianMatcher
    from src.models.entities import Criteria, Entity, EntityType

    rng = random.Random(seed)
    skills = ["Python", "SQL", "Java", "Go", "Linux", "Git"]

    def group(prefix):
        return [
            Entity(
                f"{prefix}{i}",
                EntityType.USER,
                {
                    "experience": rng.randrange(1, 15),
                    "skills": rng.sample(skills, 3),
                    "location": rng.choice(["Berlin", "Remote", "Munich"]),
                },
            )
            for i in range(size)
        ]

    a, b = group("a"), group("b")
    criteria = Criteria(
        {"experience": 0.3, "skills": 0.5, "location": 0.2}, min_score=0.3
    )
    matcher = HungarianMatcher() if algorithm == "hungarian" else GaleShapleyMatcher()
    start = perf_counter()
    result = matcher.match(a, b, criteria)
    elapsed = perf_counter() - start
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == "darwin" else rss * 1024
    return {
        "size_per_group": size,
        "algorithm": algorithm,
        "seed": seed,
        "latency_ms": elapsed * 1000,
        "peak_process_rss_mib": rss_bytes / 1024**2,
        "matches": len(result.matches),
        "total_score": result.total_score,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10, 50, 100, 200])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results.json"))
    parser.add_argument("--worker", nargs=3, metavar=("SIZE", "ALGORITHM", "SEED"))
    args = parser.parse_args()
    if args.worker:
        size, algorithm, seed = args.worker
        print(json.dumps(sample(int(size), algorithm, int(seed))))
        return
    if args.repeats < 1 or any(n < 1 or n > 200 for n in args.sizes):
        parser.error("Use positive repeats and sizes between 1 and 200")
    raw = []
    for size in args.sizes:
        for algorithm in ["hungarian", "gale_shapley"]:
            for repeat in range(args.repeats):
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "benchmarks.run",
                        "--worker",
                        str(size),
                        algorithm,
                        str(27 + repeat),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).resolve().parents[1],
                    timeout=120,
                )
                raw.append(json.loads(completed.stdout))
            print(f"Completed {algorithm}: {size} × {size}", flush=True)
    summary = []
    for size in args.sizes:
        for algorithm in ["hungarian", "gale_shapley"]:
            rows = [
                r
                for r in raw
                if r["size_per_group"] == size and r["algorithm"] == algorithm
            ]
            summary.append(
                {
                    "size_per_group": size,
                    "algorithm": algorithm,
                    "median_latency_ms": statistics.median(
                        r["latency_ms"] for r in rows
                    ),
                    "min_latency_ms": min(r["latency_ms"] for r in rows),
                    "max_latency_ms": max(r["latency_ms"] for r in rows),
                    "max_peak_process_rss_mib": max(
                        r["peak_process_rss_mib"] for r in rows
                    ),
                }
            )
    cpu = platform.processor() or platform.machine()
    if sys.platform == "darwin":
        try:
            cpu = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            pass  # Architecture remains available when the host restricts hardware metadata.
    report = {
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "environment": {
            "os": platform.platform(),
            "cpu": cpu,
            "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
            "packages": {p: importlib.metadata.version(p) for p in ["numpy", "scipy"]},
        },
        "method": "5 default repeats; independent fresh subprocess per sample; seeds 27 onward. Timer covers match() only. Peak RSS covers the whole worker including imports and input creation; not incremental memory, not API latency, no warm-up. RSS units normalized for macOS/Linux. Synthetic balanced groups, three weighted attributes, min_score=0.3; derived preference rankings.",
        "repeats": args.repeats,
        "summary": summary,
        "samples": raw,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
