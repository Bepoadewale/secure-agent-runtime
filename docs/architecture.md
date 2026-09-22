# Architecture and trust boundary

**Untrusted:** model output, shell commands, generated code, repositories, build scripts, dependencies, and internet content. **Trusted:** the local control plane, policy, identity validator, secret broker, audit store, and artifact service. The Docker sandbox boundary separates them. MCP/CLI are clients, never authorization bypasses.

One task maps to one sandbox. The control plane owns lifecycle and desired limits; sandbox code cannot select its runtime class, add capabilities, or modify policy. Locally, the API validates a signed fixture JWT and persists lifecycle evidence in SQLite; production identity and distributed worker adapters are documented separately.
