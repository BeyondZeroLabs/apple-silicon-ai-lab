---
id: bz-fleet-readiness-design-only
created: 2026-07-29T20:14:00+00:00
status: DESIGN_ONLY_INSTALL_FREE
data_classification: PUBLIC
policy_revision: 2561e4bbbf7a21f9989d11df0e29b54ffae7d266
---

# Fleet readiness — install-free contracts and checklists

This document defines machine readiness contracts for the approved abstract fleet. It implements design-only checklists and fail-closed validation without installing services, binding network listeners, writing protected storage, or activating OpenClaw.

Roles and exclusions are derived from `implementation-roadmap.md`. Comprehension and execution budgets reference `goal-contract.yaml`.

## Approved fleet

| Machine ID | Primary role | Deployment state |
|---|---|---|
| `mbp-m5-max` | Human policy cockpit | Controlled interactive pilot only |
| `mac-studio-m4-max` | Standing coordinator | Proposed production node |
| `mbp-m4-pro` | Mobile executor and explicit-lease failover | Proposed mobile/failover node |
| `mac-mini-m4` | Infrastructure watchdog | Proposed infrastructure node |
| `mbp-intel-2019` | Recovery terminal | Recovery-only candidate |
| `ipad` | Review surface | Review surface |
| `iphone` | Human-presence surface | Human-presence surface |
| `watch` | Notification surface | Notification surface |

## Fleet ceilings

- One active coordinator lease per repository.
- One concurrent goal per repository.
- Model endpoints remain loopback-bound.
- Authenticated model relay is allowed only from `mac-studio-m4-max`.
- Comprehension budgets must reference `goal-contract.yaml:budget`.

## Explicit non-actions

This phase does not:

- install or start Herdr, Pi, Grok Build, OpenClaw, model servers or login items;
- acquire a coordinator lease or activate OSIRIS;
- call GitHub, model providers or remote services;
- write to external volumes or protected storage;
- expose remote listeners or synchronize mutable runtime state.

OpenClaw remains inactive on the Mac mini. No relay node other than the Studio candidate is approved.

## Validate

From the repository root:

```zsh
python3 scripts/validate_fleet_readiness.py
python3 -m unittest tests.test_fleet_readiness -v
```

The validator is fail-closed for fleet ceilings, role exclusions, install/service/network/storage authority prohibitions, mobile limitations, and comprehension budget references.

## Rollback

1. Stop using the validator output as an acceptance gate.
2. Revert the fleet-readiness Git commit or close its pull request.

No service shutdown, package uninstall, credential change, network change or external-drive rollback is required because this phase performs none of those actions.
