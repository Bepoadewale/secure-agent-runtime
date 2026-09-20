# Secure Agent Runtime — Agent Guide

Mission: execute untrusted agent work only in bounded, auditable, ephemeral sandboxes. Security controls outrank convenience.

Stack: Python 3.12, FastAPI, Docker sandbox backend, Prometheus, Kubernetes contracts.

Commands: `make install`, `make test`, `make lint`, `make demo`, `make demo-security`; Docker validation is required for containment claims.

Rules: never weaken isolation to satisfy a demo; never mount Docker socket, host credentials or broad host paths; no main pushes or secrets; fake tests do not validate Docker containment. Update factual status/backlog after work.

Completion rule: do not mark **PORTFOLIO COMPLETE — LOCAL-FIRST SCOPE** unless the evidence gate in `DEFINITION_OF_DONE.md` is executed. Configuration, mocks, manifests, architecture, unit tests, and documentation do not prove sandbox containment. The central untrusted-task sandbox story must run locally; unexecuted gVisor/Firecracker/Kubernetes adapters must be explicit.
