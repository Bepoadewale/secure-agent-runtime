# MCP interface

An orchestrator-facing MCP server exposes `submit_task`, `get_task_status`, `cancel_task`, `get_task_events`, `list_task_artifacts`, and `read_task_artifact` as API clients. It never launches Docker/Kubernetes workloads or fetches secrets itself; the runtime control plane remains the authorization/policy boundary.
