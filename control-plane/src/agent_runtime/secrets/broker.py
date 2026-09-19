from datetime import UTC, datetime, timedelta

from agent_runtime.models.domain import Capability, SecretGrant, TaskRequest


class SecretBroker:
    """Demo broker. Values are held in memory, injected only into sandbox env, and redacted from output."""

    def __init__(self):
        self.grants: dict[str, SecretGrant] = {}
        self.values: dict[str, str] = {}

    def issue(self, task_id, request: TaskRequest) -> dict[str, str]:
        if not request.secret_requests:
            return {}
        if Capability.SECRET_TEST_EPHEMERAL not in request.capabilities:
            raise PermissionError("secret capability not granted")
        issued = {}
        for name in request.secret_requests:
            if name != "test-api-token":
                raise PermissionError("secret is not authorized for task")
            grant = SecretGrant(
                task_id=task_id,
                tenant_id=request.tenant_id,
                name=name,
                expires_at=datetime.now(UTC) + timedelta(minutes=10),
            )
            value = f"demo-task-{task_id}"
            self.grants[str(grant.id)] = grant
            self.values[str(grant.id)] = value
            issued["AGENT_TEST_TOKEN"] = value
        return issued

    def revoke_task(self, task_id):
        for key, grant in self.grants.items():
            if grant.task_id == task_id:
                grant.revoked = True
                self.values.pop(key, None)

    def redact(self, text: str) -> str:
        for value in self.values.values():
            text = text.replace(value, "[REDACTED]")
        return text
