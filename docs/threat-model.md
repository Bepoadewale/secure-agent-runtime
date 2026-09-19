# Threat model

Protect host OS, other tenants, control plane, credentials, repositories, APIs, databases, artifacts, audit records, and network from malicious users/agents/repositories/dependencies, prompt injection, escape attempts, credential theft, lateral movement, SSRF, resource exhaustion, fork bombs, disk exhaustion, and crypto mining.

Controls: isolated workspace, finite resource/time limits, deny-by-default network, capability policy, brokered short-lived grants, non-root restricted containers, tenant-scoped API/artifact access, audit/reaper. Containers reduce risk but do not prove escape resistance; use gVisor/microVMs for higher-risk tenants.
