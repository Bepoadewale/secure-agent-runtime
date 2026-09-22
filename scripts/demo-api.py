#!/usr/bin/env python3
"""Exercise the authenticated FastAPI → hardened Docker sandbox lifecycle."""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

from agent_runtime.auth.jwt import issue_local_token

ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:18080"
database = ROOT / ".local" / "api-demo.db"


def request(path: str, method: str = "GET", body: dict | None = None, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(body).encode() if body else None
    item = urllib.request.Request(f"{URL}{path}", data=payload, method=method, headers=headers)
    with urllib.request.urlopen(item, timeout=30) as response:
        return json.loads(response.read())


def wait_for_health():
    for _ in range(30):
        try:
            if request("/healthz")["status"] == "ok":
                return
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.25)
    raise RuntimeError("control-plane did not become healthy")


def start() -> subprocess.Popen:
    environment = os.environ | {"AGENT_RUNTIME_DB": str(database)}
    return subprocess.Popen(
        [".venv/bin/python", "-m", "uvicorn", "agent_runtime.api.main:app", "--port", "18080"],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop(process: subprocess.Popen):
    process.terminate()
    process.wait(timeout=10)


database.parent.mkdir(exist_ok=True)
database.unlink(missing_ok=True)
token = issue_local_token("team-a", "agent:api-demo", ["task.submit"], "agent")
process = start()
try:
    wait_for_health()
    created = request(
        "/api/v1/tasks",
        "POST",
        {
            "tenant_id": "team-a",
            "agent_id": "agent:api-demo",
            "idempotency_key": f"api-demo-{uuid4()}",
            "capabilities": ["filesystem.read", "filesystem.write", "process.execute", "artifact.upload"],
            "command": ["sh", "-lc", "python -m unittest -q && printf '\\n# api patch\\n' >> app.py"],
        },
        token,
    )
    task_id = created["id"]
    finished = request(f"/api/v1/tasks/{task_id}/run", "POST", token=token)
    assert finished["state"] == "DESTROYED"
    artifacts = request(f"/api/v1/tasks/{task_id}/artifacts", token=token)
    assert {artifact["name"] for artifact in artifacts} == {"logs.txt", "workspace.patch"}
    events = request(f"/api/v1/tasks/{task_id}/events", token=token)
    assert any(event["type"] == "SANDBOX_HARDENING_VERIFIED" for event in events)
finally:
    stop(process)

process = start()
try:
    wait_for_health()
    restored = request(f"/api/v1/tasks/{task_id}", token=token)
    assert restored["state"] == "DESTROYED"
finally:
    stop(process)

print(f"API lifecycle demo passed for task {task_id}; durable restart recovery verified")
