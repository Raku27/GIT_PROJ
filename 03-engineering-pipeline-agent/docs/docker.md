# Run the common runner in Docker

Docker support packages **batch workflows**, not a hosted API or cloud deployment. The bundled image contains the common runner, both public project folders, and the Matching API's locked Python dependencies. A smaller `runner` build target contains only the common runner for use with other mounted workspaces.

## One-command Matching workflow

With Docker running, from the GIT_PROJ repository root:

```bash
bash 03-engineering-pipeline-agent/scripts/run_container.sh
```

This builds the `matching` target as `git-proj-runner:local`, then runs all seven Matching workflow stages. The first build needs internet access to download the official Python image and pinned packages. Later builds reuse cached layers. Execution itself has networking disabled.

Expected stages: dependencies, tests, lint, format, example, tradeoff and benchmark-smoke. The test log contains the 46-test Matching suite. A successful run exits 0; build or workflow failures propagate a nonzero exit code.

The launcher prints the **host report directory** before building. Reports and logs survive container removal under:

```text
GIT_PROJ/.pipeline-runs/<pipeline-name>-<unique-id>/report.json
```

Inside a report, `/reports/...` refers to this mounted host directory. stdout/stderr paths are relative to that run's folder. Inspect the host files even though the container has been removed.

Useful variants:

```bash
# Validate the bundled Matching configuration without running its commands.
bash 03-engineering-pipeline-agent/scripts/run_container.sh --dry-run

# Run the runner project's regression suite inside the same image.
bash 03-engineering-pipeline-agent/scripts/run_container.sh \
  --config /workspace/03-engineering-pipeline-agent/configs/pipeline-agent.json

# Choose a different image tag or host report directory.
RUNNER_IMAGE=my-runner:local RUNNER_REPORTS_DIR="$PWD/my-reports" \
  bash 03-engineering-pipeline-agent/scripts/run_container.sh
```

Additional arguments are passed to the runner; explicit options override its defaults. Report paths containing commas are rejected because Docker's mount syntax uses commas as separators. Choose a separate report directory if desired and keep private command output out of source control.

## Container behavior

- Official Python 3.13.18 base, pinned by multi-platform image digest. Update the digest deliberately when refreshing the base image.
- The image defaults to UID/GID `10001:10001`. The launcher overrides this with the invoking host user's UID/GID so bind-mounted reports remain writable/readable by that user. Run the launcher as your normal Docker-enabled account.
- Read-only root filesystem; only `/reports` and a 256 MiB temporary `/tmp` are writable.
- Coverage, pytest and Ruff caches use `/tmp`; source is never mounted writable by this launcher.
- No runtime networking, no published ports, all Linux capabilities dropped, no privilege escalation, an init process for signal forwarding/reaping, 1 GiB memory, two CPUs and a 128-process limit.
- Numerical-library threads are capped at one to avoid oversubscription during checks. This is a verification environment, not a performance benchmark environment.
- No host Docker socket, kubeconfig, cloud credentials or arbitrary host environment variables are mounted/passed by the launcher.

The Docker build context allows only the two relevant public project folders and excludes Git metadata, `.env` files, local environments, caches and run logs. The image copies a snapshot of that source; rerun the launcher to rebuild after editing.

## Generic runner for another workspace

Build the dependency-free runner target:

```bash
docker build --target runner \
  -f 03-engineering-pipeline-agent/docker/Dockerfile \
  -t git-proj-runner:base .
```

For an existing project with a reviewed `pipeline.json`, mount its workspace read-only and a writable report directory:

```bash
mkdir -p .pipeline-runs
docker run --rm --init --user "$(id -u):$(id -g)" \
  --read-only --network none --cap-drop ALL --security-opt no-new-privileges \
  --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m \
  --mount "type=bind,src=/absolute/path/to/project,dst=/workspace,readonly" \
  --mount "type=bind,src=$PWD/.pipeline-runs,dst=/reports" \
  git-proj-runner:base --config /workspace/pipeline.json
```

Set `project_dir` to `.` when the mount is the project root. The runner entry point is in `/opt/project-runner`, so mounting another workspace does not hide it. This target has only the standard library; project-specific dependencies must be installed in a derived image. Adjust writable paths/networking deliberately for workflows that need them. See [configuration rules](runner.md).

## Verification and CI

`Common runner Docker` in GitHub Actions builds and runs the Matching workflow, runs the runner regression suite inside the bundled image, and tests the generic image against an external workspace. The generic checks verify success, failed-command dependency blocking, timeout handling, default image user and reports/logs persisted on the host. Download **docker-runner-reports** from that workflow's artifacts; retention is seven days.

To run the generic checks locally after building the base target:

```bash
python3 03-engineering-pipeline-agent/docker/smoke_test.py --image git-proj-runner:base
```

These explicitly launch real local Docker containers. Standard-library unit tests instead use a fake Docker executable to test launcher arguments and exit-code propagation. No cloud deployment or image publication occurs.

The local build is verified on Linux/ARM64 through Docker Desktop on macOS; CI verifies Linux/AMD64. Native Windows launch support, registry publishing, Compose service orchestration and hosting are separate future work.
