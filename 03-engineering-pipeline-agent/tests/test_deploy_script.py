"""Exercise deployment failures with fake commands; never contact Docker or a cluster."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "deploy.sh"


class TestDeploymentScript(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        (self.root / "Dockerfile").write_text("FROM scratch\n")
        self.env = dict(os.environ, PATH=str(self.bin), COMMAND_LOG=str(self.log),
                        APP_NAME="demo", REGISTRY="registry.example/team", KUBE_CONTEXT="test-cluster",
                        HEALTH_URL="https://demo.example/health", BUILD_CONTEXT=str(self.root))
        for key in ("FAIL_DOCKER", "FAIL_KUBECTL", "FAIL_CURL", "HTTP_STATUS",
                    "ROLLOUT_TIMEOUT_SECONDS", "API_TIMEOUT_SECONDS", "HEALTH_TIMEOUT_SECONDS"):
            self.env.pop(key, None)
        self.stub("docker", '''
if [[ "${FAIL_DOCKER:-}" == "$1" ]]; then exit 1; fi
''')
        self.stub("kubectl", '''
for argument in "$@"; do
    if [[ -n "${FAIL_KUBECTL:-}" && "$argument" == "$FAIL_KUBECTL" ]]; then exit 1; fi
done
''')
        self.stub("curl", '''
if [[ "${FAIL_CURL:-}" == "1" ]]; then exit 28; fi
printf '%s' "${HTTP_STATUS:-200}"
''')

    def stub(self, name, body):
        script = self.bin / name
        script.write_text("#!/bin/bash\nprintf '%s' " + repr(name) + " >> \"$COMMAND_LOG\"\n"
                          "printf ' <%s>' \"$@\" >> \"$COMMAND_LOG\"\n"
                          "printf '\\n' >> \"$COMMAND_LOG\"\n" + body)
        script.chmod(0o755)

    def run_script(self, environment="staging", tag="v1", **overrides):
        env = dict(self.env, **overrides)
        return subprocess.run(["/bin/bash", str(SCRIPT), environment, tag], cwd=str(self.root),
                              env=env, capture_output=True, text=True, timeout=10)

    def calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_success_requires_rollout_and_http_200(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Deployment completed successfully", result.stdout)
        calls = self.calls()
        self.assertIn("--context> <test-cluster", calls)
        self.assertIn("--namespace> <staging", calls)
        self.assertIn("--timeout=120s", calls)
        self.assertIn("--request-timeout=30s", calls)
        self.assertIn("--max-time> <15", calls)
        self.assertIn("--connect-timeout> <5", calls)
        self.assertIn("https://demo.example/health", calls)
        self.assertLess(calls.index("<get>"), calls.index("docker <build>"))
        self.assertLess(calls.index("<rollout>"), calls.index("curl"))

    def test_missing_tools_fail_before_any_side_effects(self):
        for tool in ("docker", "kubectl", "curl"):
            with self.subTest(tool=tool):
                path = self.bin / tool
                original = path.read_text()
                path.unlink()
                result = self.run_script()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(tool, result.stderr)
                self.assertEqual(self.calls(), "")
                path.write_text(original)
                path.chmod(0o755)

    def test_missing_required_configuration_fails_before_commands(self):
        for key in ("APP_NAME", "REGISTRY", "KUBE_CONTEXT", "HEALTH_URL"):
            with self.subTest(key=key):
                result = self.run_script(**{key: ""})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(key, result.stderr)
                self.assertEqual(self.calls(), "")

    def test_invalid_arguments_fail_before_commands(self):
        cases = [dict(environment="wrong"), dict(tag=""), dict(tag="--bad"),
                 dict(APP_NAME="bad name"), dict(REGISTRY="bad registry"),
                 dict(HEALTH_URL="file:///tmp/health"), dict(HEALTH_URL="https://bad host"),
                 dict(ROLLOUT_TIMEOUT_SECONDS="0"), dict(API_TIMEOUT_SECONDS="invalid"),
                 dict(HEALTH_TIMEOUT_SECONDS="-1")]
        for case in cases:
            with self.subTest(case=case):
                result = self.run_script(**case)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), "")

    def test_missing_dockerfile_fails_before_commands(self):
        (self.root / "Dockerfile").unlink()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Dockerfile", result.stderr)
        self.assertEqual(self.calls(), "")

    def test_wrong_or_inaccessible_target_stops_before_build(self):
        result = self.run_script(FAIL_KUBECTL="get")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("docker", self.calls())
        self.assertNotIn("<set>", self.calls())

    def test_docker_failures_stop_deployment(self):
        for operation in ("build", "tag", "push"):
            with self.subTest(operation=operation):
                if self.log.exists(): self.log.unlink()
                result = self.run_script(FAIL_DOCKER=operation)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("<set>", self.calls())
                self.assertNotIn("curl", self.calls())
                self.assertNotIn("Deployment completed successfully", result.stdout)

    def test_kubernetes_failures_stop_health_check(self):
        for operation in ("set", "rollout"):
            with self.subTest(operation=operation):
                if self.log.exists(): self.log.unlink()
                result = self.run_script(FAIL_KUBECTL=operation)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("curl", self.calls())
                self.assertNotIn("Deployment completed successfully", result.stdout)

    def test_health_command_failure_or_unhealthy_status_fails_deployment(self):
        for override in [dict(FAIL_CURL="1"), dict(HTTP_STATUS="503"), dict(HTTP_STATUS="302")]:
            with self.subTest(override=override):
                result = self.run_script(**override)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Deployment completed successfully", result.stdout)

    def test_build_context_is_passed_as_one_argument(self):
        path = self.root / "context with spaces"
        path.mkdir()
        (path / "Dockerfile").write_text("FROM scratch\n")
        result = self.run_script(BUILD_CONTEXT=str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("<" + str(path) + ">", self.calls())


if __name__ == "__main__":
    unittest.main()
