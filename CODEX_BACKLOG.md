# Completion Target

PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE

# Current Completion Blockers

- Execute the hardened Docker task lifecycle and verify containment, egress controls, artifacts, audit, and cleanup.
- Demonstrate blocked injection/exfiltration and recovery/reaper behavior.

# P0 — Required for Portfolio Claim

P0 blocks PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE. Do not choose P1/P2 polish while blockers remain.

- Make hardened Docker backend the tested default path.
- Run clone/test/modify/artifact/destroy lifecycle against a fixture repository.
- Add containment checks for non-root, read-only root, caps, socket/credential absence and limits.
- Test network deny and constrained allow with a local target.
- Demonstrate injection/exfiltration attempt blocked and audited; add reaper recovery.

# P1 — Production Hardening

- OTel, Prometheus, persistent audit/artifacts, gVisor profile.

# P2 — Enhancements

- Developer UI and richer CLI.

# P3 — Future / Cloud / Hardware

- Firecracker and production Kubernetes isolation.
