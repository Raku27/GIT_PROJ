"""Regression tests for reported test results and pipeline exit behavior."""

import contextlib
import io
import subprocess
import sys
import unittest
from unittest.mock import patch

from agents.orchestrator_agent import OrchestratorAgent, PipelineStage, StageStatus
from agents.orchestrator_agent import main as orchestrator_main
from example_usage import main as example_main


class TestReportedTestFailures(unittest.TestCase):
    def setUp(self):
        sleeper = patch("agents.orchestrator_agent.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def test_failed_tests_fail_pipeline_and_block_default_deployment(self):
        agent = OrchestratorAgent()
        with patch.object(agent, "_deploy_stage") as deploy:
            result = agent.execute_pipeline({"name": "regression"})
        self.assertEqual(result["pipeline_status"], "failed")
        self.assertEqual(result["failed_stages"], ["test"])
        stage = agent.stage_results[PipelineStage.TEST]
        self.assertEqual(stage.status, StageStatus.FAILED)
        self.assertEqual(stage.output["tests_failed"], 2)
        self.assertIn("2 test(s) failed", stage.error)
        deploy.assert_not_called()

    def test_passing_tests_allow_pipeline_to_complete(self):
        agent = OrchestratorAgent()
        passing = {"tests_run": 3, "tests_passed": 3, "tests_failed": 0}
        with patch.object(agent, "_test_stage", return_value=passing):
            result = agent.execute_pipeline({"name": "passing"})
        self.assertEqual(result["pipeline_status"], "success")
        self.assertEqual(result["stages_successful"], 8)
        self.assertEqual(agent.stage_results[PipelineStage.TEST].output, passing)

    def test_invalid_or_empty_reports_fail_closed(self):
        reports = [
            {},
            {"tests_run": 0, "tests_passed": 0, "tests_failed": 0},
            {"tests_run": 2, "tests_passed": 2, "tests_failed": 1},
            {"tests_run": 1, "tests_passed": 2, "tests_failed": -1},
            {"tests_run": 1, "tests_passed": 1, "tests_failed": "0"},
            {"tests_run": 1, "tests_passed": 1, "tests_failed": False},
        ]
        for report in reports:
            with self.subTest(report=report):
                agent = OrchestratorAgent()
                with patch.object(agent, "_test_stage", return_value=report):
                    result = agent._execute_stage(PipelineStage.TEST)
                self.assertEqual(result.status, StageStatus.FAILED)
                self.assertEqual(result.output, report)
                self.assertTrue(result.error)

    def test_test_runner_exception_fails_stage(self):
        agent = OrchestratorAgent()
        with patch.object(agent, "_test_stage", side_effect=RuntimeError("runner failed")):
            result = agent._execute_stage(PipelineStage.TEST)
        self.assertEqual(result.status, StageStatus.FAILED)
        self.assertEqual(result.error, "runner failed")

    def test_explicitly_disabled_tests_remain_skipped(self):
        agent = OrchestratorAgent({"run_tests": False})
        with patch.object(agent, "_test_stage") as test_stage:
            result = agent.execute_pipeline({"name": "skip"})
        test_stage.assert_not_called()
        self.assertEqual(agent.stage_results[PipelineStage.TEST].status, StageStatus.SKIPPED)
        self.assertEqual(result["pipeline_status"], "success")

    def test_entry_points_signal_failure(self):
        for entry_point in (orchestrator_main, example_main):
            with self.subTest(entry_point=entry_point.__module__):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(entry_point(), 1)

    def test_cli_processes_exit_nonzero_on_failed_tests(self):
        for script in ("agents/orchestrator_agent.py", "example_usage.py"):
            with self.subTest(script=script):
                code = (
                    "import runpy; from unittest.mock import patch\n"
                    "with patch('time.sleep'):\n"
                    f"    runpy.run_path({script!r}, run_name='__main__')\n"
                )
                completed = subprocess.run(
                    [sys.executable, "-B", "-c", code],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(completed.returncode, 1)
                self.assertIn("status: failed", completed.stdout.lower())

    def test_entry_points_signal_success(self):
        passing = {"tests_run": 1, "tests_passed": 1, "tests_failed": 0}
        with patch.object(OrchestratorAgent, "_test_stage", return_value=passing):
            for entry_point in (orchestrator_main, example_main):
                with self.subTest(entry_point=entry_point.__module__):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(entry_point(), 0)


if __name__ == "__main__":
    unittest.main()
