# Interview guide

Docker is a packaging boundary, not automatically a sufficient hostile-code boundary; seccomp, dropped capabilities, non-root, read-only filesystems, no sockets, no mounts, cgroups, PID limits, and network denial reduce risk. gVisor changes syscall mediation trade-offs; Firecracker provides microVM/KVM isolation at higher startup/operations cost.

Explain capability-based access, workload identity/SPIFFE, brokered short-lived credentials, deny egress, SSRF blocks, output/artifact boundaries, fork-bomb/resource limits, idempotent cleanup/reaper, durable queues, and why MCP is a client interface rather than the security boundary. For 10k sandboxes discuss cells, queues, placement, image caches, artifact storage, quotas, warm pools, and regional control planes. Do not build user Dockerfiles through a privileged host socket; use isolated/rootless build systems.
