from agent_runtime.models.domain import TaskRequest
from agent_runtime.sandboxes.fake import FakeBackend
from agent_runtime.tasks.service import TaskService
service=TaskService(FakeBackend())
task=service.submit(TaskRequest(tenant_id="team-a",agent_id="agent:demo",idempotency_key="demo-normal-001",command=["pytest","-q"]))
done=service.run(str(task.id))
print(done.state, done.exit_code, [event.type for event in service.events[str(done.id)]])
