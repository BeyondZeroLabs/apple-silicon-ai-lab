---
id: bz-buzz-workspace-setup-v1
status: DOCUMENTATION_ONLY_NOT_LIVE_CONFIGURED
truth_classification: PUBLIC_SAFE_SETUP_PACKAGE
---

# BeyondZero Labs Buzz workspace setup package

This package documents how to configure Buzz as a secure virtual office for BeyondZero Labs development, multi-agent coordination, independent review, and local-AI experimentation.

## Important boundary

This repository package is **documentation and procedure only**. It does not configure a live Buzz community by itself. A human operator with Buzz Desktop installed must perform channel creation, harness registration, authentication, and pilot execution on an approved machine.

## Authority model

| Surface | Role |
|---|---|
| GitHub repositories | Authoritative code and version history |
| CASE_BRAIN storage | Authoritative legal evidence and structured case facts (not connected in this phase) |
| GBrain | Approved durable institutional memory (quarantined until separate gate passes) |
| Buzz | Coordination, discussion, handoffs, review, and task routing |
| Local filesystem | Temporary workspace only |
| Decision receipts | Committed to an approved repository or designated durable store |

## Package contents

| File | Purpose |
|---|---|
| [BUZZ_OPERATING_MODEL.md](BUZZ_OPERATING_MODEL.md) | Coordination principles and workflow |
| [CHANNELS.md](CHANNELS.md) | Recommended channel layout and rules |
| [AGENT_ROLES.md](AGENT_ROLES.md) | Logical agent roles and boundaries |
| [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) | Standard multi-agent handoff format |
| [BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md](BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md) | Security gate and CASE_BRAIN readiness decision |
| [CURSOR_BUZZ_INTEGRATION.md](CURSOR_BUZZ_INTEGRATION.md) | Cursor ACP integration path and test plan |
| [PILOT_TEST_PLAN.md](PILOT_TEST_PLAN.md) | Synthetic pilot procedure |
| [PILOT_RESULTS.md](PILOT_RESULTS.md) | Pilot execution record (fill after local run) |
| [ROLLBACK.md](ROLLBACK.md) | Disable and unwind steps |
| [receipts/](receipts/) | Environment, version, permission, and test receipts |

## Default deny

During setup and pilot:

- no real CASE_BRAIN evidence, legal documents, medical data, credentials, or financial records;
- no secrets, tokens, OAuth material, or environment files;
- no push, merge, deploy, publish, or external messaging without explicit Bryant approval;
- synthetic or public test material only.

## Quick start for Bryant

1. Install Buzz Desktop v0.5.0 or later from the official Block release channel.
2. Create or select the BeyondZero Labs community on an approved relay.
3. Create channels listed in [CHANNELS.md](CHANNELS.md).
4. Register harnesses per [CURSOR_BUZZ_INTEGRATION.md](CURSOR_BUZZ_INTEGRATION.md) and [AGENT_ROLES.md](AGENT_ROLES.md).
5. Run the synthetic pilot in [PILOT_TEST_PLAN.md](PILOT_TEST_PLAN.md).
6. Record outcomes in [PILOT_RESULTS.md](PILOT_RESULTS.md) and `receipts/`.
7. Do not post real CASE_BRAIN content until [BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md](BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md) records an approved gate beyond synthetic-only.

## Related factory contracts

This package complements the design-only Software Factory Buzz adapter contracts under `docs/software-factory/`. Buzz remains a collaboration and signed-event adapter, not policy, merge, deployment, credential, or memory authority.
