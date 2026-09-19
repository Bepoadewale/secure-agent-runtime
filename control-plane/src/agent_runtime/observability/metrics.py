from prometheus_client import Counter, Gauge, Histogram

TASKS = Counter("agent_runtime_tasks_total", "Task outcomes", ["tenant", "outcome"])
DENIALS = Counter("agent_runtime_policy_denials_total", "Policy denials", ["reason"])
ACTIVE = Gauge("agent_runtime_active_sandboxes", "Active sandboxes")
EXECUTION = Histogram("agent_runtime_execution_seconds", "Task execution duration")
SECRETS = Counter("agent_runtime_secret_issuance_total", "Secret grants", ["outcome"])
