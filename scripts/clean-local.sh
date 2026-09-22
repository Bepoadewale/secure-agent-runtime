#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

docker compose -f "${repo_root}/docker-compose.observability.yml" down -v --remove-orphans >/dev/null 2>&1 || true
docker rm -f agent-runtime-local-egress-fixture >/dev/null 2>&1 || true
containers=$(docker ps -aq --filter 'label=agent-runtime.managed=true')
if [[ -n "${containers}" ]]; then
  docker rm -f ${containers} >/dev/null
fi
volumes=$(docker volume ls -q --filter 'label=agent-runtime.managed=true')
if [[ -n "${volumes}" ]]; then
  docker volume rm -f ${volumes} >/dev/null
fi
docker network rm agent-runtime-local-allow >/dev/null 2>&1 || true
kind delete cluster --name secure-agent-runtime-local >/dev/null 2>&1 || true
rm -rf "${repo_root}/.venv" "${repo_root}/.local"
echo 'Removed only Secure Agent Runtime containers, workspace volumes, local egress network, kind cluster, and generated artifacts.'
