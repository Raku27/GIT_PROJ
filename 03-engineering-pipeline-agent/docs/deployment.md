# Deployment script

`scripts/deploy.sh` is a real deployment script, separate from the Python orchestrator's simulated stage handlers. The orchestrator does not invoke it. Regression tests substitute fake `docker`, `kubectl` and `curl` commands; no live deployment has been validated.

## Required inputs

Run from a build directory containing a real `Dockerfile`, or supply `BUILD_CONTEXT`. The repository does not yet include a deployable application, Dockerfile or Kubernetes manifests for this project.

You must already have an authenticated Docker registry, an accessible Kubernetes context, and a Deployment in the selected namespace. The Deployment and its container must both use `APP_NAME`. The environment argument doubles as the namespace and must be `dev`, `staging` or `production`.

| Input | Meaning |
|---|---|
| First argument | Environment/namespace; defaults to `staging` |
| Second argument | Required explicit image tag |
| `APP_NAME` | Deployment and container name |
| `REGISTRY` | Registry plus optional repository prefix, e.g. `registry.example/team` |
| `KUBE_CONTEXT` | Explicit kubeconfig context; every Kubernetes command selects it |
| `HEALTH_URL` | Explicit HTTP(S) endpoint for the deployed service |
| `BUILD_CONTEXT` | Directory containing `Dockerfile`; defaults to current directory |
| `API_TIMEOUT_SECONDS` | Kubernetes per-request timeout, default 30 |
| `ROLLOUT_TIMEOUT_SECONDS` | Kubernetes rollout wait, default 120 |
| `HEALTH_TIMEOUT_SECONDS` | Maximum duration of the health request, default 15 |

Example **for a separately provisioned test application**, after setting the values for your own environment:

```bash
export APP_NAME=myapp
export REGISTRY=registry.example/team
export KUBE_CONTEXT=my-staging-cluster
export HEALTH_URL=https://myapp.staging.example/health
export BUILD_CONTEXT=/path/to/application
bash scripts/deploy.sh staging commit-abc123
```

This example is not runnable against this repository alone. Use a version-specific tag for traceability. Tags are not enforced as immutable and images are not pinned by digest.

## Success and failure behavior

1. Validate arguments, positive timeouts, Dockerfile and command availability before external commands.
2. Read the existing Deployment using the supplied context and namespace before building or pushing an image.
3. Build, tag and push; any failing command stops execution.
4. Update the Deployment image and wait for the rollout with a timeout.
5. Request `HEALTH_URL` with a 5-second connection timeout and the configured total request timeout. Require HTTP **200**; redirects, unhealthy responses, connection errors and timeouts fail verification.
6. Print success only after both rollout and health verification pass. Any failure returns a nonzero exit status.

Choose a health URL that reaches the intended deployed service; the script cannot establish that an arbitrary supplied URL belongs to the selected Deployment. No localhost endpoint is assumed, no TLS verification is disabled, and redirects are not followed.

A health or rollout failure can occur **after the cluster image was changed**. The script reports failure but does not automatically roll back. Docker build/push duration is not bounded by the rollout/health timeout settings. This is not a blue-green/canary deployer or a production release system.

## Manual checks without deploying

From `03-engineering-pipeline-agent`:

```bash
# Shell syntax only; executes no deployment commands.
bash -n scripts/deploy.sh

# Ten script tests using fake external commands.
python3 -B -m unittest discover -s tests -p test_deploy_script.py -v

# Complete pipeline regression suite.
python3 -B -m unittest discover -s tests -v
```

The script tests cover missing tools/configuration/Dockerfile, invalid arguments, target validation, failures during Docker build/tag/push, image update and rollout, unhealthy or timed-out health requests, command argument quoting and successful execution order. The timeout tests assert the timeout arguments and simulate a timeout failure; they do not establish real cluster/network behavior.
