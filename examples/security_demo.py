from agent_runtime.models.domain import Capability,TaskRequest
from agent_runtime.sandboxes.fake import FakeBackend
from agent_runtime.tasks.service import TaskService
service=TaskService(FakeBackend())
task=service.submit(TaskRequest(tenant_id="team-a",agent_id="agent:injected",workspace="malicious-repo",runtime_profile="restricted",capabilities={Capability.PROCESS_EXECUTE,Capability.GIT_PUSH},idempotency_key="prompt-injection-001",command=["cat","README.md"]))
print(task.state, task.failure_reason)
