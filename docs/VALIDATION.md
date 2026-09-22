# Validation

## Local validation

Executed on 2026-09-22 on macOS with Docker Desktop, Python 3.12, kind, kubectl, and Helm. The local stack used kind Kubernetes, Docker Engine, OTel Collector `0.120.0`, Jaeger `1.66.0`, Prometheus `3.2.1`, and Grafana `11.5.2`.

- `make lint`: passed.
- `make test`: 17 passed, 1 Docker integration skipped by default.
- `RUN_DOCKER_INTEGRATION=1 PYTHONPATH=control-plane/src .venv/bin/python -m pytest -q`: 18 passed.
- `make demo-api`: signed agent identity, API task lifecycle, task/audit/artifact persistence across restart: passed.
- `make demo-agent-task`: real clone/test/bounded change/patch/destroy: passed.
- `make demo-containment`: public egress denied and internal fixture allowed: passed.
- `make demo-security-real`: ungranted secret denied; synthetic secret redacted/revoked; public exfiltration blocked: passed.
- `make demo-timeout`, `make demo-cancel`, `make demo-recovery`: real timeout, active cancellation, and labelled orphan cleanup: passed.
- `make demo-observability`: Prometheus task series and Jaeger `sandbox.execute` trace through OTel Collector: passed.

## Clean-Room Validation

Starting state: no `secure-agent-runtime-local` kind cluster, no project-labelled Docker containers/volumes, no project Compose stack, no egress fixture, and no `.venv` or `.local` directory.

First cycle:

```console
make install
make bootstrap-local
make smoke
make demo-api
make demo-agent-task
make demo-containment
make demo-security-real
make demo-recovery
make demo-observability
make verify
make clean-local
```

Results: kind control plane became Ready; API lifecycle, hardened fixture, network/secret/recovery, and observability demos passed. Cleanup removed the project kind cluster, Compose services, labelled runtime resources, egress fixture, and generated state.

Cleanup safety check: an unrelated `alpine:3.21` Docker container ran during both cleanup checks and survived. It was explicitly removed only after the second check.

Second cycle:

```console
make install
make bootstrap-local
make smoke
make demo-api
make demo-security-real
make clean-local
```

Results: second bootstrap, kind readiness, authenticated API lifecycle/restart recovery, and security denial passed. The final cleanup confirmed no project-owned containers, labelled volumes, Compose resources, egress fixture, kind cluster, `.venv`, or `.local` state remained.

The sandbox image remains as a local build cache by design; it is not runtime state and is rebuilt safely by `make build-sandbox`.
