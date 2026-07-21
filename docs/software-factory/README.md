---
id: bz-software-factory-v2-20260719
created: 2026-07-19T14:02:14-04:00
updated: 2026-07-20T20:00:00-04:00
status: PROPOSED_ARCHITECTURE_IMPLEMENTATION_GATED
truth_classification: ACTUAL_RESEARCH_WITH_PROPOSED_BZ_DESIGN
authority: ~/TomorrowAI_OS/runtime/agent_bridge/
---

# BZ Software Factory v2

## Decision

Do not replace the BZ stack with LangChain's stack. Adopt the factory separation it demonstrates and keep every component replaceable behind BZ contracts.

The target production path is:

```text
intent/specification
  -> FirstMate/Pi coordinator
  -> Herdr session + isolated Git worktree
  -> Pi, Grok Build, or another approved worker
  -> deterministic tests and policy gates
  -> independent read-only reviewer
  -> draft pull request
  -> accountable human merge owner
  -> staged rollout, monitoring, and rollback
```

`~/TomorrowAI_OS/runtime/agent_bridge/` remains the authoritative operational source. Repository documentation, OpenWiki output, Obsidian notes, dashboards, and traces are projections or evidence; none may silently override policy.

## What “self-healing” means here

Allowed automatic actions:

- detect failures, drift, stalled agents, unhealthy model endpoints, and evaluation regressions;
- stop or quarantine a run or candidate model;
- roll back to the last approved policy/model/configuration;
- append a sanitized trace and receipt;
- create a bounded issue or draft remediation pull request;
- replay an existing regression suite in a sandbox.

Human approval is required to:

- merge code or policy changes;
- promote a model, quantization, prompt, skill, tool, or routing rule;
- expand permissions, network exposure, or credential scope;
- accept a new license or provenance class;
- change authoritative facts or financial/legal records.

This creates a continuously improving system without allowing an agent to mutate its own controls unchecked.

## Component decision

| Component/pattern | BZ decision | Reason |
|---|---|---|
| Deep Agents / dcode | Learn from; do not add as the default local harness | Pi already owns local/frontier routing; a second default harness increases drift |
| OpenSWE | Defer | Cloud sandboxes, OAuth, triggers, and PR creation expand the control plane too early |
| OpenSWE Review pattern | Pilot read-only after factory contracts exist | Strong bounded-diff, severity/confidence, deduplication, dry-run, and untrusted-trace rules |
| OpenWiki code mode | Pilot on one public-safe repo | Useful derived repo memory and PR updates; generated content must not become authority |
| OpenWiki personal mode/connectors | Reject for now | Duplicates private Obsidian scope and adds OAuth/secret/synchronization risk |
| LangSmith | Optional exporter only | Useful trace/evaluation ideas, but the BZ event contract must remain vendor-neutral |
| OpenInference + OpenTelemetry | Adopt as the interoperability target | Harness/model-neutral trace conventions and portable backends |
| Phoenix | Pilot locally after a data-classification review | Local tracing, datasets, experiments, replay, and evaluations; telemetry must be disabled |
| Imbue Vet | Evaluate as an independent CI check | Reads goal, conversation, repo, and diff; supports OpenAI-compatible endpoints and structured exit codes |
| Ollama | Convenience adapter | Stable localhost API and broad local-model usability |
| llama.cpp server | Reference low-level GGUF adapter | Quantized Apple Silicon inference, OpenAI-compatible routes, monitoring, structured output |
| Hugging Face Hub | Source registry, never blind latest | Pin commits, record license/provenance/hash, and download into quarantine |

## Two governed improvement loops

### Product loop

Intent -> change -> deterministic validation -> independent review -> draft PR -> human merge -> deployment evidence -> incident/regression.

### Factory loop

Sanitized traces + human verdicts -> clustered failure mode -> regression fixture -> proposed prompt/tool/model/routing change -> offline replay -> canary -> independent judge -> human approval -> staged promotion.

