"""Level 1 local sandbox backed by hardened Docker containers.

The trusted control-plane process talks to Docker.  The untrusted workload does
not receive a Docker socket, host directory, host network, or host credentials.
Each task receives a fresh Docker-managed volume that is deleted at teardown.
"""

from __future__ import annotations

import json
import subprocess

from agent_runtime.sandboxes.backend import ExecutionResult, SandboxBackend


class LocalContainerBackend(SandboxBackend):
    image = "agent-runtime-sandbox:local"

    def __init__(self, docker: str = "docker") -> None:
        self.docker = docker
        self.secrets: dict[str, str] = {}
        self.volumes: dict[str, str] = {}

    def _container_name(self, sandbox) -> str:
        return f"agent-runtime-{sandbox.id}"

    def _volume_name(self, sandbox) -> str:
        return f"agent-runtime-workspace-{sandbox.id}"

    def _run(self, args: list[str], *, check: bool = True, timeout: int | None = None):
        return subprocess.run(
            [self.docker, *args],
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def _hardened_args(self, sandbox, request, volume: str) -> list[str]:
        network = "agent-runtime-local-allow" if request.runtime_profile == "local-allow" else "none"
        args = [
            "--name",
            self._container_name(sandbox),
            "--network",
            network,
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
            "--mount",
            f"type=volume,source={volume},target=/workspace,volume-nocopy",
        ]
        for key, value in self.secrets.items():
            args.extend(["--env", f"{key}={value}"])
        return args

    def create(self, sandbox, request, secrets: dict[str, str]):
        self.secrets = secrets
        volume = self._volume_name(sandbox)
        self.volumes[str(sandbox.id)] = volume
        self._run(["volume", "create", volume])
        try:
            # Docker creates a fresh volume as root. This trusted one-shot setup
            # container only changes its ownership; it does not run task input.
            self._run(
                [
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--mount",
                    f"type=volume,source={volume},target=/workspace,volume-nocopy",
                    "alpine:3.21",
                    "chown",
                    "65532:65532",
                    "/workspace",
                ]
            )
            # The fixture repository lives inside the immutable sandbox image;
            # this is a genuine local git clone without a host bind mount.
            self._run(
                [
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--read-only",
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges",
                    "--tmpfs",
                    "/tmp:rw,noexec,nosuid,size=64m",
                    "--user",
                    "65532:65532",
                    "--mount",
                    f"type=volume,source={volume},target=/workspace,volume-nocopy",
                    self.image,
                    "git",
                    "clone",
                    "--no-local",
                    "/opt/fixture-repo",
                    "/workspace",
                ]
            )
            self._run(
                [
                    "create",
                    *self._hardened_args(sandbox, request, volume),
                    self.image,
                    *request.command,
                ]
            )
        except Exception:
            self.destroy(sandbox)
            raise

    def execute(self, sandbox, request) -> ExecutionResult:
        try:
            completed = self._run(
                ["start", "--attach", self._container_name(sandbox)],
                check=False,
                timeout=request.limits.timeout_seconds,
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

    def hardening_evidence(self, sandbox) -> dict[str, str]:
        raw = self._run(["inspect", self._container_name(sandbox)]).stdout
        config = json.loads(raw)[0]
        host = config["HostConfig"]
        mounts = config.get("Mounts", [])
        destinations = {mount["Destination"] for mount in mounts}
        return {
            "user": config["Config"].get("User", ""),
            "read_only_rootfs": str(host.get("ReadonlyRootfs", False)).lower(),
            "cap_drop": ",".join(host.get("CapDrop") or []),
            "no_new_privileges": str(host.get("SecurityOpt") or []),
            "network_mode": host.get("NetworkMode", ""),
            "pids_limit": str(host.get("PidsLimit")),
            "memory_bytes": str(host.get("Memory")),
            "docker_socket_mounted": str("/var/run/docker.sock" in destinations).lower(),
            "host_bind_mounted": str(any(mount["Type"] == "bind" for mount in mounts)).lower(),
        }

    def collect_patch(self, sandbox, maximum: int) -> bytes:
        volume = self.volumes[str(sandbox.id)]
        completed = self._run(
            [
                "run",
                "--rm",
                "--network",
                "none",
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=64m",
                "--user",
                "65532:65532",
                "--workdir",
                "/workspace",
                "--mount",
                f"type=volume,source={volume},target=/workspace,volume-nocopy",
                self.image,
                "git",
                "diff",
                "--no-ext-diff",
            ],
            check=False,
        )
        return (completed.stdout + completed.stderr).encode()[:maximum]

    def destroy(self, sandbox):
        self._run(["rm", "-f", self._container_name(sandbox)], check=False)
        volume = self.volumes.pop(str(sandbox.id), self._volume_name(sandbox))
        self._run(["volume", "rm", "-f", volume], check=False)
