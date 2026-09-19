package agent_runtime
default allow := false
deny contains "privileged runtime denied" if input.request.privileged
deny contains "hostPath denied" if input.request.host_path
deny contains "Docker socket denied" if input.request.docker_socket
deny contains "host network denied" if input.request.host_network
deny contains "wildcard egress denied" if "network.*" in input.request.capabilities
deny contains "git.push denied" if "git.push" in input.request.capabilities
deny contains "untrusted repo requires gVisor" if input.request.workspace == "malicious-repo" and input.request.runtime_profile != "gvisor-required"
allow if count(deny) == 0
