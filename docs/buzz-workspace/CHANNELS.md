---
id: bz-buzz-channels-v1
status: DOCUMENTATION_ONLY
truth_classification: PUBLIC_SAFE
---

# Buzz channel layout — BeyondZero Labs

## Scope

This document specifies the recommended BeyondZero Labs Buzz channel layout. Channels are the sole access-control boundary in Buzz: membership grants read and write; non-members cannot see private channel listings or subscribe to their events.

**Live status:** Channels are **not yet created** in a verified BeyondZero community from this cloud environment. Bryant must create them in Buzz Desktop after selecting or provisioning a relay.

## How to create channels (manual)

1. Open Buzz Desktop and connect to the BeyondZero Labs community relay.
2. For each channel below: **Create channel** → set name and visibility → add members.
3. Add only the agents and humans required for that channel's purpose.
4. Record creation timestamps and member lists in `receipts/permissions.md`.

### Visibility guidance

| Channel | Recommended visibility | Notes |
|---|---|---|
| `#dev-command` | Private (team) | Development coordination only |
| `#agent-coordination` | Private (team) | Agent routing; minimize human noise |
| `#review-verification` | Private (team) | Independent review surface |
| `#decisions-receipts` | Private (team) | Durable decision log |
| `#local-ai-lab` | Private (team) | Synthetic fixtures only |
| `#bz-university` | Private (team) | Product and curriculum work |
| `#case-brain-private` | Private (restricted) | Synthetic placeholders only until security gate passes |
| `#welcome` | Default (existing) | Confine starter agents here until remapped |

Buzz private channels are invisible to non-members per official `SECURITY.md` and `ARCHITECTURE.md`.

---

## `#dev-command`

**Purpose:** Main development coordination room.

| Allowed | Not allowed |
|---|---|
| Public or approved private development work | CASE_BRAIN evidence |
| Repository-relative paths | Secrets and production credentials |
| Architecture discussions | Unrelated personal information |
| Test output and non-sensitive receipts | Legal, health, or financial records |

**Typical members:** Bryant, Codex Builder agent, Claude Reviewer agent, Cursor Engineer agent (optional), Coordinator agent.

**Usage pattern:** Bryant posts one bounded goal per thread. Coordinator rewrites scope. Implementation and review handoffs reference this thread.

---

## `#agent-coordination`

**Purpose:** Agent assignments, role declarations, work queues, handoff formatting, availability and status.

**Use for:**

- declaring which agent owns implementation, review, verification, research, local execution, or synthesis;
- posting work-queue items with explicit `@mention` targets;
- reporting agent availability (`idle`, `busy`, `blocked`);
- formatting handoffs per [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md).

**Typical members:** Bryant, Coordinator, all active worker agents, Verification Agent.

---

## `#review-verification`

**Purpose:** Independent second-model review, test evidence, privacy and security checks, architecture critique, acceptance or rejection.

**Reviewer discipline:** Distinguish explicitly:

- verified fact;
- reported claim;
- inference;
- unresolved unknown;
- recommendation.

**Typical members:** Bryant, Claude Reviewer, Verification Agent. Implementer agents should **not** be the sole reviewer of their own output.

---

## `#decisions-receipts`

**Purpose:** Final accepted decisions and durable receipts.

**Include:**

- concise decision summary;
- status value (`PASS`, `PASS_WITH_FOLLOWUPS`, etc.);
- commit identifiers and hashes when applicable;
- version identifiers;
- rollback notes;
- approval status;
- unresolved blockers.

**Exclude:** long implementation threads, raw logs, secrets, and sensitive attachments.

---

## `#local-ai-lab`

**Purpose:** Local-model experiments on approved hardware.

**Topics:** Ollama or other approved runtime testing, Goose evaluation, ACP experiments, performance comparison, local-versus-cloud routing tests.

**Constraint:** Synthetic fixtures only until privacy controls are confirmed on the M5 control node.

**Default local coding model:** `qwen2.5-coder:7b`. Larger models require explicit task-level approval per `AGENTS.md`.

---

## `#bz-university`

**Purpose:** BeyondZero University development and learning workflows.

**Topics:** curriculum agents, tutor behavior, mastery tracking, model evaluation, UI and product work.

---

## `#case-brain-private`

**Create only if Buzz private-channel access controls are verified on the target relay.**

**Initial label:**

```text
RESTRICTED — NO REAL CASE DATA UNTIL SECURITY GATE PASSES
```

**Allowed (synthetic only):**

- `CASE_FIXTURE_001`
- `SAMPLE_TIMELINE_EVENT`
- `TEST_EXHIBIT_A`
- `SYNTHETIC_FINANCIAL_RECORD`

**Not allowed:** real case facts, legal documents, medical data, credentials, or production CASE_BRAIN exports.

**Readiness:** See [BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md](BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md). Current decision: `APPROVED_FOR_SYNTHETIC_ONLY`.

---

## Starter channel handling

Buzz provisions a Welcome Team (Fizz, Honey, Bumble) in the default welcome channel. Until remapped:

- keep starter agents confined to `#welcome` or equivalent onboarding channel;
- do not add them to `#case-brain-private` or other restricted channels;
- remap roles per [AGENT_ROLES.md](AGENT_ROLES.md) after inspecting harnesses and permissions.

## Member matrix (fill after local setup)

| Channel | Bryant | Codex | Claude | Cursor | Coordinator | Verifier | Local AI |
|---|---|---|---|---|---|---|---|
| `#dev-command` | owner | member | member | optional | member | — | — |
| `#agent-coordination` | owner | member | member | member | member | member | future |
| `#review-verification` | owner | — | member | — | — | member | — |
| `#decisions-receipts` | owner | read | read | read | member | member | — |
| `#local-ai-lab` | owner | optional | optional | member | — | member | future |
| `#bz-university` | owner | member | member | member | member | — | — |
| `#case-brain-private` | owner | — | — | — | — | — | — |

Record actual pubkeys and membership events in `receipts/permissions.md` after creation.
