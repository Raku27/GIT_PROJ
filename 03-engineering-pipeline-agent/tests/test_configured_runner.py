"""Real subprocess tests for the configurable runner; no cloud or deployment access."""

import json
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from runner.config import ConfigError, load_config
from runner.pipeline import run_pipeline

CLI = Path(__file__).resolve().parents[1] / "run_pipeline.py"


class TestConfiguredRunner(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.config_file = self.root / "pipeline.json"
        self.output = self.root / "reports"

    def command(self, name="first", code="print('ok')", **options):
        return dict(name=name, argv=["{python}", "-c", code], **options)

    def configure(self, stages=None, **options):
        raw = dict(
            version=1,
            name="demo",
            project_dir="project",
            stages=stages if stages is not None else [self.command()],
        )
        raw.update(options)
        self.config_file.write_text(json.dumps(raw))
        return load_config(self.config_file, self.root)

    def execute(self, config):
        return run_pipeline(config, self.output)

    def cli(self, *extra):
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(CLI),
                "--config",
                str(self.config_file),
                "--workspace",
                str(self.root),
                "--output-dir",
                str(self.output),
                *extra,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_success_records_exit_codes_logs_and_working_directory(self):
        config = self.configure(
            [
                self.command(
                    code="import os,sys; print(os.getcwd()); print('warning', file=sys.stderr)"
                )
            ]
        )
        report = self.execute(config)
        self.assertEqual(report["status"], "success")
        stage = report["stages"][0]
        self.assertEqual(stage["returncode"], 0)
        run = Path(report["run_dir"])
        self.assertIn(str(self.project), (run / stage["stdout_log"]).read_text())
        self.assertIn("warning", (run / stage["stderr_log"]).read_text())
        self.assertEqual(json.loads((run / "report.json").read_text()), report)

    def test_failed_prerequisite_blocks_descendants_but_not_independent_stages(self):
        config = self.configure(
            [
                self.command("fail", "raise SystemExit(7)"),
                self.command("blocked"),
                self.command("independent", needs=[]),
                self.command("still-blocked", needs=["blocked", "independent"]),
            ],
            fail_fast=False,
        )
        report = self.execute(config)
        self.assertEqual(
            [s["status"] for s in report["stages"]],
            ["failed", "skipped", "success", "skipped"],
        )
        self.assertEqual(report["stages"][0]["returncode"], 7)
        self.assertEqual(report["status"], "failed")

    def test_fail_fast_also_skips_independent_stages(self):
        config = self.configure(
            [
                self.command("fail", "raise SystemExit(1)"),
                self.command("independent", needs=[]),
            ]
        )
        self.assertEqual(
            [s["status"] for s in self.execute(config)["stages"]], ["failed", "skipped"]
        )

    def test_missing_executable_fails_and_blocks_next_stage(self):
        config = self.configure(
            [
                dict(name="missing", argv=[str(self.root / "not-a-program")]),
                self.command("later"),
            ]
        )
        stages = self.execute(config)["stages"]
        self.assertEqual(stages[0]["status"], "failed")
        self.assertIsNone(stages[0]["returncode"])
        self.assertIn("Unable to start", stages[0]["error"])
        self.assertEqual(stages[1]["status"], "skipped")

    def test_timeout_kills_child_process_group(self):
        marker, child_id = self.project / "leaked-child", self.project / "child-id"
        child = "import time,pathlib; time.sleep(.8); pathlib.Path('leaked-child').write_text('bad')"
        parent = (
            "import subprocess,sys,time,pathlib; "
            "p=subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); "
            "pathlib.Path('child-id').write_text(str(p.pid)); time.sleep(10)"
        )
        report = self.execute(
            self.configure([self.command(code=parent, timeout_seconds=0.3)])
        )
        self.assertEqual(report["status"], "failed")
        self.assertIn("timeout", report["stages"][0]["error"])
        self.assertTrue(
            child_id.exists(), "Parent must spawn its child before the deadline"
        )
        time.sleep(0.85)
        self.assertFalse(
            marker.exists(), "Timed-out descendants must not continue writing"
        )

    def test_log_output_is_bounded_but_command_still_completes(self):
        code = "import os; os.write(1,b'x'*100000); os.write(2,b'y'*100000)"
        with patch("runner.execution.LOG_LIMIT_BYTES", 1024):
            report = self.execute(self.configure([self.command(code=code)]))
        stage = report["stages"][0]
        self.assertEqual(stage["status"], "success")
        self.assertTrue(stage["logs_truncated"])
        for key in ("stdout_log", "stderr_log"):
            self.assertEqual(
                (Path(report["run_dir"]) / stage[key]).stat().st_size, 1024
            )

    def test_run_directory_placeholder_keeps_command_artifacts_with_report(self):
        stage = dict(
            name="artifact",
            argv=[
                "{python}",
                "-c",
                "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('artifact')",
                "{run_dir}/artifact.txt",
            ],
        )
        report = self.execute(self.configure([stage]))
        self.assertEqual(report["status"], "success")
        self.assertEqual(
            (Path(report["run_dir"]) / "artifact.txt").read_text(), "artifact"
        )
        self.assertNotIn("{run_dir}", report["stages"][0]["argv"][-1])

    def test_repeated_runs_have_distinct_reports_and_fresh_results(self):
        config = self.configure()
        first = self.execute(config)
        config["stages"][0]["argv"] = [sys.executable, "-c", "raise SystemExit(3)"]
        second = self.execute(config)
        self.assertNotEqual(first["run_dir"], second["run_dir"])
        self.assertEqual(first["status"], "success")
        self.assertEqual(second["status"], "failed")
        self.assertEqual(
            json.loads((Path(first["run_dir"]) / "report.json").read_text())["status"],
            "success",
        )

    def test_arguments_are_literal_and_do_not_invoke_a_shell(self):
        argument = "; touch should-not-exist $(echo surprise)"
        stage = dict(
            name="literal",
            argv=["{python}", "-c", "import sys; print(sys.argv[1])", argument],
        )
        report = self.execute(self.configure([stage]))
        self.assertEqual(report["status"], "success")
        self.assertIn(
            argument, (Path(report["run_dir"]) / "literal.stdout.log").read_text()
        )
        self.assertFalse((self.project / "should-not-exist").exists())

    def test_dry_run_validates_without_executing_or_creating_reports(self):
        self.configure(
            [self.command(code="from pathlib import Path; Path('marker').touch()")]
        )
        response = self.cli("--dry-run")
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(json.loads(response.stdout)["name"], "demo")
        self.assertFalse((self.project / "marker").exists())
        self.assertFalse(self.output.exists())

    def test_cli_exit_codes_for_success_failure_and_bad_configuration(self):
        self.configure()
        self.assertEqual(self.cli().returncode, 0)
        self.configure([self.command(code="raise SystemExit(4)")])
        self.assertEqual(self.cli().returncode, 1)
        self.config_file.write_text("not json")
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_interrupt_records_failure_and_skips_remaining_stages(self):
        config = self.configure(
            [self.command(), self.command("later", needs=[])], fail_fast=False
        )
        with patch("runner.pipeline.execute", side_effect=KeyboardInterrupt):
            report = self.execute(config)
        self.assertTrue(report["interrupted"])
        self.assertEqual([s["status"] for s in report["stages"]], ["failed", "skipped"])
        self.assertEqual(report["status"], "failed")

    def test_cli_termination_cleans_up_and_saves_interrupted_report(self):
        self.configure(
            [
                self.command(
                    code="from pathlib import Path; import time; Path('ready').touch(); time.sleep(10)"
                )
            ]
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                str(CLI),
                "--config",
                str(self.config_file),
                "--workspace",
                str(self.root),
                "--output-dir",
                str(self.output),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 5
            while (
                not (self.project / "ready").exists()
                and process.poll() is None
                and time.monotonic() < deadline
            ):
                time.sleep(0.01)
            self.assertTrue((self.project / "ready").exists())
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 130, stderr.decode())
            self.assertIn(b"Report:", stdout)
            report = json.loads(next(self.output.glob("*/report.json")).read_text())
            self.assertTrue(report["interrupted"])
            self.assertEqual(report["status"], "failed")
            self.assertGreater(report["stages"][0]["execution_time"], 0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            for stream in (process.stdout, process.stderr):
                stream.close()

    def test_rejects_paths_outside_workspace_including_symlinks(self):
        for directory in ["../", str(self.root), "does-not-exist"]:
            with self.subTest(directory=directory), self.assertRaises(ConfigError):
                self.configure(project_dir=directory)
        (self.root / "link").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ConfigError):
            self.configure(project_dir="link")

    def test_rejects_malformed_schema_and_unsafe_dependencies(self):
        cases = [
            dict(version=True),
            dict(name="../bad"),
            dict(fail_fast="false"),
            dict(extra=True),
            dict(stages=[]),
            dict(stages=[self.command(), self.command()]),
            dict(stages=[self.command(needs=["later"])]),
            dict(stages=[self.command(needs=["first"])]),
            dict(
                stages=[
                    self.command(),
                    self.command("second", needs=["first", "first"]),
                ]
            ),
            dict(stages=[dict(name="bad", argv="echo hello")]),
            dict(stages=[dict(name="bad", argv=["echo", "\0"])]),
            dict(stages=[self.command(timeout_seconds=0)]),
            dict(stages=[self.command(timeout_seconds=True)]),
            dict(stages=[self.command(timeout_seconds=float("inf"))]),
            dict(stages=[self.command(timeout_seconds=float("nan"))]),
            dict(stages=[dict(self.command(), unknown=1)]),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ConfigError):
                self.configure(**case)

    def test_rejects_invalid_encoding_and_excessive_json_nesting(self):
        for content in [b"\xff", b"[" * 2000 + b"0" + b"]" * 2000]:
            with self.subTest(content_length=len(content)):
                self.config_file.write_bytes(content)
                with self.assertRaises(ConfigError):
                    load_config(self.config_file, self.root)

    def test_rejects_oversized_configuration(self):
        self.config_file.write_text(" " * 65537)
        with self.assertRaises(ConfigError):
            load_config(self.config_file, self.root)


if __name__ == "__main__":
    unittest.main()
