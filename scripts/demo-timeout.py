#!/usr/bin/env python3
"""Execute a real sandbox timeout and verify its container is removed."""

import subprocess

from agent_runtime.models.domain import Capability, ResourceLimits, TaskRequest, TaskState
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService

service = TaskService(LocalContainerBackend())
task = service.submit(
    TaskRequest(
        tenant_id="team-a",
        agent_id="agent:timeout",
        idempotency_key="real-timeout-001",
        capabilities={Capability.PROCESS_EXECUTE, Capability.ARTIFACT_UPLOAD},
        command=["sh", "-lc", "sleep 10"],
        limits=ResourceLimits(timeout_seconds=1),
    )
)
done = service.run(str(task.id))
assert done.state is TaskState.DESTROYED
assert done.exit_code == 124
assert any(event.type == "TASK_TIMEOUT" for event in service.events[str(task.id)])
assert subprocess.run(
    ["docker", "container", "inspect", f"agent-runtime-{task.sandbox_id}"], capture_output=True
).returncode != 0
print("timeout demo passed: timed-out sandbox was destroyed")
