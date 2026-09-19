# Network isolation

Default is no egress. Package installation needs an approved profile plus egress proxy/domain policy; NetworkPolicy alone is IP/port oriented and cannot safely implement arbitrary hostname policy. Block localhost, metadata endpoints, RFC1918, Kubernetes API, control plane, broker, and internal databases to prevent SSRF/lateral movement.
