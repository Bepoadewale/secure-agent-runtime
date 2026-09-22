# Project Status

## Current Maturity

PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE

## Executed and Verified

- Signed HS256 local JWT validation with expiry, issuer/audience, tenant, role, and agent-subject binding.
- FastAPI task API → policy → hardened Docker fixture lifecycle → patch/log artifacts → API restart recovery.
- Docker effective configuration: uid/gid `65532`, read-only root, dropped capabilities, no-new-privileges, PID/memory/CPU bounds, no Docker socket, and no host bind mount.
- Public egress denial plus an explicit internal-network fixture allow path.
- Secret-capability denial, synthetic-secret redaction/revocation, real timeout cleanup, active cancellation, and labelled orphan reaping.
- SQLite durability for tasks, audit events, and artifacts across control-plane restart.
- kind Helm deployment of the hardened control-plane API and readiness smoke check.
- OTel Collector → Jaeger trace and Prometheus/Grafana local observability stack.
- Two clean-room cycles, including project-scoped teardown and survival of an unrelated Docker fixture.

## Implemented but Not End-to-End Validated

- None in the local-first core path.

## Simulated

- Synthetic short-lived secret value only; no production secret manager was used.

## Architecture / Contracts Only

- gVisor, Firecracker, and production Kubernetes sandbox execution.

## Known Failures

- None known in the local-first scope.

## Current P0 Objective

Maintain the validated local demo and keep production adapters explicitly unexecuted until they are actually exercised.

## Completion Blockers

- None for the local-first scope.

## Explicitly Unexecuted Production Adapters

- Enterprise OIDC/JWKS, managed secret broker, gVisor, Firecracker, production Kubernetes job execution, and cloud-scale runtime scheduling.

## Last Validation

- `make lint`: passed.
- `make test`: 17 passed, 1 Docker integration skipped by default.
- `RUN_DOCKER_INTEGRATION=1 PYTHONPATH=control-plane/src .venv/bin/python -m pytest -q`: 18 passed.
- `make demo-api`, `make demo-agent-task`, `make demo-containment`, `make demo-security-real`, `make demo-timeout`, `make demo-cancel`, `make demo-recovery`, and `make demo-observability`: passed.
- Two clean-room bootstrap/demo/cleanup cycles: passed; details in `docs/VALIDATION.md`.
- GitHub Actions `test`, `supply-chain`, and `local-e2e`: passed for PR #4 (runs `35775377997` and `35775384612`).

## Last Updated

2026-09-22, implementation and documentation evidence through `db906d8` on `codex/week-04-secure-agent-runtime`.

## Clean-Room Reproducibility

**Status: VALIDATED**

Two clean starts successfully completed bootstrap, smoke, primary/security demos, validation, safe teardown, and a second bootstrap/demo. The teardown was checked against an unrelated Docker fixture, which survived.
