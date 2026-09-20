# Definition of Done

# Portfolio Complete — Local-First Scope Gate

- [ ] Hardened Docker backend, not a fake backend, executes the fixture lifecycle: workspace → clone → test → bounded change → patch/artifact → destroy.
- [ ] Effective container configuration proves non-root, dropped capabilities, no Docker socket/host credentials, filesystem restriction, CPU/memory/PID limits, and timeout.
- [ ] Default-deny or constrained egress and an explicit local allow path are executed; unauthorized destination is blocked.
- [ ] Scoped synthetic secret delivery, expiration/revocation, and redaction are demonstrated.
- [ ] Capability policy denies an ungranted privileged action.
- [ ] Prompt-injection/exfiltration attempt for secret, network, or forbidden host action is blocked and audited.
- [ ] Timeout/cancel cleanup and claimed abandoned-sandbox reaper behavior are executed.
- [ ] Audit and appropriate sandbox lifecycle metrics/traces are observable.
- [ ] Reproducible local demo, unit/integration/security/failure tests, and required CI pass.
- [ ] Documentation distinguishes hardened Docker execution from unexecuted gVisor/Firecracker/Kubernetes isolation.

## Maturity Levels

- **FOUNDATION:** core architecture/logic exists.
- **PARTIALLY VALIDATED:** meaningful integrations run but core sandbox evidence is incomplete.
- **LOCAL END-TO-END VALIDATED:** primary sandbox path runs, with material safety/recovery/observability gaps.
- **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE:** every gate above is executed; do not omit the suffix without production validation.

# Clean-Room Reproducibility Gate

`PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE` requires two executed clean-room cycles: clone → install → bootstrap hardened Docker runtime → smoke → fixture agent coding task/artifact demo → malicious containment/audit demo → validation → project-scoped cleanup → second clean bootstrap/demo. Planned commands: `make install`, `make bootstrap-local`, `make smoke`, `make demo-agent-task`, `make demo-containment`, `make verify`, `make clean-local`.

- [ ] Clean clone/bootstrap has no hidden state; primary and failure demos pass.
- [ ] Cleanup removes only this project and unrelated resources survive.
- [ ] Post-cleanup absence and second bootstrap/demo are recorded in `docs/VALIDATION.md`.
