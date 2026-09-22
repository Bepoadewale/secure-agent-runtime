#!/usr/bin/env python3
"""Demonstrate project-scoped recovery of an abandoned sandbox resource."""

import subprocess
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from agent_runtime.models.domain import Capability, ResourceLimits, Sandbox, TaskRequest
from agent_runtime.sandboxes.local_docker import LocalContainerBackend

backend = LocalContainerBackend()
task_id = uuid4()
sandbox = Sandbox(
    task_id=task_id,
    tenant_id="team-a",
    runtime_class="runc-standard",
    expires_at=datetime.now(UTC) + timedelta(minutes=5),
)
request = TaskRequest(
    tenant_id="team-a",
    agent_id="agent:recovery",
    idempotency_key="recovery-demo-001",
    capabilities={
        Capability.FILESYSTEM_READ,
        Capability.FILESYSTEM_WRITE,
        Capability.PROCESS_EXECUTE,
        Capability.ARTIFACT_UPLOAD,
    },
    command=["sh", "-lc", "sleep 30"],
    limits=ResourceLimits(timeout_seconds=30),
)

backend.create(sandbox, request, {})
name = f"agent-runtime-{sandbox.id}"
assert subprocess.run(["docker", "container", "inspect", name], capture_output=True).returncode == 0
result = backend.reap_orphans()
assert result == {"containers": 1, "volumes": 1}
assert subprocess.run(["docker", "container", "inspect", name], capture_output=True).returncode != 0
print("recovery demo passed", result)
