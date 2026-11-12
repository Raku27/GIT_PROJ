"""Per-run state, dependency gates, logs and atomic JSON reports."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from .execution import execute


def _write_report(report, directory):
    temporary = directory / "report.json.tmp"
    temporary.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    temporary.replace(directory / "report.json")


def run_pipeline(config, output_dir):
    if os.name != "posix":
        raise ValueError("Command execution currently supports Linux and macOS only")
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory = output_dir / (config["name"] + "-" + uuid.uuid4().hex)
    directory.mkdir(mode=0o700)
    start = monotonic()
    report = {
        "name": config["name"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": config["project_dir"],
        "run_dir": str(directory),
        "status": "running",
        "execution_time": 0.0,
        "interrupted": False,
        "stages": [
            {
                **stage,
                "status": "pending",
                "returncode": None,
                "error": None,
                "execution_time": 0.0,
            }
            for stage in config["stages"]
        ],
    }
    _write_report(report, directory)
    statuses, halt = {}, False
    for stage, result in zip(config["stages"], report["stages"]):
        if halt or any(statuses[name] != "success" for name in stage["needs"]):
            result.update(
                status="skipped",
                error="Stopped after failure"
                if halt
                else "Prerequisite did not succeed",
            )
        else:
            result.update(
                status="running",
                stdout_log=stage["name"] + ".stdout.log",
                stderr_log=stage["name"] + ".stderr.log",
            )
            _write_report(report, directory)
            stage_start = monotonic()
            try:
                result.update(execute(stage, config["project_dir"], directory))
            except KeyboardInterrupt:
                result.update(
                    status="failed",
                    error="Interrupted by user",
                    execution_time=monotonic() - stage_start,
                )
                report["interrupted"] = True
            except OSError as exc:
                result.update(status="failed", error="Execution failed: " + str(exc))
            if result["status"] == "failed" and (
                config["fail_fast"] or report["interrupted"]
            ):
                halt = True
        statuses[stage["name"]] = result["status"]
        report["execution_time"] = monotonic() - start
        _write_report(report, directory)
    report["status"] = (
        "failed"
        if any(s["status"] == "failed" for s in report["stages"])
        else "success"
    )
    _write_report(report, directory)
    return report
