---
id: bz-buzz-pilot-test-plan-v1
status: READY_FOR_LOCAL_EXECUTION
truth_classification: PUBLIC_SAFE
---

# Synthetic pilot test plan

## Objective

Validate the BeyondZero Labs multi-agent Buzz workflow end-to-end using a harmless public repository and synthetic content only.

**Pilot task:**

> Inspect a small sample repository, identify one low-risk improvement, have Codex propose the change, Claude critique it, Cursor implement the accepted version, and a verifier confirm tests and report the result.

## Preconditions

| Requirement | Owner |
|---|---|
| Buzz Desktop v0.5.0+ installed | Bryant |
| BeyondZero community relay configured | Bryant |
| Channels created per [CHANNELS.md](CHANNELS.md) | Bryant |
| Managed agents provisioned per [AGENT_ROLES.md](AGENT_ROLES.md) | Bryant |
| Codex, Claude, Cursor harnesses available on PATH | Bryant |
| Public repo cloned locally (e.g., `apple-silicon-ai-lab`) | Bryant |
| No secrets in repo or Buzz channels | All agents |

## Test repository

**Primary:** `BeyondZeroLabs/apple-silicon-ai-lab` (public, already approved in workspace rules)

**Fallback:** Any public repo with existing tests and < 50 source files.

**Prohibited:** private repos, CASE_BRAIN content, credentials, `.env` files.

## Channel assignments

| Phase | Channel |
|---|---|
| Goal posting | `#dev-command` |
| Role routing | `#agent-coordination` |
| Plan critique | `#review-verification` |
| Implementation discussion | `#dev-command` |
| Verification evidence | `#review-verification` |
| Final decision | `#decisions-receipts` |

## Pilot script

### Phase 0 — Setup verification (5 min)

1. Confirm all agents running in Buzz Desktop Agents panel.
2. Confirm channel membership per [CHANNELS.md](CHANNELS.md) member matrix.
3. Post setup confirmation in `#agent-coordination`:

```text
Pilot PILOT-001 starting. Repository: apple-silicon-ai-lab (public).
Synthetic only. No push/merge/deploy. Status: AWAITING_BRYANT
```

### Phase 1 — Bryant posts goal (1 message)

Post in `#dev-command`:

```text
PILOT-001 — Bounded documentation improvement

Objective: Find one low-risk clarity improvement in docs/buzz-workspace/README.md
Scope: Read-only analysis first; implement only after review approval
Constraints: No secrets, no CASE_BRAIN, no push/merge/deploy
Acceptance: Handoff posted, tests pass if files changed, decision in #decisions-receipts
Prohibited: push, merge, deploy, publish, credential access

@Coordinator please route to Codex Builder for plan, Claude Reviewer for critique.
Status: AWAITING_BRYANT
```

### Phase 2 — Coordinator rewrite

Coordinator posts structured handoff in `#agent-coordination` using [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md), then `@Codex Builder` for plan.

### Phase 3 — Codex proposes plan

Codex Builder posts plan in `#dev-command`:

- file to change;
- exact proposed edit;
- rationale;
- test plan (if any).

Status: `AWAITING_BRYANT` or route to Claude.

### Phase 4 — Claude critiques plan

Claude Reviewer posts in `#review-verification`:

- verified facts vs inferences;
- approve / approve with blockers / reject;
- security and privacy check.

**Must be separate session from Codex.**

### Phase 5 — Bryant selects plan

Bryant replies `APPROVED` or `REJECTED` in `#dev-command`.

### Phase 6 — Cursor implements (if approved)

`@Cursor Engineer` implements bounded change locally.

- Report files changed;
- run relevant tests;
- post handoff with evidence.

### Phase 7 — Verification

Verification Agent (separate session):

- run `python -m pytest tests/` or applicable test command;
- verify file count and diff scope;
- confirm no prohibited actions;
- post evidence in `#review-verification`.

### Phase 8 — Final decision

Post in `#decisions-receipts`:

```text
PILOT-001 FINAL

Status: PASS | PASS_WITH_FOLLOWUPS | REJECTED | BLOCKED
Repository: apple-silicon-ai-lab
Commit: <local-only SHA or "not committed">
Files changed: <list>
Tests: <pass/fail summary>
Agents: Coordinator=<name> Codex=<name> Claude=<name> Cursor=<name> Verifier=<name>
Prohibited actions avoided: push, merge, deploy, publish
Next: <one action>
```

## Acceptance criteria

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Bryant posts task once | Single goal message in `#dev-command` |
| 2 | Shared context without copy-paste | Agents reference same thread content |
| 3 | Roles distinct | Implementer ≠ independent reviewer |
| 4 | Bounded implementation | ≤ 1 file, documentation only |
| 5 | No sensitive data | Synthetic/public only |
| 6 | No push/merge/deploy | Confirmed in handoffs |
| 7 | Verification evidence visible | Test output in `#review-verification` |
| 8 | Final receipt posted | Entry in `#decisions-receipts` |
| 9 | Transcript clarity | Each agent role identifiable |
| 10 | Repeatable | Documented steps succeed on second run |

## Failure handling

| Failure | Action |
|---|---|
| Agent does not respond | Check harness running, `respondTo` allowlist, `@mention` |
| Runaway agent loop | `@mention` discipline; set teammates to `owner-only` |
| Harness crash | Restart agent; check `buzz-acp` logs on stderr |
| Test failure | Status `BLOCKED`; do not merge |
| Secret detected | Status `SECURITY_GATE_REQUIRED`; rotate if real |

## Evidence collection

Record in [PILOT_RESULTS.md](PILOT_RESULTS.md) and `receipts/test-results.md`:

- timestamps per phase;
- agent pubkeys;
- message IDs (if available);
- test command output;
- local commit SHA (if committed locally only);
- screenshots of agent panel (optional).

## Rollback

If pilot fails or must abort, follow [ROLLBACK.md](ROLLBACK.md).
