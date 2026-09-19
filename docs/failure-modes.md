# Failure modes

Backend/image/repository/dependency failures are task failures with bounded logs; policy/broker failures fail closed. Timeout/OOM/PID exhaustion produce termination and cleanup events. Control-plane/worker crash requires durable state plus reaper reconciliation; backend disappearance becomes orphan cleanup. Revocation failure is high-severity/audited and retried. Sandbox escape is assumed possible at some risk level; contain with gVisor/microVM and host patching rather than claiming Docker is sufficient.
