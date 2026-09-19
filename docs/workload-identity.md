# Workload identity

Optional SPIFFE/SPIRE assigns a sandbox identity such as `spiffe://agent-runtime.local/tenant/team-a/task/task-123`, enabling mTLS/broker authorization without static credentials. SPIFFE SVIDs are short-lived verifiable workload identity documents; SPIRE attests the workload before issuance. [SPIFFE concepts](https://spiffe.io/docs/latest/spiffe/concepts/)
