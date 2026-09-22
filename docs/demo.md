# Demo scenarios

All commands below exercise the local Docker backend; they do not use the fake
backend used by some deterministic unit tests.

## Successful bounded task

`make demo-agent-task` builds the hardened sandbox image and runs a fixture
coding task. The sandbox clones its embedded fixture repository into a
project-owned Docker volume, runs its tests, makes a bounded change, writes a
patch artifact, and is destroyed. The task runs as UID/GID `65532`, with a
read-only root filesystem, dropped Linux capabilities, `no-new-privileges`,
resource limits, no Docker socket, and no host bind mounts.

## Signed API task and restart recovery

`make demo-api` starts the FastAPI control plane, submits a task with a signed
local agent JWT, runs it through the Docker backend, restarts the API process,
and reads the persisted task, audit events, and artifacts from SQLite.

## Network and secret containment

`make demo-containment` proves that a sandbox cannot reach an arbitrary public
destination while a sandbox explicitly assigned to the project-owned internal
allow network can reach the local fixture service.

`make demo-security-real` proves that an ungranted secret request is denied,
a synthetic scoped secret is redacted from output and revoked, and the
prompt-injection fixture cannot exfiltrate it to a public destination.

## Failure and recovery paths

`make demo-timeout` runs a real sleeping sandbox command with a bounded timeout
and verifies that the command exits with the timeout status before the sandbox
is destroyed. `make demo-cancel` cancels an active sandbox task and verifies
cleanup. `make demo-recovery` creates a deliberately labelled abandoned
sandbox resource and verifies that the reaper removes only resources owned by
this project.

## Local observability

`make demo-observability` starts the project-scoped OpenTelemetry Collector,
Jaeger, Prometheus, and Grafana stack. It runs a task and verifies both the
Prometheus task series and an exported `sandbox.execute` trace in Jaeger.

Run `make clean-local` after a demonstration to remove only this repository's
kind cluster, Compose services, labelled sandbox resources, local virtual
environment, and generated local state. It intentionally retains the sandbox
image as a Docker build cache.
