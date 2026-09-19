# Security invariants

- Sandboxes never mount Docker/runtime sockets or arbitrary host paths.
- No host PID/IPC/network or privileged sandbox is allowed.
- Agent policy/capabilities/runtime class are centrally selected.
- Sandboxes are tenant/task scoped, finite, and deny-all network by default.
- Long-lived platform credentials and raw secret values never enter sandboxes/audit logs.
- Cross-tenant task, sandbox, and artifact access is denied.
- Cleanup/revocation is idempotent.

Unit/security tests cover profile capability denial, runtime downgrade denial, idempotency, secret redaction, lifecycle destruction, and timeout events. Kubernetes admission controls enforce workload-level invariants in deployment.
