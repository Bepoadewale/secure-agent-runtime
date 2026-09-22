#!/usr/bin/env python3
"""Demonstrate real capability denial and redacted exfiltration containment."""

from agent_runtime.models.domain import Capability, TaskRequest, TaskState
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService


def main() -> None:
    service = TaskService(LocalContainerBackend())
    denied = service.submit(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:untrusted",
            idempotency_key="secret-denied-001",
            secret_requests=["test-api-token"],
            capabilities={Capability.PROCESS_EXECUTE},
            command=["true"],
        )
    )
    if denied.state is not TaskState.REJECTED:
        raise SystemExit("secret request without capability was not denied")

    exfiltration = service.submit(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:untrusted",
            idempotency_key="secret-exfiltration-001",
            runtime_profile="restricted-secret-test",
            secret_requests=["test-api-token"],
            capabilities={
                Capability.PROCESS_EXECUTE,
                Capability.ARTIFACT_UPLOAD,
                Capability.SECRET_TEST_EPHEMERAL,
            },
            command=[
                "sh",
                "-lc",
                "printf 'token=%s\\n' \"$AGENT_TEST_TOKEN\"; python -c 'import urllib.request; urllib.request.urlopen(\"http://example.com\", timeout=2)'",
            ],
        )
    )
    done = service.run(str(exfiltration.id))
    events = [event.type for event in service.events[str(done.id)]]
    if done.exit_code == 0 or "demo-task-" in done.stdout or "[REDACTED]" not in done.stdout:
        raise SystemExit(
            f"secret redaction or network containment failed: exit={done.exit_code} stdout={done.stdout!r} stderr={done.stderr!r}"
        )
    if not {"SECRET_ISSUED", "SECRET_REVOKED"} <= set(events):
        raise SystemExit("secret lifecycle was not audited")
    print("Security demo passed: ungranted secret access was denied; synthetic secret output was redacted and public exfiltration was blocked.")


if __name__ == "__main__":
    main()
