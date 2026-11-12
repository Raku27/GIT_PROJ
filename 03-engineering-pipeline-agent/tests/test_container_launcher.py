"""Test the launcher with a fake Docker executable, not a live Docker engine."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_container.sh"


class TestContainerLauncher(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "docker.jsonl"
        fake = self.bin / "docker"
        fake.write_text(
            "#!"
            + sys.executable
            + "\n"
            + """import json, os, sys
with open(os.environ["FAKE_DOCKER_LOG"], "a") as stream:
    stream.write(json.dumps(sys.argv[1:]) + "\\n")
raise SystemExit(int(os.environ.get("FAKE_BUILD_EXIT" if sys.argv[1] == "build" else "FAKE_RUN_EXIT", "0")))
"""
        )
        fake.chmod(0o755)
        self.env = dict(
            os.environ,
            PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
            FAKE_DOCKER_LOG=str(self.log),
            RUNNER_IMAGE="unit-runner:local",
            RUNNER_REPORTS_DIR=str(self.root / "reports with spaces"),
        )
        self.env.pop("FAKE_BUILD_EXIT", None)
        self.env.pop("FAKE_RUN_EXIT", None)

    def launch(self, *args, **overrides):
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), *args],
            cwd=str(self.root),
            env=dict(self.env, **overrides),
            capture_output=True,
            text=True,
            timeout=10,
        )

    def calls(self):
        return (
            [json.loads(line) for line in self.log.read_text().splitlines()]
            if self.log.exists()
            else []
        )

    def test_build_and_run_preserve_arguments_and_mount_host_reports(self):
        result = self.launch("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        build, run = self.calls()
        self.assertEqual(build[0], "build")
        self.assertEqual(build[build.index("--target") + 1], "matching")
        self.assertEqual(build[-1], str(SCRIPT.parents[2]))
        for flag in ("--rm", "--init", "--read-only"):
            self.assertIn(flag, run)
        self.assertEqual(run[run.index("--network") + 1], "none")
        self.assertEqual(run[run.index("--cap-drop") + 1], "ALL")
        self.assertEqual(
            run[run.index("--user") + 1], str(os.getuid()) + ":" + str(os.getgid())
        )
        self.assertIn("size=256m", run[run.index("--tmpfs") + 1])
        self.assertEqual(
            run[run.index("--mount") + 1],
            "type=bind,src=" + self.env["RUNNER_REPORTS_DIR"] + ",dst=/reports",
        )
        self.assertEqual(run[-1], "--dry-run")
        self.assertIn("Host reports:", result.stdout)

    def test_failed_build_does_not_run_container(self):
        result = self.launch(FAKE_BUILD_EXIT="17")
        self.assertEqual(result.returncode, 17)
        self.assertEqual([call[0] for call in self.calls()], ["build"])

    def test_container_failure_exit_code_is_preserved(self):
        self.assertEqual(self.launch(FAKE_RUN_EXIT="9").returncode, 9)

    def test_comma_in_mount_path_is_rejected_before_build(self):
        result = self.launch(RUNNER_REPORTS_DIR=str(self.root / "invalid,path"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
