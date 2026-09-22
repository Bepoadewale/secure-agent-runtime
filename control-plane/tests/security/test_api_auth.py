from agent_runtime.api import main
from agent_runtime.auth.jwt import issue_local_token
from agent_runtime.sandboxes.fake import FakeBackend
from agent_runtime.tasks.service import TaskService
from fastapi.testclient import TestClient


def payload(tenant_id="team-a", agent_id="agent:api"):
    return {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "idempotency_key": "api-boundary-001",
        "capabilities": ["process.execute", "artifact.upload"],
        "command": ["true"],
    }


def client(monkeypatch):
    monkeypatch.setattr(main, "service", TaskService(FakeBackend()))
    return TestClient(main.app)


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signed_agent_identity_can_submit_its_own_task(monkeypatch):
    result = client(monkeypatch).post(
        "/api/v1/tasks",
        json=payload(),
        headers=headers(issue_local_token("team-a", "agent:api", ["task.submit"], "agent")),
    )
    assert result.status_code == 202
    assert result.json()["state"] == "QUEUED"


def test_agent_cannot_impersonate_another_agent(monkeypatch):
    result = client(monkeypatch).post(
        "/api/v1/tasks",
        json=payload(agent_id="agent:other"),
        headers=headers(issue_local_token("team-a", "agent:api", ["task.submit"], "agent")),
    )
    assert result.status_code == 403


def test_tenant_cannot_submit_for_another_tenant(monkeypatch):
    result = client(monkeypatch).post(
        "/api/v1/tasks",
        json=payload(tenant_id="team-b"),
        headers=headers(issue_local_token("team-a", "user:alice", ["task.submit"])),
    )
    assert result.status_code == 403


def test_unsigned_token_is_rejected(monkeypatch):
    result = client(monkeypatch).post("/api/v1/tasks", json=payload(), headers=headers("not-a-jwt"))
    assert result.status_code == 401
