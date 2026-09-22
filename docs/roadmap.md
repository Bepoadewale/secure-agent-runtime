# Roadmap

- [x] Local-first core: hardened Docker task execution, bounded fixture modification, artifacts, policy/capabilities, prompt-injection containment, and scoped synthetic secrets.
- [x] Local recovery: durable SQLite task/audit/artifact state, API restart recovery, active cancellation, and project-labelled orphan reaping.
- [x] Local observability: Prometheus metrics plus a `sandbox.execute` trace exported through an OTel Collector to Jaeger; the project Compose stack includes Grafana.
- [x] Local Kubernetes validation: kind bootstrap, hardened control-plane Helm deployment, and readiness smoke check. The kind pod does not execute Docker sandboxes.
- [x] Documentation/adapters: gVisor, Firecracker, SPIFFE/Vault, OPA sidecar, MCP, and broader production deployment patterns.
- [ ] Production validation: dedicated hardened Docker host; gVisor or Firecracker execution; enterprise OIDC/JWKS; OPA sidecar; Redis/PostgreSQL queue; Vault/SPIRE; egress proxy; cluster-wide admission policy; distributed worker/Kubernetes sandbox backend; and production Grafana/SLO operations.
