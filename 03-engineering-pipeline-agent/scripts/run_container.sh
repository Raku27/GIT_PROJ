#!/bin/bash
# Build and run the bundled Matching workflow; leave reports on the host.
set -euo pipefail

command -v docker >/dev/null 2>&1 || { echo "Docker is required" >&2; exit 2; }
REPOSITORY_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
RUNNER_IMAGE=${RUNNER_IMAGE:-git-proj-runner:local}
RUNNER_REPORTS_DIR=${RUNNER_REPORTS_DIR:-$REPOSITORY_ROOT/.pipeline-runs}

mkdir -p -- "$RUNNER_REPORTS_DIR"
# Normalize the path for Docker's bind mount; quoted values preserve spaces.
RUNNER_REPORTS_DIR=$(cd -- "$RUNNER_REPORTS_DIR" && pwd)
[[ "$RUNNER_REPORTS_DIR" != *,* ]] || { echo "Report paths containing commas are not supported" >&2; exit 2; }
printf 'Host reports: %s\n' "$RUNNER_REPORTS_DIR"
docker build --target matching -f "$REPOSITORY_ROOT/03-engineering-pipeline-agent/docker/Dockerfile" \
    -t "$RUNNER_IMAGE" "$REPOSITORY_ROOT"

exec docker run --rm --init --user "$(id -u):$(id -g)" \
    --read-only --network none --cap-drop ALL --security-opt no-new-privileges \
    --memory 1g --cpus 2 --pids-limit 128 \
    --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m \
    --mount "type=bind,src=$RUNNER_REPORTS_DIR,dst=/reports" \
    "$RUNNER_IMAGE" --config /workspace/03-engineering-pipeline-agent/configs/matching.json "$@"
