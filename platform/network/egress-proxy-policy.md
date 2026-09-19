# Domain-aware egress

NetworkPolicy controls IP/port, not complete DNS policy. Production networked profiles route egress through an authenticated proxy that validates destination hosts, rejects localhost/RFC1918/metadata/control-plane CIDRs, logs destination metadata only, and never logs payloads. Default sandbox policy is deny-all.