The loops share evidence but not authority. A model cannot grade and promote its own change without an independent deterministic or human gate.

## Model onboarding lifecycle

```text
DISCOVERED
 -> QUARANTINED
 -> PROVENANCE_VERIFIED
 -> COMPATIBILITY_VERIFIED
 -> BENCHMARKED
 -> CANARY
 -> APPROVED
 -> ACTIVE
 -> DEPRECATED or ROLLED_BACK
```

Every transition requires evidence. “Latest” model aliases are prohibited in production routing. Pin the Hugging Face revision and artifact SHA-256; record developer, quantizer, license, format, parameter count, context limit, chat template, tool/schema support, memory headroom, serving engine/version, and benchmark result.

The existing policy remains active: Qwen 7B default, Qwen 14B explicit task approval, unknown models denied, and 30B+ blocked. This package does not promote any new model.

## Concurrency rule

Schedule from measured capacity, not agent count. Each machine publishes a capability lease containing free unified memory, loaded model, context allocation, maximum concurrent slots, thermal/power state, disk availability, and lease expiry. The coordinator must refuse work when the lease is absent or stale.

For local inference, start with one generation slot per loaded model. Increase only after measuring latency, context/KV-cache pressure, memory headroom, and output quality. Do not expose Ollama or llama.cpp on `0.0.0.0`; cross-machine portability comes from the approved catalog and model SSD, not an unauthenticated LAN endpoint.

## Implementation order

1. Ratify `factory-contract.yaml`, `trace-event.schema.json`, and `model-onboarding.yaml` through a PR.
2. Add append-only local run receipts and a redaction test before adopting any trace UI.
3. Pilot an independent read-only review on one public-safe BZ repository.
4. Pilot OpenWiki code mode on that same repo with telemetry disabled; review every generated documentation PR.
5. Pilot Phoenix locally against synthetic/public-safe traces only; retain raw JSONL as the portable source.
6. Preserve and audit `AI_MODELS` read-only; do not use it as the authoritative model store. Accept a clean model-artifact store, backup, catalog, and rollback design before downloading or benchmarking a new model.
7. Add model adapters one at a time: llama.cpp first, Ollama second. Both must satisfy the same health and structured-output contract.
8. Add automated quarantine/rollback and issue creation. Keep policy/code/model promotion human-approved.
9. Only after the local line passes acceptance, reconsider background/cloud agents and cross-machine scheduling.

The reconciled fleet sequence and long-running goal design are now specified in `implementation-roadmap.md` and `goal-contract.yaml`. These are proposed contracts, not active services.

## Gates still open

- Fable 5 and ChatGPT architecture judgments were reviewed and incorporated; their added acceptance, lease, fallback-console, power, and credential-scope gates remain implementation prerequisites.
- Herdr acceptance and cmux rollback tests remain incomplete.
- `AI_MODELS` is mapped as a preservation/read-only mixed-content volume, not an authoritative model store; ownership, encryption, backup, and restore gates remain open.
- Portable read-only acceptance inventories remain incomplete for the Studio, M4 Pro, Mini, and Intel nodes.
- The authorized private Obsidian vault and synchronization audience remain unverified.
- Grok Build fork PR workflow has not been locally exercised on this M5.
- Phoenix, OpenWiki, Vet, or any new model has not been installed by this package.

## Package inventory

- `README.md` — architecture decision and rollout.
- `factory-contract.yaml` — authority, roles, gates, and rollback rules.
- `goal-contract.yaml` — harness-neutral durable goals, leases, budgets, checkpoints and stop conditions.
- `implementation-roadmap.md` — reconciled fleet roles and staged machine-by-machine rollout.
- `model-onboarding.yaml` — model lifecycle and evidence requirements.
- `trace-event.schema.json` — sanitized portable run-event schema.
- `source-register.md` — primary sources and X discovery signals.
- `validate_package.sh` — local syntax and safety checks.
- `validation-receipt.md` — recorded validation outcome and non-actions.
