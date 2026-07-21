---
id: bz-m5-policy-cockpit-phase-1
status: ACTIVE_INTERACTIVE_PILOT
data_classification: PUBLIC
policy_revision: 094f5a852c90be00c19e5915ae0fd8b45a22826c
---

# M5 policy cockpit — bounded Phase 1 activation

This phase activates an offline policy gate on the M5 without activating the fleet. It implements the human-authority boundary from the ratified Software Factory contracts while leaving Herdr, Pi, Grok Build, model adapters, coordinators, watchdogs and OSIRIS services uninstalled and inactive.

## What is active

- A versioned M5 role policy for one public-safe repository.
- A standard-library CLI that evaluates explicit human approval envelopes.
- Fail-closed gates for public classification, repository allowlisting, evidence completeness and human confirmation.
- Optional append-only receipts stored under ignored `.factory-state/` with create-exclusive writes and owner-only file permissions.
- Deterministic unit tests and a synthetic example request.

An approved result means only `APPROVED_FOR_HUMAN_ACTION`. The CLI never executes a merge, rollback, model action or permission change.

## Explicit non-actions

This phase does not:

- install or start a daemon, harness, model server or login item;
- call GitHub, a model provider, a local model endpoint or any network service;
- read credentials, private data, private operational authorities, synchronized notes or external volumes;
- write to `AI_MODELS`, `OSIRIS_CORE`, `LaCie`, `LACIE1` or any other protected storage;
- coordinate agents, acquire a lease, download a model, promote policy or merge automatically.

## Validate

From the repository root:

```zsh
./scripts/validate_m5_policy_cockpit.sh
```

Evaluate the synthetic request without writing a receipt:

```zsh
python3 scripts/m5_policy_cockpit.py check \
  examples/m5-policy-cockpit/public-safe-approval-request.json
```

Recording is deliberate and local:

```zsh
python3 scripts/m5_policy_cockpit.py record \
  examples/m5-policy-cockpit/public-safe-approval-request.json \
  --human-confirm
```

The separate flag makes receipt creation an explicit operator action rather than an implication of request content. The same request ID cannot be recorded twice. Receipts are ignored by Git and remain non-authoritative pilot evidence; the merged contracts and the designated operational authority retain precedence.

## Rollback

1. Stop using the CLI.
2. Remove the untracked `.factory-state/` directory if its local receipts are no longer required.
3. Revert the Phase 1 Git commit or close its pull request.

No service shutdown, package uninstall, credential revocation, network change or external-drive rollback is required because this phase performs none of those actions.
