from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class SandboxBackend(ABC):
    @abstractmethod
    def create(self, sandbox, request, secrets: dict[str, str]): ...
    @abstractmethod
    def execute(self, sandbox, request) -> ExecutionResult: ...
    @abstractmethod
    def destroy(self, sandbox) -> None: ...
