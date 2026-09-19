# Architecture and trust boundary

**Untrusted:** model output, shell commands, generated code, repositories, build scripts, dependencies, and internet content. **Trusted:** control plane, policy, identity, secret broker, provisioner, audit, and artifact service. The sandbox boundary separates them. MCP/CLI are clients, never authorization bypasses.

One task maps to one sandbox. The control plane owns lifecycle and desired limits; sandbox code cannot select its runtime class, add capabilities, or modify policy.
