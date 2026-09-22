#!/usr/bin/env python3
"""Run the real, bounded fixture-task lifecycle through the Docker backend."""

from agent_runtime.models.domain import Capability, TaskRequest, TaskState
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.tasks.service import TaskService


def main() -> None:
    service = TaskService(LocalContainerBackend())
    task = service.submit(
        TaskRequest(
            tenant_id="team-a",
            agent_id="agent:fixture-coder",
            idempotency_key="fixture-task-001",
            workspace="fixture-repo",
            capabilities={
                Capability.FILESYSTEM_READ,
                Capability.FILESYSTEM_WRITE,
                Capability.PROCESS_EXECUTE,
                Capability.ARTIFACT_UPLOAD,
            },
            command=[
                "sh",
                "-lc",
                "python -m unittest -v && printf '\\n# bounded fixture change\\n' >> app.py && python -m unittest -v",
            ],
        )
    )
    if task.state is not TaskState.QUEUED:
        raise SystemExit(f"fixture task was rejected: {task.failure_reason}")

    done = service.run(str(task.id))
    events = service.events[str(task.id)]
    artifacts = service.artifacts.list(task.id, "team-a")
    event_types = [event.type for event in events]
    if done.exit_code != 0 or done.state is not TaskState.DESTROYED:
        raise SystemExit(f"fixture task failed: exit={done.exit_code} state={done.state}")
    if "SANDBOX_HARDENING_VERIFIED" not in event_types:
        raise SystemExit("hardened Docker configuration was not captured")
    if {artifact.name for artifact in artifacts} != {"logs.txt", "workspace.patch"}:
        raise SystemExit("expected logs and patch artifacts were not created")

    evidence = next(event.details for event in events if event.type == "SANDBOX_HARDENING_VERIFIED")
    print(f"task={done.id} exit={done.exit_code} final_state={done.state}")
    print("lifecycle=" + " → ".join(event_types))
    print("artifacts=" + ", ".join(f"{item.name}:{item.sha256[:12]}" for item in artifacts))
    print(
        "hardening="
        + ", ".join(
            f"{key}={evidence[key]}"
            for key in ("user", "read_only_rootfs", "cap_drop", "network_mode", "docker_socket_mounted", "host_bind_mounted")
        )
    )
    print("Real hardened Docker fixture task passed and its sandbox workspace was deleted.")


if __name__ == "__main__":
    main()
