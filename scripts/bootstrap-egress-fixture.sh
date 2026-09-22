#!/usr/bin/env bash
set -euo pipefail

network=agent-runtime-local-allow
fixture=agent-runtime-local-egress-fixture

docker network inspect "${network}" >/dev/null 2>&1 || docker network create --label agent-runtime.managed=true --internal "${network}" >/dev/null
if ! docker container inspect "${fixture}" >/dev/null 2>&1; then
  docker run -d --name "${fixture}" --label agent-runtime.managed=true --network "${network}" --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=16m --cap-drop ALL --security-opt no-new-privileges \
    --user 65532:65532 python:3.12-alpine python -m http.server 8080 >/dev/null
fi
echo "Local egress fixture is ready on ${network}; it has no host port and the network is internal."
