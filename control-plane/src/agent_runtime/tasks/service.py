from time import perf_counter

from agent_runtime.artifacts.store import ArtifactStore
from agent_runtime.models.domain import Sandbox, Task, TaskEvent, TaskRequest, TaskState
from agent_runtime.observability.metrics import ACTIVE, DENIALS, EXECUTION, SECRETS, TASKS
from agent_runtime.policy.engine import PolicyEngine
from agent_runtime.secrets.broker import SecretBroker


class TaskService:
    def __init__(self, backend):
        self.backend = backend
        self.policy = PolicyEngine()
        self.secrets = SecretBroker()
        self.artifacts = ArtifactStore()
        self.tasks = {}
        self.events = {}
        self.keys = {}
        self.sandboxes = {}

    def event(self, task, typ, principal, **details):
        self.events.setdefault(str(task.id), []).append(
            TaskEvent(type=typ, task_id=task.id, principal=principal, details=details)
        )

    def submit(self, request: TaskRequest) -> Task:
        key = (request.tenant_id, request.idempotency_key)
        if key in self.keys:
            return self.tasks[self.keys[key]]
        task = Task(request=request)
        self.tasks[str(task.id)] = task
        self.keys[key] = str(task.id)
        self.event(task, "TASK_SUBMITTED", request.agent_id)
        task.state = TaskState.VALIDATING
        task.state = TaskState.POLICY_CHECK
        decision = self.policy.evaluate(request)
        if not decision.allowed:
            task.state = TaskState.REJECTED
            task.failure_reason = "; ".join(decision.reasons)
            self.event(task, "POLICY_DENIED", "service:policy", reasons=task.failure_reason)
            DENIALS.labels("policy").inc()
            TASKS.labels(request.tenant_id, "rejected").inc()
            return task
        self.event(task, "POLICY_APPROVED", "service:policy", profile=decision.profile)
        task.state = TaskState.QUEUED
        return task

    def run(self, task_id):
        task = self.tasks[task_id]
        if task.state != TaskState.QUEUED:
            return task
        task.state = TaskState.PROVISIONING
        sandbox = Sandbox(
            task_id=task.id,
            tenant_id=task.request.tenant_id,
            runtime_class=__import__("agent_runtime.models.domain", fromlist=["PROFILES"])
            .PROFILES[task.request.runtime_profile]
            .runtime_class,
            expires_at=task.created_at
            + __import__("datetime").timedelta(seconds=task.request.limits.timeout_seconds + 60),
        )
        self.sandboxes[str(sandbox.id)] = sandbox
        task.sandbox_id = sandbox.id
        self.event(task, "SANDBOX_CREATED", "service:provisioner", sandbox_id=str(sandbox.id))
        try:
            issued = self.secrets.issue(task.id, task.request)
            SECRETS.labels("issued").inc() if issued else None
            self.event(task, "SECRET_ISSUED", "service:secret-broker") if issued else None
            self.backend.create(sandbox, task.request, issued)
            if hasattr(self.backend, "hardening_evidence"):
                self.event(
                    task,
                    "SANDBOX_HARDENING_VERIFIED",
                    "service:provisioner",
                    **self.backend.hardening_evidence(sandbox),
                )
            sandbox.state = "RUNNING"
            task.state = TaskState.RUNNING
            ACTIVE.inc()
            start = perf_counter()
            self.event(task, "COMMAND_STARTED", task.request.agent_id)
            result = self.backend.execute(sandbox, task.request)
            EXECUTION.observe(perf_counter() - start)
            task.stdout = self.secrets.redact(result.stdout)
            task.stderr = self.secrets.redact(result.stderr)
            task.exit_code = result.exit_code
            if result.timed_out:
                task.state = TaskState.TIMED_OUT
                self.event(task, "TASK_TIMEOUT", "service:worker")
            elif result.exit_code == 0:
                task.state = TaskState.SUCCEEDED
                self.event(task, "COMMAND_EXITED", task.request.agent_id, exit_code="0")
            else:
                task.state = TaskState.FAILED
                self.event(
                    task, "COMMAND_EXITED", task.request.agent_id, exit_code=str(result.exit_code)
                )
            artifact = self.artifacts.put(
                task.id,
                task.request.tenant_id,
                "logs.txt",
                (task.stdout + task.stderr).encode(),
                task.request.limits.artifact_bytes,
            )
            self.event(task, "ARTIFACT_CREATED", "service:artifacts", artifact_id=str(artifact.id))
            if hasattr(self.backend, "collect_patch"):
                patch = self.backend.collect_patch(sandbox, task.request.limits.artifact_bytes)
                patch_artifact = self.artifacts.put(
                    task.id,
                    task.request.tenant_id,
                    "workspace.patch",
                    patch,
                    task.request.limits.artifact_bytes,
                )
                self.event(
                    task,
                    "PATCH_ARTIFACT_CREATED",
                    "service:artifacts",
                    artifact_id=str(patch_artifact.id),
                )
            TASKS.labels(task.request.tenant_id, task.state.value).inc()
        finally:
            task.state = TaskState.TERMINATING
            self.secrets.revoke_task(task.id)
            self.event(task, "SECRET_REVOKED", "service:secret-broker")
            self.backend.destroy(sandbox)
            sandbox.state = "DESTROYED"
            task.state = TaskState.DESTROYED
            self.event(task, "SANDBOX_DESTROYED", "service:provisioner")
            ACTIVE.dec()
        return task

    def cancel(self, task_id, principal):
        task = self.tasks[task_id]
        if task.state in {TaskState.DESTROYED, TaskState.CANCELLED}:
            return task
        task.state = TaskState.CANCELLED
        self.secrets.revoke_task(task.id)
        self.event(task, "TASK_CANCELLED", principal)
        return task
