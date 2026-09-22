import os
import shutil
import subprocess

import pytest
from agent_runtime.models.domain import Capability, TaskRequest, TaskState
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DOCKER_INTEGRATION") != "1" or shutil.which("docker") is None,
    reason="requires RUN_DOCKER_INTEGRATION=1 and a local Docker daemon",
)


def test_hardened_container_clones_fixture_creates_patch_and_cleans_up():
    service = TaskService(LocalContainerBackend())
    task = service.submit(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:integration",
            idempotency_key="docker-integration-001",
            capabilities={
                Capability.FILESYSTEM_READ,
                Capability.FILESYSTEM_WRITE,
                Capability.PROCESS_EXECUTE,
                Capability.ARTIFACT_UPLOAD,
            },
            command=["sh", "-lc", "python -m unittest -q && printf '\\n# patch\\n' >> app.py"],
        )
    )

    done = service.run(str(task.id))
    evidence = next(
        event.details
        for event in service.events[str(task.id)]
        if event.type == "SANDBOX_HARDENING_VERIFIED"
    )
    names = {artifact.name for artifact in service.artifacts.list(task.id, "team-a")}

    assert done.state is TaskState.DESTROYED
    assert done.exit_code == 0
    assert names == {"logs.txt", "workspace.patch"}
    assert evidence["user"] == "65532:65532"
    assert evidence["read_only_rootfs"] == "true"
    assert evidence["cap_drop"] == "ALL"
    assert evidence["network_mode"] == "none"
    assert evidence["docker_socket_mounted"] == "false"
    assert evidence["host_bind_mounted"] == "false"
    assert (
        subprocess.run(
            ["docker", "container", "inspect", f"agent-runtime-{task.sandbox_id}"],
            capture_output=True,
            check=False,
        ).returncode
        != 0
    )
