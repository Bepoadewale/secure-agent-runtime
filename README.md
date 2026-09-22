# Secure Agent Runtime

A local-first execution platform for AI agents that need to make bounded changes to untrusted code without receiving host, Docker, Kubernetes, cloud, or long-lived secret credentials.

An agent may request a task. It may not choose its own isolation level, expand its capabilities, access another tenant, mount host paths, use the Docker socket, or approve a privileged action by implication.

```text
signed agent/human identity
  -> tenant binding + capability policy
  -> trusted control plane
  -> ephemeral hardened Docker sandbox
  -> fixture clone / test / bounded change
  -> redacted artifacts + append-only audit
  -> revoke secrets + destroy container and workspace
```

## What genuinely runs locally

| Capability | Status | Evidence |
| --- | --- | --- |
| Signed local JWT API identity | ✅ EXECUTED LOCALLY | authenticated API lifecycle and boundary tests |
| Hardened Docker sandbox | ✅ EXECUTED LOCALLY | clone, test, modify, patch artifact, destroy |
| Network containment | ✅ EXECUTED LOCALLY | public egress blocked; explicit internal-only fixture allowed |
| Scoped synthetic secret | ✅ EXECUTED LOCALLY | denied when ungranted; redacted and revoked when granted |
| Restart recovery | ✅ EXECUTED LOCALLY | SQLite task/audit/artifact recovery after API restart |
| Timeout, cancellation, reaper | ✅ EXECUTED LOCALLY | real Docker timeout, active cancel, labelled orphan cleanup |
| Metrics and traces | ✅ EXECUTED LOCALLY | Prometheus series and OTLP trace in Jaeger through Collector |
| Hardened kind deployment | ✅ EXECUTED LOCALLY | non-root/read-only control-plane health deployment |
| gVisor / Firecracker / production Kubernetes sandboxing | 📐 ARCHITECTURE ONLY | documented production adapters; not claimed as run |

The sandbox is **Level 1 Docker isolation**, not VM-equivalent isolation. The trusted host control plane uses Docker to create sandboxes; untrusted workloads receive no Docker socket, host bind mount, host network, cloud credential, Kubernetes credential, or user credential directory.

## Clean local demo

Prerequisites: Docker Desktop, Python 3.12, `kind`, `kubectl`, and Helm.

```console
make install
make bootstrap-local
make smoke
make demo-api
make demo-agent-task
make demo-containment
make demo-security-real
make demo-timeout
make demo-cancel
make demo-recovery
make demo-observability
make verify
make clean-local
```

`make clean-local` deletes only labelled runtime containers/volumes, the exact egress fixture, this repository's Compose stack, kind cluster, and generated local state. It does not prune Docker globally or delete unrelated Kubernetes/Docker resources.

## Scenarios

- A signed agent submits a task for its own tenant and identity; the API rejects unsigned, cross-tenant, and impersonating requests.
- The sandbox clones an immutable local fixture, runs `unittest`, changes one tracked file, captures a patch, and deletes its workspace volume.
- An attempted public-network request fails under `--network none`; a distinct policy profile can reach only an internal fixture network.
- An agent that requests an ungranted secret is denied. A synthetic, task-scoped secret printed by a permitted task is redacted from retained output and revoked at teardown.
- A slow command hits its enforced runtime timeout; an active command can be cancelled; a labelled abandoned sandbox is reaped without touching unrelated Docker resources.

See [architecture](docs/architecture.md), [local development](docs/local-development.md), [security model](docs/security-model.md), [observability](docs/observability.md), and [validation evidence](docs/VALIDATION.md).
