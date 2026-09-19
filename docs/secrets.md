# Secret broker

The demo broker issues only a task-bound `test-api-token` for an authorized capability with a ten-minute TTL, injects it only at execution, redacts it from output, and revokes it on termination. Production adapters use Vault dynamic credentials and workload identity; never inject master credentials or user SSH/AWS/Kubernetes directories.
