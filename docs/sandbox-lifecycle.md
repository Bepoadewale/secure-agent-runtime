# Sandbox lifecycle

`SUBMITTED → VALIDATING → POLICY_CHECK → QUEUED → PROVISIONING → RUNNING → terminal → TERMINATING → DESTROYED`. Rejection is terminal without sandbox creation. Every transition is persisted as an audit event. Termination revokes grants, bounds output/artifact extraction, destroys the backend, and records destruction.

The local implementation persists tasks, artifacts, and audit events in SQLite. `make demo-recovery` creates a deliberately labelled abandoned sandbox resource and proves that the reaper removes only project-owned labelled containers and volumes. A production scheduler/worker queue and cross-host reconciliation remain roadmap work.
