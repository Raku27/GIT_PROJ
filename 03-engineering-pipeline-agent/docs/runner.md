# Runner configuration and execution

Run the entry point from your repository root. `--workspace` defaults to the current directory. `--config` is a path to a trusted JSON file. The runner needs no packages beyond Python's standard library; commands need their own project dependencies installed.

## Configuration

```json
{
  "version": 1,
  "name": "my-project",
  "project_dir": "my-project-folder",
  "fail_fast": false,
  "stages": [
    {
      "name": "tests",
      "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"],
      "timeout_seconds": 120
    },
    {
      "name": "independent-check",
      "argv": ["{python}", "-c", "print('independent check')"],
      "needs": [],
      "timeout_seconds": 10
    },
    {
      "name": "verify",
      "argv": ["{python}", "-c", "print('checks passed')"],
      "needs": ["tests", "independent-check"]
    }
  ]
}
```

| Field | Rule |
|---|---|
| `version` | Required integer `1` |
| `name` | Required pipeline identifier: 1–64 letters, numbers, hyphens or underscores; first character alphanumeric |
| `project_dir` | Required existing workspace-relative directory, resolved from `--workspace`, not from the config file |
| `fail_fast` | Optional boolean, default `true` |
| `stages` | Required ordered list of 1–50 stages |
| Stage `name` | Unique identifier, same rules as pipeline name |
| Stage `argv` | 1–100 nonempty string arguments; maximum 4096 characters per argument, no NUL |
| Stage `needs` | Unique names of earlier stages; omitted means depend on the preceding stage; `[]` means independent |
| Stage `timeout_seconds` | Number greater than 0 and at most 3600; default 120 |

Unknown fields, duplicate stage names, forward/cyclic/self dependencies, absolute/outside-workspace project folders and configurations exceeding 64 KiB are rejected. Symlinks in project paths are resolved before validation. Use `--dry-run` to validate and print the resolved plan without running commands or creating reports.

`{python}` as an entire argument resolves to the interpreter used to invoke the runner. `{run_dir}` inside an argument resolves to the unique report directory, useful for command artifacts such as `{run_dir}/benchmark.json`. Variables and shell expressions are not expanded. There is no implicit shell; if a trusted project explicitly invokes a shell or script, that code runs with normal account permissions.

## Dependency and failure behavior

Stages execute one at a time in configuration order. Every named prerequisite must have succeeded. Blocked stages are skipped and never launch a process. With `fail_fast=true`, any failed stage skips all remaining stages. With `false`, independent stages can continue, but failed/skipped prerequisites still block their descendants. A workflow with a failed stage returns failure even when independent stages pass.

Commands receive no interactive stdin. Nonzero exits, signal termination, missing executables and timeouts fail the stage. Timeouts cover process startup and command execution, with a short bounded drain/cleanup period afterward. Ctrl+C or SIGTERM during a command triggers process-group cleanup, a failed/interrupted report and exit 130.

The runner kills remaining members of a command's POSIX process group when its parent exits or reaches its deadline. It is designed for finite commands, not background services or interactive servers. Programs that deliberately detach into another session are outside this cleanup guarantee. Use separate processes/runner instances for concurrent workflows; scheduling within one workflow is sequential.

## Reports and logs

`--output-dir` defaults to `WORKSPACE/.pipeline-runs`. Every invocation creates a new directory; reports from earlier runs are preserved. `report.json` is atomically replaced as execution progresses and after completion. It includes the pipeline name, project directory, timestamps, overall status, stage arguments/dependencies, return codes, durations, error descriptions and command log paths.

stdout/stderr are saved separately, capped at 1 MiB per stream per stage. Extra output is drained so a command cannot deadlock on a full pipe; the report sets `logs_truncated=true`. Commands can still write other files and consume other resources: log caps are not disk, CPU or memory isolation. Output is binary-safe; use an appropriate encoding when reading logs.

Reports are not a resumable queue. An uncatchable process termination, host crash or report-storage failure can leave a report with the last running/pending state. Normal command failures are recorded; initial configuration/storage errors return 2. Protect and expire local reports as appropriate: the runner does not redact secrets from arguments or command output, and local history is not automatically pruned.

## Matching API integration

`configs/matching.json` runs seven stages: dependency consistency, the pytest suite, lint, format check, the candidate/job example, the algorithm tradeoff example, and a tiny benchmark smoke run. Tests depend on dependency consistency; lint/format are independent; the examples require the checks to succeed. The benchmark writes its artifact inside its own run directory.

The Matching GitHub workflow installs that project's locked environment, invokes this common configuration, and uploads `.pipeline-runs` as the `matching-runner-report` artifact even on failure. This is a CI integration and local demonstration, not a deployment.

`configs/pipeline-agent.json` uses the same runner to run this project's standard-library tests and Bash syntax check. Add new projects with new configurations; no runner source change is needed for another set of finite commands.
