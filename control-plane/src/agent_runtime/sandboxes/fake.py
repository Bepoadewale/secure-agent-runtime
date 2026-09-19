from agent_runtime.sandboxes.backend import ExecutionResult, SandboxBackend


class FakeBackend(SandboxBackend):
    def __init__(self, result=None):
        self.result = result or ExecutionResult(0, "tests passed\n", " ")
        self.destroyed = []

    def create(self, sandbox, request, secrets):
        self.last = (sandbox, request, secrets)

    def execute(self, sandbox, request):
        return self.result

    def destroy(self, sandbox):
        self.destroyed.append(sandbox.id)
