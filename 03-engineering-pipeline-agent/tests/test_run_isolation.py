"""Reusing an orchestrator must not reuse execution results or run context."""

import unittest
from unittest.mock import patch

from agents.orchestrator_agent import OrchestratorAgent, PipelineStage, StageStatus


class TestRunIsolation(unittest.TestCase):
    def setUp(self):
        sleeper = patch("agents.orchestrator_agent.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)
        passing = patch.object(
            OrchestratorAgent, "_test_stage",
            return_value={"tests_run": 1, "tests_passed": 1, "tests_failed": 0},
        )
        passing.start()
        self.addCleanup(passing.stop)

    def test_success_then_early_failure_does_not_reuse_successes(self):
        agent = OrchestratorAgent()
        first = agent.execute_pipeline({"name": "first"})
        old_results = agent.stage_results
        with patch.object(agent, "_source_stage", side_effect=RuntimeError("source failed")):
            second = agent.execute_pipeline({"name": "second"})
        self.assertEqual(second["project"], "second")
        self.assertEqual(second["stages_successful"], 0)
        self.assertEqual(second["failed_stages"], ["source"])
        self.assertEqual(second["pipeline_status"], "failed")
        self.assertEqual(agent.context["stages_completed"], [])
        self.assertIsNot(agent.stage_results, old_results)
        self.assertEqual(first["stages_successful"], 8)
        self.assertEqual(old_results[PipelineStage.DEPLOY].status, StageStatus.SUCCESS)
        for stage in list(PipelineStage)[1:]:
            result = agent.stage_results[stage]
            self.assertEqual(result.status, StageStatus.SKIPPED)
            self.assertEqual(result.output, {})
            self.assertEqual(result.execution_time, 0)
            self.assertIn("source", result.error)

    def test_failure_then_success_does_not_reuse_errors(self):
        agent = OrchestratorAgent()
        with patch.object(agent, "_build_stage", side_effect=RuntimeError("old build error")):
            first = agent.execute_pipeline({"name": "broken"})
        agent.context["old_marker"] = True
        second = agent.execute_pipeline({"name": "recovered"})
        self.assertEqual(first["failed_stages"], ["build"])
        self.assertEqual(second["pipeline_status"], "success")
        self.assertEqual(second["failed_stages"], [])
        self.assertEqual(second["stages_successful"], 8)
        self.assertNotIn("old_marker", agent.context)
        self.assertEqual(agent.context["stages_completed"], list(PipelineStage))
        self.assertTrue(all(result.error is None for result in agent.stage_results.values()))

    def test_first_run_failure_records_unexecuted_stages(self):
        agent = OrchestratorAgent()
        with patch.object(agent, "_build_stage", side_effect=RuntimeError("build failed")):
            summary = agent.execute_pipeline({"name": "first-failure"})
        self.assertEqual(len(summary["stage_results"]), len(PipelineStage))
        self.assertEqual(agent.context["stages_completed"], [PipelineStage.SOURCE])
        for stage in list(PipelineStage)[2:]:
            self.assertEqual(summary["stage_results"][stage.value]["status"], "skipped")

    def test_disabled_checks_do_not_keep_previous_outputs(self):
        agent = OrchestratorAgent()
        agent.execute_pipeline({"name": "checked"})
        agent.config.update(run_tests=False, run_quality_checks=False)
        summary = agent.execute_pipeline({"name": "checks-disabled"})
        self.assertEqual(summary["pipeline_status"], "success")
        self.assertEqual(summary["stages_successful"], 6)
        for stage in (PipelineStage.TEST, PipelineStage.QUALITY):
            result = agent.stage_results[stage]
            self.assertEqual(result.status, StageStatus.SKIPPED)
            self.assertEqual(result.output, {})
            self.assertIsNone(result.error)
            self.assertNotIn(stage, agent.context["stages_completed"])


if __name__ == "__main__":
    unittest.main()
