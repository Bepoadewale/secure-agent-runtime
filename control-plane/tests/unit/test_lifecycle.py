from agent_runtime.models.domain import TaskRequest, TaskState
from agent_runtime.sandboxes.backend import ExecutionResult
from agent_runtime.sandboxes.fake import FakeBackend
from agent_runtime.state.store import RuntimeStateStore
from agent_runtime.tasks.service import TaskService


def request(**kwargs):
    return TaskRequest(
        tenant_id="team-a",
        agent_id="agent:demo",
        idempotency_key="request-key-123",
        command=["pytest"],
        **kwargs,
    )


def test_task_executes_extracts_artifact_and_destroys():
    service = TaskService(FakeBackend())
    task = service.submit(request())
    assert task.state is TaskState.QUEUED
    done = service.run(str(task.id))
    assert done.state is TaskState.DESTROYED
    assert service.artifacts.list(task.id, "team-a")
    assert any(e.type == "SANDBOX_DESTROYED" for e in service.events[str(task.id)])


def test_idempotency_returns_same_task():
    service = TaskService(FakeBackend())
    assert service.submit(request()).id == service.submit(request()).id


def test_timeout_revokes_and_destroys():
    service = TaskService(FakeBackend(ExecutionResult(124, "", "", True)))
    done = service.run(str(service.submit(request()).id))
    assert done.state is TaskState.DESTROYED
    assert any(e.type == "TASK_TIMEOUT" for e in service.events[str(done.id)])


def test_task_audit_and_artifacts_survive_control_plane_restart(tmp_path):
    database = str(tmp_path / "runtime.db")
    service = TaskService(FakeBackend(), RuntimeStateStore(database))
    done = service.run(str(service.submit(request()).id))

    restarted = TaskService(FakeBackend(), RuntimeStateStore(database))

    restored = restarted.tasks[str(done.id)]
    assert restored.state is TaskState.DESTROYED
    assert any(event.type == "SANDBOX_DESTROYED" for event in restarted.events[str(done.id)])
    assert {artifact.name for artifact in restarted.artifacts.list(done.id, "team-a")} == {"logs.txt"}
