#!/usr/bin/env python3
"""Generate a real task metric and OTLP trace against the local observability stack."""

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import uuid4

from agent_runtime.auth.jwt import issue_local_token

ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:18080"


def call(url: str, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url, data=json.dumps(body).encode() if body else None, method=method, headers=headers
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def wait(label, predicate):
    for _ in range(30):
        try:
            value = predicate()
            if value:
                return value
        except (urllib.error.URLError, urllib.error.HTTPError, ConnectionError):
            pass
        time.sleep(1)
    raise RuntimeError(f"{label} did not become observable")


database = ROOT / ".local" / "observability-demo.db"
database.parent.mkdir(exist_ok=True)
database.unlink(missing_ok=True)
environment = os.environ | {
    "AGENT_RUNTIME_DB": str(database),
    "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT": "http://127.0.0.1:4318/v1/traces",
}
process = subprocess.Popen(
    [".venv/bin/python", "-m", "uvicorn", "agent_runtime.api.main:app", "--port", "18080"],
    cwd=ROOT,
    env=environment,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
token = issue_local_token("team-a", "agent:observability", ["task.submit"], "agent")
try:
    wait("control-plane", lambda: call(f"{URL}/healthz").get("status") == "ok")
    created = call(
        f"{URL}/api/v1/tasks",
        "POST",
        {
            "tenant_id": "team-a",
            "agent_id": "agent:observability",
            "idempotency_key": f"observability-{uuid4()}",
            "capabilities": ["process.execute", "artifact.upload"],
            "command": ["python", "-c", "print('observability task')"],
        },
        token,
    )
    completed = call(f"{URL}/api/v1/tasks/{created['id']}/run", "POST", token=token)
    assert completed["state"] == "DESTROYED"
    metric = wait(
        "Prometheus task metric",
        lambda: call(
            "http://127.0.0.1:9090/api/v1/query?" + urllib.parse.urlencode({"query": "agent_runtime_tasks_total"})
        ).get("data", {}).get("result"),
    )
    traces = wait(
        "Jaeger sandbox.execute trace",
        lambda: call("http://127.0.0.1:16686/api/traces?service=secure-agent-runtime")
        .get("data"),
    )
    print(f"observability demo passed: Prometheus series={len(metric)} Jaeger traces={len(traces)}")
finally:
    process.terminate()
    process.wait(timeout=10)
