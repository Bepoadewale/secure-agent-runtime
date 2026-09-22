# Definition of Done

# Portfolio Complete — Local-First Scope Gate

- [x] Hardened Docker backend executes the fixture lifecycle: workspace → clone → test → bounded change → patch/artifact → destroy.
- [x] Effective configuration proves non-root, read-only root, dropped capabilities, no Docker socket/host bind, no-new-privileges, and CPU/memory/PID/timeout limits.
- [x] Default-deny egress and explicit constrained local allow path execute; public egress is blocked.
- [x] Scoped synthetic secret delivery, output redaction, and revocation execute.
- [x] Capability policy denies ungranted privileged action.
- [x] Secret/network exfiltration attempt is blocked and audited.
- [x] Real timeout cleanup, active cancellation, and labelled abandoned-sandbox reaping execute.
- [x] Task/audit/artifact state survives control-plane restart.
- [x] Prometheus metrics and OTLP traces are observable in local services.
- [x] Reproducible demos, unit/security/integration tests, container build, Helm lint, and audit validation execute locally.
- [x] Documentation distinguishes hardened Docker execution from unexecuted gVisor/Firecracker/Kubernetes sandbox execution.
- [x] Required GitHub Actions checks are green for the final PR revision.

## Maturity Levels

- **FOUNDATION:** core architecture/logic exists.
- **PARTIALLY VALIDATED:** meaningful integrations run but core sandbox evidence is incomplete.
- **LOCAL END-TO-END VALIDATED:** primary sandbox path runs, with material safety/recovery/observability gaps or CI evidence pending.
- **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE:** every gate above is complete; do not omit the suffix without production validation.

# Clean-Room Reproducibility Gate

- [x] Clean project state → install → bootstrap → smoke → primary/security demos → validation → safe cleanup executed.
- [x] Cleanup removes only runtime-owned resources; an unrelated Docker fixture survived.
- [x] A second clean bootstrap, smoke, API lifecycle, security demo, and teardown executed.
- [x] `docs/VALIDATION.md` records the evidence.
