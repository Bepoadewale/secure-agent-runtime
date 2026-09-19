# gVisor

gVisor adds a userspace kernel boundary for container syscalls and can reduce host-kernel attack surface, with compatibility/performance trade-offs. The provided RuntimeClass selects `runsc`; installation/verification is optional and host-specific. Agents cannot request a weaker class. It is not validated in this repository’s local run.
