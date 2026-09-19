from agent_runtime.models.domain import TaskRequest, TaskState
from agent_runtime.sandboxes.backend import ExecutionResult
from agent_runtime.sandboxes.fake import FakeBackend
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
