#!/usr/bin/env bash
set -euo pipefail
command -v kind >/dev/null || { echo 'install kind first'; exit 1; }
kind get clusters | grep -qx secure-agent-runtime-local || kind create cluster --name secure-agent-runtime-local
helm upgrade --install agent-runtime platform/helm/agent-runtime --namespace agent-runtime --create-namespace --set image.repository=nginx --set image.tag=1.27-alpine
kubectl get pods -n agent-runtime
