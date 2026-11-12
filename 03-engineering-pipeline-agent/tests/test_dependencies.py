"""Sequential prerequisites must succeed even when fail-fast is disabled."""

import unittest
from unittest.mock import patch

from agents.orchestrator_agent import (
    OrchestratorAgent, PipelineStage, StageResult, StageStatus,
)


class TestStagePrerequisites(unittest.TestCase):
    def setUp(self):
        sleeper = patch("agents.orchestrator_agent.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)
        passing_tests = patch.object(
            OrchestratorAgent, "_test_stage",
            return_value={"tests_run": 3, "tests_passed": 3, "tests_failed": 0},
        )
        passing_tests.start()
        self.addCleanup(passing_tests.stop)

    def test_failure_blocks_every_later_stage_without_fail_fast(self):
        for failed_stage in list(PipelineStage)[:-1]:
            with self.subTest(failed_stage=failed_stage.value):
                agent = OrchestratorAgent({"stop_on_failure": False})
                handler = "_" + failed_stage.value + "_stage"
                with patch.object(agent, handler, side_effect=RuntimeError("injected failure")):
                    with patch.object(agent, "_run_stage_logic", wraps=agent._run_stage_logic) as run:
                        summary = agent.execute_pipeline({"name": "dependency-test"})
                self.assertEqual(summary["pipeline_status"], "failed")
                self.assertEqual(summary["failed_stages"], [failed_stage.value])
                index = agent.stages.index(failed_stage)
                self.assertEqual(run.call_count, index + 1)
                for later in agent.stages[index + 1:]:
                    self.assertEqual(agent.stage_results[later].status, StageStatus.SKIPPED)
                    self.assertEqual(agent.stage_results[later].execution_time, 0)

    def test_reported_test_failure_blocks_packaging_and_deployment(self):
        agent = OrchestratorAgent({"stop_on_failure": False})
        with patch.object(agent, "_test_stage", return_value={"tests_run": 3, "tests_passed": 2, "tests_failed": 1}):
            with patch.object(agent, "_package_stage") as package:
                with patch.object(agent, "_deploy_stage") as deploy:
                    summary = agent.execute_pipeline({"name": "failed-tests"})
        package.assert_not_called()
        deploy.assert_not_called()
        self.assertEqual(summary["pipeline_status"], "failed")
        self.assertEqual(agent.stage_results[PipelineStage.MONITOR].status, StageStatus.SKIPPED)

    def test_explicitly_disabled_optional_stages_allow_deployment(self):
        for flags in [{"run_tests": False}, {"run_quality_checks": False},
                      {"run_tests": False, "run_quality_checks": False}]:
            with self.subTest(flags=flags):
                agent = OrchestratorAgent(dict(flags, stop_on_failure=False))
                with patch.object(agent, "_deploy_stage", wraps=agent._deploy_stage) as deploy:
                    summary = agent.execute_pipeline({"name": "optional-stages"})
                deploy.assert_called_once()
                self.assertEqual(summary["pipeline_status"], "success")

    def test_disabled_optional_stage_does_not_bypass_a_build_failure(self):
        agent = OrchestratorAgent({"stop_on_failure": False, "run_tests": False,
                                   "run_quality_checks": False})
        with patch.object(agent, "_build_stage", side_effect=RuntimeError("build failed")):
            with patch.object(agent, "_deploy_stage") as deploy:
                summary = agent.execute_pipeline({"name": "blocked"})
        deploy.assert_not_called()
        self.assertEqual(summary["pipeline_status"], "failed")
        self.assertEqual(agent.stage_results[PipelineStage.PACKAGE].status, StageStatus.SKIPPED)

    def test_missing_or_unfinished_prerequisite_blocks_deployment(self):
        for status in [None, StageStatus.PENDING, StageStatus.RUNNING, StageStatus.SKIPPED,
                       StageStatus.FAILED]:
            with self.subTest(status=status):
                agent = OrchestratorAgent({"stop_on_failure": False})
                for stage in agent.stages[:agent.stages.index(PipelineStage.DEPLOY)]:
                    agent.stage_results[stage] = StageResult(stage, StageStatus.SUCCESS, 0, {})
                if status is None:
                    del agent.stage_results[PipelineStage.BUILD]
                else:
                    agent.stage_results[PipelineStage.BUILD].status = status
                self.assertFalse(agent._should_execute_stage(PipelineStage.DEPLOY))

    def test_all_successful_prerequisites_allow_deployment(self):
        agent = OrchestratorAgent({"stop_on_failure": False})
        with patch.object(agent, "_deploy_stage", wraps=agent._deploy_stage) as deploy:
            summary = agent.execute_pipeline({"name": "passing"})
        deploy.assert_called_once()
        self.assertEqual(summary["pipeline_status"], "success")
        self.assertEqual(summary["stages_successful"], 8)


if __name__ == "__main__":
    unittest.main()
