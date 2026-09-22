#!/usr/bin/env python3
"""Cancel an active hardened task and verify Docker cleanup occurs."""

import subprocess
import threading
import time

from agent_runtime.models.domain import Capability, ResourceLimits, TaskRequest, TaskState
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService

service = TaskService(LocalContainerBackend())
task = service.submit(
    TaskRequest(
        tenant_id="team-a",
        agent_id="agent:cancel",
        idempotency_key="real-cancel-001",
        capabilities={Capability.PROCESS_EXECUTE, Capability.ARTIFACT_UPLOAD},
        command=["sh", "-lc", "sleep 20"],
        limits=ResourceLimits(timeout_seconds=30),
    )
)
worker = threading.Thread(target=service.run, args=(str(task.id),), daemon=True)
worker.start()
for _ in range(100):
    if task.state is TaskState.RUNNING and task.sandbox_id:
        break
    time.sleep(0.1)
else:
    raise RuntimeError("sandbox did not reach RUNNING")

service.cancel(str(task.id), "user:operator")
worker.join(timeout=10)
assert not worker.is_alive()
assert task.state is TaskState.DESTROYED
event_types = {event.type for event in service.events[str(task.id)]}
assert {"TASK_CANCELLED", "SANDBOX_CANCEL_REQUESTED", "SANDBOX_DESTROYED"} <= event_types
assert subprocess.run(
    ["docker", "container", "inspect", f"agent-runtime-{task.sandbox_id}"], capture_output=True
).returncode != 0
print("cancel demo passed: active sandbox was cancelled and destroyed")
