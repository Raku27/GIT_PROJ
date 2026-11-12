#!/bin/bash

# Deploy an existing Kubernetes Deployment and verify its explicitly supplied health URL.
set -euo pipefail

STEP="configuration"
trap 'printf "Deployment failed during %s.\n" "$STEP" >&2' ERR

die() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-}
APP_NAME=${APP_NAME:-}
REGISTRY=${REGISTRY:-}
KUBE_CONTEXT=${KUBE_CONTEXT:-}
HEALTH_URL=${HEALTH_URL:-}
BUILD_CONTEXT=${BUILD_CONTEXT:-.}
ROLLOUT_TIMEOUT_SECONDS=${ROLLOUT_TIMEOUT_SECONDS:-120}
API_TIMEOUT_SECONDS=${API_TIMEOUT_SECONDS:-30}
HEALTH_TIMEOUT_SECONDS=${HEALTH_TIMEOUT_SECONDS:-15}

[[ "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]] || die "Invalid environment: use dev, staging, or production"
[[ "$IMAGE_TAG" =~ ^[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}$ ]] || die "Supply an explicit valid image tag as argument 2"
[[ "$APP_NAME" =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ && ${#APP_NAME} -le 63 ]] || die "APP_NAME must be a Kubernetes name of at most 63 characters"
[[ "$REGISTRY" =~ ^[a-zA-Z0-9][a-zA-Z0-9._:/-]*$ ]] || die "REGISTRY must be a registry/image-prefix without whitespace"
[[ -n "$KUBE_CONTEXT" ]] || die "KUBE_CONTEXT must explicitly select a cluster context"
[[ "$HEALTH_URL" =~ ^https?://[^[:space:]]+$ ]] || die "HEALTH_URL must explicitly identify the deployed service over HTTP(S)"
for timeout in "$ROLLOUT_TIMEOUT_SECONDS" "$API_TIMEOUT_SECONDS" "$HEALTH_TIMEOUT_SECONDS"; do
    [[ "$timeout" =~ ^[1-9][0-9]{0,4}$ ]] || die "Timeouts must be positive integers of at most five digits"
done
[[ -f "$BUILD_CONTEXT/Dockerfile" ]] || die "Dockerfile not found in BUILD_CONTEXT"
for tool in docker kubectl curl; do
    command -v "$tool" >/dev/null 2>&1 || die "Required tool not found: $tool"
done

IMAGE="${REGISTRY}/${APP_NAME}:${IMAGE_TAG}"
LOCAL_IMAGE="${APP_NAME}:${IMAGE_TAG}"

# Validate the intended context, namespace and existing deployment before publishing an image.
STEP="target validation"
kubectl --context "$KUBE_CONTEXT" --request-timeout="${API_TIMEOUT_SECONDS}s" \
    get deployment "$APP_NAME" --namespace "$ENVIRONMENT" -o name >/dev/null

STEP="image build"
docker build -t "$LOCAL_IMAGE" "$BUILD_CONTEXT"
STEP="image tagging"
docker tag "$LOCAL_IMAGE" "$IMAGE"
STEP="image push"
docker push "$IMAGE"

STEP="deployment update"
kubectl --context "$KUBE_CONTEXT" --request-timeout="${API_TIMEOUT_SECONDS}s" \
    set image "deployment/$APP_NAME" "$APP_NAME=$IMAGE" --namespace "$ENVIRONMENT"
STEP="rollout verification"
kubectl --context "$KUBE_CONTEXT" --request-timeout="${API_TIMEOUT_SECONDS}s" \
    rollout status "deployment/$APP_NAME" --namespace "$ENVIRONMENT" \
    --timeout="${ROLLOUT_TIMEOUT_SECONDS}s"

STEP="health verification"
if ! HTTP_STATUS=$(curl --fail --silent --show-error --connect-timeout 5 \
    --max-time "$HEALTH_TIMEOUT_SECONDS" --output /dev/null --write-out '%{http_code}' "$HEALTH_URL"); then
    die "Health request failed or timed out; deployment is not verified"
fi
[[ "$HTTP_STATUS" == "200" ]] || die "Health endpoint returned HTTP $HTTP_STATUS; expected 200"

printf 'Deployment completed successfully: %s in %s.\n' "$APP_NAME" "$ENVIRONMENT"
