import pytest
from agent_runtime.models.domain import Capability, TaskRequest, TaskState
from agent_runtime.sandboxes.fake import FakeBackend
from agent_runtime.tasks.service import TaskService


def req(**kwargs):
    return TaskRequest(
        tenant_id="team-a",
        agent_id="agent:untrusted",
        idempotency_key="security-key-123",
        command=["true"],
        **kwargs,
    )


@pytest.mark.parametrize(
    "capability", [Capability.GIT_PUSH, Capability.SECRET_TEST_EPHEMERAL, Capability.NETWORK_PYPI]
)
def test_capabilities_not_in_restricted_profile_are_denied(capability):
    assert (
        TaskService(FakeBackend()).submit(req(capabilities={capability})).state
        is TaskState.REJECTED
    )


def test_untrusted_repository_cannot_downgrade_isolation():
    assert (
        TaskService(FakeBackend()).submit(req(workspace="malicious-repo")).state
        is TaskState.REJECTED
    )


def test_secret_values_are_redacted():
    service = TaskService(FakeBackend())
    task = service.submit(
        req(
            capabilities={Capability.PROCESS_EXECUTE, Capability.SECRET_TEST_EPHEMERAL},
            secret_requests=["test-api-token"],
        )
    )
    done = service.run(str(task.id))
    assert "demo-task" not in done.stdout + done.stderr
