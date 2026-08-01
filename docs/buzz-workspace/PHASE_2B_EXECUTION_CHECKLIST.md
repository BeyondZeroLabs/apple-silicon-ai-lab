---
id: bz-buzz-phase2b-checklist-v1
phase: 2B
status: READY_FOR_BRYANT_EXECUTION
approval: Bryant approved Phase 2 — 2026-08-01
truth_classification: PUBLIC_SAFE
---

# Phase 2B execution checklist — workspace configuration

Execute on M5 in Buzz Desktop. Check each box and record outcomes in `receipts/permissions.md`.

**Prerequisites:** Phase 2A UI inventory recorded in `BUZZ_DISCOVERY_REPORT.md` §14.

**Do not** post real CASE_BRAIN content. Use synthetic fixtures only in `#case-brain-private` after creation.

---

## Step 1 — Verify version and relay (2 minutes)

1. Open **Buzz → About** (or Settings → About).
2. Record exact version string in `receipts/versions.md`.
3. Open **Settings → Communities** (or community rail).
4. Record relay URL and hosting type in `receipts/environment.md`.

---

## Step 2 — Inspect starter agents before remapping (5 minutes)

1. Open **Agents** in sidebar.
2. For each visible agent (Fizz, Honey, Bumble if present), record:

| Field | Record in |
|---|---|
| Name | `receipts/permissions.md` |
| Harness / runtime | `receipts/permissions.md` |
| Model | `receipts/permissions.md` |
| `respondTo` policy | `receipts/permissions.md` |
| Status (running/stopped) | `receipts/permissions.md` |
| Channel memberships | `receipts/permissions.md` |

3. **Confine starters to welcome channels** until inspected:
   - Remove Fizz/Honey/Bumble from any non-welcome channel if present.
   - Keep them in `#Welcome` / `#welcome-everyone` only.

---

## Step 3 — Create recommended channels (10 minutes)

Create **private** channels per [CHANNELS.md](CHANNELS.md):

| Channel | Visibility | Initial members |
|---|---|---|
| `#dev-command` | Private | Bryant only (add agents in Step 4) |
| `#agent-coordination` | Private | Bryant only |
| `#review-verification` | Private | Bryant only |
| `#decisions-receipts` | Private | Bryant only |
| `#local-ai-lab` | Private | Bryant only |
| `#bz-university` | Private | Bryant only |

**Defer** `#case-brain-private` until security gate re-confirmed after harness inspection.

Post one seed message in `#decisions-receipts`:

```text
BeyondZero Labs Buzz workspace configuration started.
Status: AWAITING_BRYANT
Synthetic content only. No CASE_BRAIN data.
```

---

## Step 4 — Create dedicated managed agents (20 minutes)

Create one agent per role. Do **not** overload Fizz/Honey/Bumble for production roles unless prompts are verified editable.

| Agent name | Harness | respondTo | Channels to add |
|---|---|---|---|
| Coordinator | Claude or Buzz Agent | allowlist: Bryant | `#agent-coordination`, `#dev-command` |
| Codex Builder | Codex (tier-1) | allowlist: Bryant, Coordinator | `#dev-command`, `#agent-coordination`, `#bz-university` |
| Claude Reviewer | Claude (tier-1) | allowlist: Bryant, Coordinator | `#review-verification`, `#dev-command` (read) |
| Cursor Engineer | Cursor (`cursor-agent acp`) | allowlist: Bryant, Coordinator | `#dev-command`, `#agent-coordination`, `#local-ai-lab` |
| Verification Agent | Buzz Agent or lightweight harness | allowlist: Bryant, Coordinator | `#review-verification`, `#agent-coordination`, `#decisions-receipts` |

For each agent:

1. **Create agent** → set name, harness, system prompt per [AGENT_ROLES.md](AGENT_ROLES.md).
2. Save identity key per Buzz keyring policy.
3. Set `respondTo` to **allowlist** (not `anyone`).
4. Add to channels listed above.
5. **Start** agent from Agents panel.
6. Record pubkey and harness in `receipts/permissions.md`.

---

## Step 5 — Verify harness availability (5 minutes)

In **Agents → Runtime settings** (or Create agent → Runtime picker), record:

| Runtime | Available? | Notes |
|---|---|---|
| goose | | |
| claude | | |
| codex | | |
| cursor (`cursor-agent acp`) | | |
| buzz-agent | | |

Run on terminal (optional):

```bash
cursor-agent acp --help
```

Record in `receipts/versions.md`.

---

## Step 6 — Mobile pairing check (2 minutes)

1. Open Buzz mobile pairing settings (if present).
2. Record: paired yes/no, method observed, revocation UI present yes/no.
3. Update `receipts/permissions.md` mobile section.

---

## Step 7 — Post configuration receipt

Post in `#decisions-receipts`:

```text
PHASE-2B CONFIGURATION COMPLETE

Channels created: #dev-command #agent-coordination #review-verification
  #decisions-receipts #local-ai-lab #bz-university
Agents created: Coordinator Codex-Builder Claude-Reviewer Cursor-Engineer Verification
Starters confined to welcome: yes/no
CASE_BRAIN channel created: no (deferred)
Status: PASS_WITH_FOLLOWUPS | BLOCKED
Follow-ups: <list>
```

---

## Rollback

If anything fails, follow [ROLLBACK.md](ROLLBACK.md) Level L1–L2 before retrying.

---

## Next phase

After Step 7 passes, approve **Phase 2C** (integration smoke tests) then **Phase 2D** (PILOT-001).
