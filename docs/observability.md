# Observability and SLOs

The local stack launched by `make demo-observability` contains a
project-scoped OpenTelemetry Collector, Jaeger, Prometheus, and Grafana.
`make demo-observability` has been executed locally: it verified a Prometheus
task series and an OTLP-exported `sandbox.execute` trace in Jaeger.

The control plane exposes these Prometheus metrics at `/metrics`:

- `agent_runtime_tasks_total` by tenant and outcome;
- `agent_runtime_policy_denials_total` by reason;
- `agent_runtime_active_sandboxes`;
- `agent_runtime_execution_seconds`; and
- `agent_runtime_secret_issuance_total` by outcome.

Tracing is optional and enabled only when
`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` is configured. The currently executed
trace boundary is the real sandbox execution lifecycle (`sandbox.execute`),
with no source code, raw task content, or secret value recorded as span data.
Broader API, policy, scheduling, artifact, and cleanup spans are production
hardening work, not an executed local claim.

Example objectives—such as task API availability, p95 execution time, cleanup
success, and credential-revocation success—are illustrative workload-specific
targets, not measured production SLOs.
