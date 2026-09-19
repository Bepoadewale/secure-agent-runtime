# Sandbox lifecycle

`SUBMITTED → VALIDATING → POLICY_CHECK → QUEUED → PROVISIONING → RUNNING → terminal → TERMINATING → DESTROYED`. Rejection is terminal without sandbox creation. Every transition produces an event. Termination revokes grants, bounds output/artifact extraction, destroys the backend, and records destruction. A reaper should reconcile expired/orphaned sandbox records against backend state in durable production storage.
