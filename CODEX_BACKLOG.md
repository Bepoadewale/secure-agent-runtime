# Completion Target

PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE

# Current Completion Blockers

- [ ] Required CI checks for the final Week 4 PR pass and the PR evidence is reviewed.

# P0 — Required for Portfolio Claim

P0 blocks `PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE`. Do not select P1/P2 polish while an item remains.

- [ ] Confirm green CI and reconcile the final PR/README claims with its executed evidence.

# P1 — Production Hardening

- Replace the local HMAC identity fixture with enterprise OIDC/JWKS validation.
- Add a durable production database and externally managed secret broker adapter.
- Add authenticated OTLP transport and trace retention controls.
- Add cancellation concurrency/load tests beyond the one-task local demonstration.

# P2 — Enhancements

- Expand `agentctl` to submit, run, cancel, and retrieve artifacts through the API.
- Add a small operator UI for task/audit inspection.

# P3 — Future / Cloud / Hardware

- Execute gVisor or Firecracker on a supported Linux/Kubernetes environment.
- Validate Kubernetes Job execution and production scheduler integration.
