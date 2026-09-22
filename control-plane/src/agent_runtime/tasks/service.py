from time import perf_counter

from agent_runtime.artifacts.store import ArtifactStore
from agent_runtime.models.domain import Sandbox, Task, TaskEvent, TaskRequest, TaskState
from agent_runtime.observability.metrics import ACTIVE, DENIALS, EXECUTION, SECRETS, TASKS
from agent_runtime.observability.tracing import force_flush
from agent_runtime.policy.engine import PolicyEngine
from agent_runtime.secrets.broker import SecretBroker
from agent_runtime.state.store import RuntimeStateStore
from opentelemetry import trace


class TaskService:
    def __init__(self, backend, state_store: RuntimeStateStore | None = None):
        self.backend = backend
        self.state = state_store or RuntimeStateStore(":memory:")
        self.policy = PolicyEngine()
        self.secrets = SecretBroker()
        self.artifacts = ArtifactStore(self.state)
        self.tasks = self.state.load_tasks()
        self.events = self.state.events()
        self.keys = {(task.request.tenant_id, task.request.idempotency_key): task_id for task_id, task in self.tasks.items()}
        self.sandboxes = {}

    def event(self, task, typ, principal, **details):
        event = TaskEvent(type=typ, task_id=task.id, principal=principal, details=details)
        self.events.setdefault(str(task.id), []).append(event)
        self.state.append_event(event)

    def save(self, task):
        self.state.save_task(task)

    def submit(self, request: TaskRequest) -> Task:
        key = (request.tenant_id, request.idempotency_key)
        if key in self.keys:
            return self.tasks[self.keys[key]]
        task = Task(request=request)
        self.tasks[str(task.id)] = task
        self.keys[key] = str(task.id)
        self.save(task)
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
            self.save(task)
            return task
        self.event(task, "POLICY_APPROVED", "service:policy", profile=decision.profile)
        task.state = TaskState.QUEUED
        self.save(task)
        return task

    def run(self, task_id):
        task = self.tasks[task_id]
        if task.state != TaskState.QUEUED:
            return task
        task.state = TaskState.PROVISIONING
        self.save(task)
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
        self.save(task)
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
            self.save(task)
            ACTIVE.inc()
            start = perf_counter()
            self.event(task, "COMMAND_STARTED", task.request.agent_id)
            with trace.get_tracer("secure-agent-runtime").start_as_current_span(
                "sandbox.execute",
                attributes={
                    "agent_runtime.task_id": str(task.id),
                    "agent_runtime.tenant": task.request.tenant_id,
                    "agent_runtime.profile": task.request.runtime_profile,
                },
            ) as span:
                result = self.backend.execute(sandbox, task.request)
                span.set_attribute("agent_runtime.exit_code", result.exit_code)
                span.set_attribute("agent_runtime.timed_out", result.timed_out)
            force_flush()
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
            self.save(task)
        finally:
            task.state = TaskState.TERMINATING
            self.secrets.revoke_task(task.id)
            self.event(task, "SECRET_REVOKED", "service:secret-broker")
            self.backend.destroy(sandbox)
            sandbox.state = "DESTROYED"
            task.state = TaskState.DESTROYED
            self.event(task, "SANDBOX_DESTROYED", "service:provisioner")
            self.save(task)
            ACTIVE.dec()
        return task

    def cancel(self, task_id, principal):
        task = self.tasks[task_id]
        if task.state in {TaskState.DESTROYED, TaskState.CANCELLED}:
            return task
        task.state = TaskState.CANCELLED
        self.secrets.revoke_task(task.id)
        self.event(task, "TASK_CANCELLED", principal)
        self.save(task)
        return task
