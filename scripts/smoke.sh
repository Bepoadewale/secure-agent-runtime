#!/usr/bin/env bash
set -euo pipefail

cluster=secure-agent-runtime-local
namespace=agent-runtime

command -v kind >/dev/null || { echo 'kind is required; run make bootstrap-local first'; exit 1; }
command -v kubectl >/dev/null || { echo 'kubectl is required; run make bootstrap-local first'; exit 1; }
kind get clusters | grep -qx "$cluster" || { echo "kind cluster $cluster is not running"; exit 1; }
kubectl rollout status deployment/agent-runtime-control-plane -n "$namespace" --timeout=30s
kubectl get service agent-runtime-control-plane -n "$namespace" >/dev/null

kubectl port-forward -n "$namespace" service/agent-runtime-control-plane 18081:8000 >/tmp/secure-agent-runtime-port-forward.log 2>&1 &
port_forward=$!
cleanup() { kill "$port_forward" 2>/dev/null || true; wait "$port_forward" 2>/dev/null || true; }
trap cleanup EXIT

for _ in $(seq 1 20); do
  if curl -fsS --max-time 2 http://127.0.0.1:18081/healthz >/tmp/secure-agent-runtime-health.json 2>/dev/null; then
    cat /tmp/secure-agent-runtime-health.json
    exit 0
  fi
  sleep 1
done

echo 'control-plane health endpoint did not become ready' >&2
exit 1
