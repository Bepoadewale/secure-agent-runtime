from agent_runtime.models.domain import PROFILES, Capability, TaskRequest


class PolicyDecision:
    def __init__(self, allowed: bool, reasons: list[str] | None = None, profile: str | None = None):
        self.allowed = allowed
        self.reasons = reasons or []
        self.profile = profile


class PolicyEngine:
    """Fail-closed local policy adapter; policy/agent-runtime.rego is deployable OPA contract."""

    def evaluate(self, request: TaskRequest) -> PolicyDecision:
        profile = PROFILES.get(request.runtime_profile)
        reasons = []
        if not profile:
            reasons.append("unknown centrally controlled runtime profile")
        else:
            if not request.capabilities <= profile.allowed_capabilities:
                reasons.append("requested capability is not granted by runtime profile")
            if Capability.GIT_PUSH in request.capabilities:
                reasons.append("git.push is denied in all default profiles")
            if request.limits.timeout_seconds > profile.limits.timeout_seconds:
                reasons.append("requested timeout exceeds profile maximum")
            if (
                request.limits.memory_mb > profile.limits.memory_mb
                or request.limits.cpu > profile.limits.cpu
            ):
                reasons.append("requested resources exceed profile maximum")
        if (
            request.runtime_profile == "restricted"
            and request.workspace == "malicious-repo"
            and profile.runtime_class != "gvisor-sandboxed"
        ):
            reasons.append("untrusted repository requires gVisor or explicit rejection")
        return PolicyDecision(not reasons, reasons, profile.name if profile else None)
