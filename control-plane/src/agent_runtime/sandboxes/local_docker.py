"""Level 1 local sandbox: hardened Docker container, not a VM security boundary."""

import subprocess

from agent_runtime.sandboxes.backend import ExecutionResult, SandboxBackend


class LocalContainerBackend(SandboxBackend):
    image = "agent-runtime-sandbox:local"

    def create(self, sandbox, request, secrets):
        # Deliberately no host mount, socket, privilege, host network, or service-account token.
        self.secrets = secrets

    def execute(self, sandbox, request):
        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            f"agent-{sandbox.id}",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(request.limits.pids),
            "--memory",
            f"{request.limits.memory_mb}m",
            "--cpus",
            str(request.limits.cpu),
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--user",
            "65532:65532",
            "--workdir",
            "/workspace",
        ]
        for key, value in self.secrets.items():
            command.extend(["--env", f"{key}={value}"])
        command.extend([self.image, *request.command])
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=request.limits.timeout_seconds
            )
            return ExecutionResult(
                completed.returncode,
                completed.stdout[: request.limits.output_bytes],
                completed.stderr[: request.limits.output_bytes],
            )
        except subprocess.TimeoutExpired as error:
            return ExecutionResult(
                124,
                (error.stdout or "")[: request.limits.output_bytes],
                (error.stderr or "")[: request.limits.output_bytes],
                True,
            )

    def destroy(self, sandbox):
        subprocess.run(
            ["docker", "rm", "-f", f"agent-{sandbox.id}"], capture_output=True, check=False
        )
