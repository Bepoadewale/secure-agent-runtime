import hashlib

from agent_runtime.models.domain import Artifact


class ArtifactStore:
    def __init__(self, state_store=None):
        self.state_store = state_store
        self.items: dict[str, tuple[Artifact, bytes]] = (
            state_store.load_artifacts() if state_store else {}
        )

    def put(self, task_id, tenant_id, name, data: bytes, maximum: int) -> Artifact:
        if "/" in name or ".." in name or len(data) > maximum:
            raise ValueError("invalid artifact")
        artifact = Artifact(
            task_id=task_id,
            tenant_id=tenant_id,
            name=name,
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
        )
        self.items[str(artifact.id)] = (artifact, data)
        if self.state_store:
            self.state_store.save_artifact(artifact, data)
        return artifact

    def list(self, task_id, tenant_id):
        return [
            a for a, _ in self.items.values() if a.task_id == task_id and a.tenant_id == tenant_id
        ]
