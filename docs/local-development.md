# Local development

`make test` uses a fake backend solely to test control-plane behavior. `make demo` uses the same deterministic test path. The actual Docker backend is used by the API when `POST /run` is called and requires a locally built `agent-runtime-sandbox:local` image; build it with `docker build -t agent-runtime-sandbox:local sandbox/images`.

`make bootstrap-local` creates a kind cluster and deploys the control-plane chart. gVisor, Vault, SPIRE, and Firecracker are optional; do not install them merely to satisfy a demo. The local container mode is Level 1 only.
