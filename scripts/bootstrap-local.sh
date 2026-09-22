#!/usr/bin/env bash
set -euo pipefail
command -v kind >/dev/null || { echo 'install kind first'; exit 1; }
command -v helm >/dev/null || { echo 'install helm first'; exit 1; }
command -v kubectl >/dev/null || { echo 'install kubectl first'; exit 1; }
kind get clusters | grep -qx secure-agent-runtime-local || kind create cluster --name secure-agent-runtime-local
docker build -t secure-agent-runtime:local -f control-plane/Dockerfile .
kind load docker-image secure-agent-runtime:local --name secure-agent-runtime-local
helm upgrade --install agent-runtime platform/helm/agent-runtime --namespace agent-runtime --create-namespace
kubectl rollout status deployment/agent-runtime-control-plane -n agent-runtime --timeout=90s
kubectl get pods,svc -n agent-runtime
