from uuid import UUID

from agent_runtime.auth.dependencies import admin, principal
from agent_runtime.models.domain import TaskRequest
from agent_runtime.observability.tracing import configure_tracing
from agent_runtime.sandboxes.local_docker import LocalContainerBackend
from agent_runtime.state.store import RuntimeStateStore
from agent_runtime.tasks.service import TaskService
from fastapi import Depends, FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

configure_tracing()
app = FastAPI(title="Secure Agent Runtime", version="0.1.0")
service = TaskService(LocalContainerBackend(), RuntimeStateStore())


@app.get("/healthz")
def healthz():
    return {"status": "ok", "isolation": "level-1-hardened-container"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/tasks", status_code=202)
def create_task(request: TaskRequest, who=Depends(principal)):
    if who.tenant_id != request.tenant_id:
        raise HTTPException(403, "tenant identity mismatch")
    if who.principal_type == "agent" and who.subject != request.agent_id:
        raise HTTPException(403, "agent identity mismatch")
    return service.submit(request)


@app.post("/api/v1/tasks/{task_id}/run")
def run_task(task_id: UUID, who=Depends(principal)):
    task = service.tasks.get(str(task_id))
    if not task or task.request.tenant_id != who.tenant_id:
        raise HTTPException(404, "task not found")
    return service.run(str(task_id))


@app.get("/api/v1/tasks/{task_id}")
def get_task(task_id: UUID, who=Depends(principal)):
    task = service.tasks.get(str(task_id))
    if not task or task.request.tenant_id != who.tenant_id:
        raise HTTPException(404, "task not found")
    return task


@app.post("/api/v1/tasks/{task_id}/cancel")
def cancel(task_id: UUID, who=Depends(principal)):
    task = service.tasks.get(str(task_id))
    if not task or task.request.tenant_id != who.tenant_id:
        raise HTTPException(404, "task not found")
    return service.cancel(str(task_id), who[1])


@app.get("/api/v1/tasks/{task_id}/events")
def events(task_id: UUID, who=Depends(principal)):
    task = get_task(task_id, who)
    return service.events.get(str(task.id), [])


@app.get("/api/v1/tasks/{task_id}/artifacts")
def artifacts(task_id: UUID, who=Depends(principal)):
    task = get_task(task_id, who)
    return service.artifacts.list(task.id, who.tenant_id)


@app.get("/api/v1/sandboxes/{sandbox_id}")
def sandbox(sandbox_id: UUID, who=Depends(principal)):
    item = service.sandboxes.get(str(sandbox_id))
    if not item or item.tenant_id != who[0]:
        raise HTTPException(404, "sandbox not found")
    return item


@app.get("/api/v1/audit")
def audit(who=Depends(admin)):
    return [event for values in service.events.values() for event in values]


@app.post("/api/v1/policies/evaluate")
def evaluate(request: TaskRequest, who=Depends(admin)):
    return service.policy.evaluate(request).__dict__
