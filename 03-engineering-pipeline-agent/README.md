# Common Project Runner

A configuration-driven Python runner for finite project commands. It runs real processes, checks their exit codes, enforces timeouts, saves logs and blocks dependent stages after failure.

The first integrated project is the [Matching API](../02-matching-project). Its GitHub workflow now uses this runner for dependency checks, tests, lint, formatting, examples and a benchmark smoke run. A second configuration runs this project's own regression suite and shell syntax check.

## Run the Matching API workflow

From the **GIT_PROJ repository root**, create a Python 3.13 environment and install the Matching API's locked dependencies:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r 02-matching-project/requirements-lock.txt

# Validate and inspect commands without running them.
python 03-engineering-pipeline-agent/run_pipeline.py \
  --config 03-engineering-pipeline-agent/configs/matching.json \
  --workspace . --dry-run

# Execute the configured workflow.
python 03-engineering-pipeline-agent/run_pipeline.py \
  --config 03-engineering-pipeline-agent/configs/matching.json \
  --workspace .
```

Expected: seven successful stages and a path to a new `report.json`. The Matching API test log contains 46 passing tests. Missing dependencies cause a real failure; the runner does not install packages automatically.

Run this project's checks through the same entry point:

```bash
python 03-engineering-pipeline-agent/run_pipeline.py \
  --config 03-engineering-pipeline-agent/configs/pipeline-agent.json \
  --workspace .
```

The runner itself uses only the Python standard library and is tested on Python 3.8 and 3.13, Linux and local macOS. The Matching API target requires Python 3.13. Windows execution is not supported yet.

## What works

- JSON project configurations with validated paths, arguments, dependencies and timeouts.
- Real commands executed as argument arrays, without an implicit shell.
- Sequential scheduling with explicit dependencies; independent checks may continue after a failure.
- Timeout and cancellation cleanup of the command's POSIX process group.
- Unique report directories and fresh results for every run.
- Separate stdout/stderr logs capped at 1 MiB each per stage; excess output is drained and discarded.
- Atomic JSON reports updated as stages finish, with exit codes, durations and failure reasons.
- Dry-run validation, meaningful command-line exit codes and downloadable CI report artifacts.

This is a local/CI runner. Docker packaging, managed environments, deployment orchestration, parallel scheduling, automatic merging, AI decision-making and a hosted service are not implemented. The learning walkthrough is separate from this implementation and will follow later.

## Add another project

Create a configuration following [the configuration guide](docs/runner.md). Set its workspace-relative project folder, commands and dependencies. Install that project's dependencies in an appropriate environment, then invoke the common runner with that configuration.

Configurations execute code with your account's permissions. Run only reviewed, trusted configurations and project code. Workspace-path validation and argument arrays do not isolate commands from your computer or network. Commands inherit the invoking environment; the runner does not collect it in reports. Arguments and command output are recorded, so do not put credentials in arguments or allow commands to print secrets.

## Inspect a run

The terminal prints the report path under `.pipeline-runs/<name>-<unique-id>/`. Open `report.json` to see stage statuses, executed argument arrays, return codes, dependencies, timings and relative log paths. Logs and reports are ignored by Git.

On GitHub, open **Actions → Matching service tests → the run → Artifacts → matching-runner-report**. The artifact contains the same report, command logs and benchmark smoke output. CI retains it for seven days.

Exit codes: **0** success, **1** workflow failure, **2** invalid configuration or setup/report error, **130** interrupted execution. A truncated log is explicitly marked in the report and does not itself make the command fail.

## Verify the runner

From `03-engineering-pipeline-agent`:

```bash
python3 -B -m unittest discover -s tests -v
bash -n scripts/deploy.sh
```

Tests cover real process execution, command failures, missing executables, deadlines, process-group cleanup, literal arguments, bounded output, dependencies, dry runs, malformed configurations and run isolation. Existing simulator and deployment-script regression tests remain included.

## Legacy simulator and deployment script

`agents/orchestrator_agent.py` and `example_usage.py` retain the original eight-stage **simulation** for regression coverage. Its hardcoded test report contains two failures; the example intentionally stops and returns status 1. The new runner in `runner/` executes commands and does not use those simulated results.

`scripts/deploy.sh` is a separate real Docker/Kubernetes helper requiring an application Dockerfile, an existing Kubernetes Deployment, registry access and explicit target settings. It is not invoked by the supplied configurations. See [deployment requirements and safe checks](docs/deployment.md). No live deployment has been validated.

The older YAML files in `pipelines/` are illustrative templates, not executable runner configurations. JSON is the supported format for the common runner.

## Layout

```text
runner/                     Config validation, process execution, reports and CLI
run_pipeline.py             Repository-root-friendly entry point
configs/matching.json       Real Matching API workflow
configs/pipeline-agent.json This project's regression workflow
agents/                     Legacy simulation
scripts/deploy.sh           Separate deployment helper
tests/                      Runner, simulator and deployment-script tests
docs/                       Configuration and deployment guides
```

[MIT license](../LICENSE) · [Contributing](../CONTRIBUTING.md) · [Rahul Kumaar Subramani](https://github.com/Raku27)
