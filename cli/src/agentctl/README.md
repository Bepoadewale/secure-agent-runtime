# agentctl

The production CLI calls runtime APIs: submit/status/cancel/logs/artifacts/sandbox/policy/profile. It never invokes Docker or Kubernetes directly. The packaged starter client lives in `agent_runtime.cli`.
