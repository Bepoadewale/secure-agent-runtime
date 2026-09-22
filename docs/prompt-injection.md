# Prompt injection containment

The malicious fixture asks an agent to export credentials to `attacker.invalid`. Infrastructure makes the instruction ineffective: no master credentials exist in the sandbox, secrets require policy-approved capability, default egress is disabled, attacker host is absent from the allowlist, and the agent cannot mutate its own policy. Run `make demo-security-real` to execute the rejection, redaction, revocation, and blocked-egress scenario; `make demo-security` remains a compatibility alias.
