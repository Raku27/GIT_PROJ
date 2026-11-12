"""Run with: python -m runner --config PATH --workspace PATH."""

import argparse
import json
import signal
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .pipeline import run_pipeline


def _interrupt(signum, frame):
    raise KeyboardInterrupt


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run a trusted project's configured commands"
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir", type=Path, help="Default: WORKSPACE/.pipeline-runs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print configuration without executing commands",
    )
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config, args.workspace)
        if args.dry_run:
            print(json.dumps(config, indent=2))
            return 0
        previous = signal.signal(signal.SIGTERM, _interrupt)
        try:
            report = run_pipeline(
                config, args.output_dir or args.workspace / ".pipeline-runs"
            )
        finally:
            signal.signal(signal.SIGTERM, previous)
    except (ConfigError, ValueError, OSError) as exc:
        print("Runner error: " + str(exc), file=sys.stderr)
        return 2
    for stage in report["stages"]:
        print(
            stage["name"]
            + ": "
            + stage["status"]
            + (" — " + stage["error"] if stage["error"] else "")
        )
    print("Report: " + str(Path(report["run_dir"]) / "report.json"))
    return 130 if report["interrupted"] else (0 if report["status"] == "success" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
