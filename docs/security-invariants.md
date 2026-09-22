# Security invariants

- Sandboxes never mount Docker/runtime sockets or arbitrary host paths.
- No host PID/IPC/network or privileged sandbox is allowed.
- Agent policy/capabilities/runtime class are centrally selected.
- Sandboxes are tenant/task scoped, finite, and deny-all network by default.
- Long-lived platform credentials and raw secret values never enter sandboxes/audit logs.
- Cross-tenant task, sandbox, and artifact access is denied.
- Cleanup/revocation is idempotent.

Unit and security tests cover profile capability denial, runtime downgrade denial, idempotency, secret redaction, lifecycle destruction, signed API identity boundaries, timeout, active cancellation, and Docker containment. The local Helm chart specifies workload-level security context defaults; cluster-wide admission policy enforcement is a production hardening adapter, not an executed local claim.
