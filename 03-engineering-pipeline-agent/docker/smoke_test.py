"""Explicit live-Docker checks for the dependency-free runner image (not unit discovery)."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile


def check(image, output_dir):
    image_user = subprocess.check_output(
        ["docker", "image", "inspect", "--format", "{{.Config.User}}", image], text=True
    ).strip()
    if image_user != "10001:10001":
        raise AssertionError("Image must default to its dedicated non-root user")
    cases = [
        (
            "success",
            [
                dict(
                    name="hello",
                    argv=["{python}", "-c", "print('external workspace works')"],
                )
            ],
            0,
            ["success"],
        ),
        (
            "failure",
            [
                dict(name="fail", argv=["{python}", "-c", "raise SystemExit(7)"]),
                dict(
                    name="blocked",
                    argv=["{python}", "-c", "raise RuntimeError('must not run')"],
                ),
            ],
            1,
            ["failed", "skipped"],
        ),
        (
            "timeout",
            [
                dict(
                    name="slow",
                    argv=["{python}", "-c", "import time; time.sleep(10)"],
                    timeout_seconds=0.2,
                )
            ],
            1,
            ["failed"],
        ),
    ]
    for name, stages, expected_exit, expected_statuses in cases:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            (workspace / "pipeline.json").write_text(
                json.dumps(dict(version=1, name=name, project_dir=".", stages=stages))
            )
            reports = (output_dir / name).resolve()
            reports.mkdir(parents=True, exist_ok=True)
            command = [
                "docker",
                "run",
                "--rm",
                "--init",
                "--user",
                str(os.getuid()) + ":" + str(os.getgid()),
                "--read-only",
                "--network",
                "none",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--memory",
                "256m",
                "--cpus",
                "1",
                "--pids-limit",
                "64",
                "--tmpfs",
                "/tmp:rw,exec,nosuid,nodev,size=64m",
                "--mount",
                "type=bind,src=" + str(workspace) + ",dst=/workspace,readonly",
                "--mount",
                "type=bind,src=" + str(reports) + ",dst=/reports",
                image,
                "--config",
                "/workspace/pipeline.json",
            ]
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=30
            )
            if completed.returncode != expected_exit:
                raise AssertionError(
                    name + " exit mismatch: " + completed.stdout + completed.stderr
                )
            runs = sorted(
                reports.glob("*/report.json"), key=lambda path: path.stat().st_mtime
            )
            if not runs:
                raise AssertionError(name + " did not persist a report on the host")
            report = json.loads(runs[-1].read_text())
            if [stage["status"] for stage in report["stages"]] != expected_statuses:
                raise AssertionError(name + " stage status mismatch")
            if name == "success":
                log = runs[-1].parent / report["stages"][0]["stdout_log"]
                if "external workspace works" not in log.read_text():
                    raise AssertionError("stdout did not persist on the host")
            if name == "timeout" and "timeout" not in report["stages"][0]["error"]:
                raise AssertionError("Timeout not identified in report")
            print(name + ": passed (report and logs persisted)", flush=True)
    print("All three live Docker checks passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="git-proj-runner:base")
    parser.add_argument(
        "--output-dir", type=Path, default=Path(".pipeline-runs/docker-smoke")
    )
    args = parser.parse_args()
    check(args.image, args.output_dir)
