# Security model

Identity is distinct for requester, agent, control plane, sandbox, broker, and tool gateway. Agents receive capabilities—not host, Docker, Kubernetes, cloud, database, or GitHub admin credentials. Policy fails closed. Secrets are task/tenant-bound and revoked at termination; values are redacted from output/audit.
