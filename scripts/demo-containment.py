#!/usr/bin/env python3
"""Exercise default-deny egress and the explicitly constrained local allow path."""

import subprocess

from agent_runtime.models.domain import Capability, TaskRequest
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService


def run(request: TaskRequest):
    service = TaskService(LocalContainerBackend())
    task = service.submit(request)
    if task.failure_reason:
        raise SystemExit(task.failure_reason)
    return service.run(str(task.id))


def main() -> None:
    subprocess.run(["./scripts/bootstrap-egress-fixture.sh"], check=True)
    denied = run(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:containment",
            idempotency_key="deny-egress-001",
            capabilities={Capability.PROCESS_EXECUTE, Capability.ARTIFACT_UPLOAD},
            command=["sh", "-lc", "python -c 'import urllib.request; urllib.request.urlopen(\"http://example.com\", timeout=2)'"],
        )
    )
    allowed = run(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:containment",
            idempotency_key="allow-egress-001",
            runtime_profile="local-allow",
            capabilities={
                Capability.PROCESS_EXECUTE,
                Capability.ARTIFACT_UPLOAD,
                Capability.NETWORK_LOCAL_FIXTURE,
            },
            command=["python", "-c", "import urllib.request; print(urllib.request.urlopen('http://agent-runtime-local-egress-fixture:8080', timeout=2).status)"],
        )
    )
    if denied.exit_code == 0 or allowed.exit_code != 0 or "200" not in allowed.stdout:
        raise SystemExit(f"containment failed: deny={denied.exit_code} allow={allowed.exit_code}")
    print("Containment demo passed: public egress was blocked; only the internal local fixture was reachable.")


if __name__ == "__main__":
    main()
