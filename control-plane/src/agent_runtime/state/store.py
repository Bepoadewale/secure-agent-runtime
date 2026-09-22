"""Durable local control-plane state for tasks and append-only audit events."""

import os
import sqlite3
from pathlib import Path

from agent_runtime.models.domain import Artifact, Task, TaskEvent


class RuntimeStateStore:
    def __init__(self, path: str | None = None):
        target = Path(path or os.getenv("AGENT_RUNTIME_DB", ".local/runtime.db"))
        target.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(target, check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(tenant_id, idempotency_key))"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS audit_events (sequence INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, payload TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY, task_id TEXT NOT NULL, tenant_id TEXT NOT NULL, payload TEXT NOT NULL, content BLOB NOT NULL)"
        )
        self.connection.commit()

    def save_task(self, task: Task) -> None:
        self.connection.execute(
            "INSERT INTO tasks(id, tenant_id, idempotency_key, payload) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
            (str(task.id), task.request.tenant_id, task.request.idempotency_key, task.model_dump_json()),
        )
        self.connection.commit()

    def load_tasks(self) -> dict[str, Task]:
        return {row[0]: Task.model_validate_json(row[1]) for row in self.connection.execute("SELECT id, payload FROM tasks")}

    def append_event(self, event: TaskEvent) -> None:
        self.connection.execute(
            "INSERT INTO audit_events(task_id, payload) VALUES (?, ?)", (str(event.task_id), event.model_dump_json())
        )
        self.connection.commit()

    def events(self) -> dict[str, list[TaskEvent]]:
        output: dict[str, list[TaskEvent]] = {}
        for task_id, payload in self.connection.execute("SELECT task_id, payload FROM audit_events ORDER BY sequence"):
            output.setdefault(task_id, []).append(TaskEvent.model_validate_json(payload))
        return output

    def save_artifact(self, artifact: Artifact, content: bytes) -> None:
        self.connection.execute(
            "INSERT INTO artifacts(id, task_id, tenant_id, payload, content) VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, content=excluded.content",
            (
                str(artifact.id),
                str(artifact.task_id),
                artifact.tenant_id,
                artifact.model_dump_json(),
                content,
            ),
        )
        self.connection.commit()

    def load_artifacts(self) -> dict[str, tuple[Artifact, bytes]]:
        return {
            row[0]: (Artifact.model_validate_json(row[1]), bytes(row[2]))
            for row in self.connection.execute("SELECT id, payload, content FROM artifacts")
        }
