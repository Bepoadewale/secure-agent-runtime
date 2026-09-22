from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TaskState(StrEnum):
    SUBMITTED = "SUBMITTED"
    VALIDATING = "VALIDATING"
    POLICY_CHECK = "POLICY_CHECK"
    REJECTED = "REJECTED"
    QUEUED = "QUEUED"
    PROVISIONING = "PROVISIONING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"
    TERMINATING = "TERMINATING"
    DESTROYED = "DESTROYED"


class Capability(StrEnum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    PROCESS_EXECUTE = "process.execute"
    GIT_CLONE_PUBLIC = "git.clone.public"
    PACKAGE_MANAGER = "package-manager"
    ARTIFACT_UPLOAD = "artifact.upload"
    SECRET_TEST_EPHEMERAL = "secret.test.ephemeral"
    NETWORK_PYPI = "network.pypi"
    NETWORK_LOCAL_FIXTURE = "network.local-fixture"
    GIT_PUSH = "git.push"


class ResourceLimits(BaseModel):
    cpu: float = Field(default=1, gt=0, le=4)
    memory_mb: int = Field(default=1024, ge=128, le=4096)
    pids: int = Field(default=128, ge=16, le=256)
    timeout_seconds: int = Field(default=300, ge=1, le=900)
    output_bytes: int = Field(default=1_000_000, ge=1024, le=5_000_000)
    artifact_bytes: int = Field(default=5_000_000, ge=1024, le=50_000_000)


class RuntimeProfile(BaseModel):
    name: str
    network: str
    allowed_capabilities: set[Capability]
    limits: ResourceLimits
    runtime_class: str = "runc-standard"


PROFILES = {
    "restricted": RuntimeProfile(
        name="restricted",
        network="offline",
        allowed_capabilities={
            Capability.FILESYSTEM_READ,
            Capability.FILESYSTEM_WRITE,
            Capability.PROCESS_EXECUTE,
            Capability.ARTIFACT_UPLOAD,
        },
        limits=ResourceLimits(),
    ),
    "networked-build": RuntimeProfile(
        name="networked-build",
        network="package-install",
        allowed_capabilities={
            Capability.FILESYSTEM_READ,
            Capability.FILESYSTEM_WRITE,
            Capability.PROCESS_EXECUTE,
            Capability.PACKAGE_MANAGER,
            Capability.NETWORK_PYPI,
            Capability.ARTIFACT_UPLOAD,
        },
        limits=ResourceLimits(timeout_seconds=600),
    ),
    "local-allow": RuntimeProfile(
        name="local-allow",
        network="local-fixture-only",
        allowed_capabilities={
            Capability.FILESYSTEM_READ,
            Capability.FILESYSTEM_WRITE,
            Capability.PROCESS_EXECUTE,
            Capability.ARTIFACT_UPLOAD,
            Capability.NETWORK_LOCAL_FIXTURE,
        },
        limits=ResourceLimits(),
    ),
    "restricted-secret-test": RuntimeProfile(
        name="restricted-secret-test",
        network="offline",
        allowed_capabilities={
            Capability.FILESYSTEM_READ,
            Capability.PROCESS_EXECUTE,
            Capability.ARTIFACT_UPLOAD,
            Capability.SECRET_TEST_EPHEMERAL,
        },
        limits=ResourceLimits(),
    ),
    "gvisor-required": RuntimeProfile(
        name="gvisor-required",
        network="offline",
        allowed_capabilities={
            Capability.FILESYSTEM_READ,
            Capability.PROCESS_EXECUTE,
            Capability.ARTIFACT_UPLOAD,
        },
        limits=ResourceLimits(),
        runtime_class="gvisor-sandboxed",
    ),
}


class TaskRequest(BaseModel):
    tenant_id: str = Field(pattern=r"^[a-z][a-z0-9-]{1,30}$")
    agent_id: str = Field(pattern=r"^agent:[a-zA-Z0-9._-]+$")
    workspace: str = "safe-repo"
    runtime_profile: str = "restricted"
    capabilities: set[Capability] = {Capability.PROCESS_EXECUTE, Capability.ARTIFACT_UPLOAD}
    secret_requests: list[str] = []
    command: list[str] = Field(min_length=1, max_length=32)
    environment: dict[str, str] = {}
    idempotency_key: str = Field(min_length=8, max_length=128)
    limits: ResourceLimits = Field(default_factory=ResourceLimits)

    @field_validator("workspace")
    @classmethod
    def safe_workspace(cls, value):
        if PurePosixPath(value).is_absolute() or ".." in PurePosixPath(value).parts:
            raise ValueError("workspace path traversal prohibited")
        return value


class Sandbox(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    tenant_id: str
    runtime_class: str
    state: str = "CREATED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime


class TaskEvent(BaseModel):
    type: str
    task_id: UUID
    principal: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, str] = Field(default_factory=dict)


class Artifact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    tenant_id: str
    name: str
    sha256: str
    size: int


class SecretGrant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    tenant_id: str
    name: str
    expires_at: datetime
    revoked: bool = False


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request: TaskRequest
    state: TaskState = TaskState.SUBMITTED
    sandbox_id: UUID | None = None
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    failure_reason: str | None = None
