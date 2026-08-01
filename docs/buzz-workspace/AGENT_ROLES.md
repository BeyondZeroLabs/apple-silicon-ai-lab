---
id: bz-buzz-agent-roles-v1
status: DOCUMENTATION_ONLY
truth_classification: PUBLIC_SAFE
---

# Agent roles — BeyondZero Labs Buzz workspace

## Scope

Logical roles for the BeyondZero Labs Buzz workspace. Each role maps to one or more **managed agents** in Buzz Desktop with a distinct Nostr identity, harness, system prompt, and channel membership.

**Live status:** Agents are **not yet provisioned** in a verified BeyondZero community from this cloud environment.

## Role summary

| Role | Primary harness | Responds to | Write access |
|---|---|---|---|
| Bryant Crowe (owner) | Human | — | Full human authority |
| Coordinator | Buzz-managed or Claude | Bryant, team | Buzz messages only |
| Codex Builder | Codex via `codex-acp` | Bryant, Coordinator | Repo via Codex tools; no autonomous push |
| Claude Reviewer | Claude via `claude-agent-acp` | Bryant, Coordinator | Review comments; no implementation by default |
| Cursor Engineer | Cursor via `cursor-agent acp` | Bryant, Coordinator | Local repo via Cursor; no autonomous push |
| Verification Agent | Buzz Agent or lightweight harness | Bryant, Coordinator | Test execution; no code authorship |
| Local AI Analyst | Ollama / approved local runtime | Bryant only | Read-only by default |

---

## Bryant Crowe — Owner and final authority

**Responsibilities:**

- sets goals and approves sensitive scope;
- resolves disagreements;
- authorizes irreversible actions;
- decides what becomes authoritative.

**Buzz configuration:** Human account with owner privileges on the community relay. Identity key stored in OS keyring per Buzz `SECURITY.md`.

---

## Coordinator

**Suggested mapping:** Fizz (if harness and prompt are safely editable) or a dedicated managed agent.

**Responsibilities:**

- rewrite Bryant goals into structured objectives;
- route work to Codex, Claude, Cursor, or Verification;
- enforce handoff format;
- prevent implementer/reviewer role collapse.

**Default `respondTo`:** `allowlist` — Bryant and designated team pubkeys only.

**System prompt essentials:**

```text
You are the BeyondZero Labs coordination agent. Rewrite goals into objective, scope,
constraints, acceptance criteria, prohibited actions, and evidence required. Route work
to the correct specialist agent. Never implement code yourself when a builder agent is
available. Never approve your own work as final. Require explicit Bryant approval for
push, merge, deploy, publish, or external messaging.
```

---

## Codex Builder

**Harness:** OpenAI Codex via `@agentclientprotocol/codex-acp` or Buzz tier-1 Codex runtime.

**Responsibilities:** implementation, repository analysis, tests, patches, structured technical plans, automation scripts, evidence-backed completion receipts.

**Default behavior:**

- work from repository truth;
- inspect before changing;
- minimize changes;
- run relevant tests;
- report exact files changed;
- distinguish completion from recommendation.

**Channel membership:** `#dev-command`, `#agent-coordination`, `#bz-university` (as needed).

**Prohibited without Bryant approval:** push, merge, deploy, publish, credential access.

---

## Claude Reviewer

**Harness:** Claude Code via `@agentclientprotocol/claude-agent-acp`.

**Responsibilities:** independent review, adversarial critique, architecture analysis, privacy review, detection of unsupported claims.

**Default behavior:**

- do not simply agree;
- inspect the same evidence independently;
- identify blockers and unknowns;
- recommend approve, approve with blockers, or reject.

**Channel membership:** `#dev-command` (read), `#review-verification`, `#agent-coordination`.

**Must not:** implement changes in the same session that reviews them when independent verification is required.

---

## Cursor Engineer

**Harness:** Cursor via tier-2 preset `cursor-agent acp` (Buzz Desktop v0.5.0+).

**Responsibilities:** interactive code changes, repository navigation, local implementation, debugging, refactoring, integration work, tool execution coordination.

**Channel membership:** `#dev-command`, `#agent-coordination`, `#local-ai-lab`, `#bz-university`.

**Integration status:** Documented, not verified in cloud. See [CURSOR_BUZZ_INTEGRATION.md](CURSOR_BUZZ_INTEGRATION.md).

---

## Verification Agent

**Suggested mapping:** Bumble (if safely reconfigured) or dedicated Buzz Agent harness.

**Responsibilities:**

- run tests and verify file counts;
- verify hashes, build, and lint;
- inspect console output;
- inspect privacy boundaries;
- confirm no unauthorized network, publication, deployment, or credential activity.

**Must not:** be the same active session that authored changes when independent verification is practical.

**Channel membership:** `#review-verification`, `#agent-coordination`, `#decisions-receipts`.

---

## Local AI Analyst (future)

**Harness:** Approved local runtime (Ollama on M5) behind a reviewed adapter.

**Responsibilities:** private local summarization, classification, low-risk drafting, data extraction, offline reasoning.

**Default:** read-only; no write access; no channel membership beyond `#local-ai-lab` until privacy gate passes.

---

## Starter agents — inspection and mapping

Buzz auto-provisions a Welcome Team from built-in personas (`desktop/src/features/onboarding/welcomeGuide.ts`):

| Starter | Persona ID | Default role | Suggested BZ mapping |
|---|---|---|---|
| Fizz | `builtin:fizz` | lead | Coordinator (if prompt editable) |
| Honey | `builtin:honey` | teammate | Reviewer or Synthesizer |
| Bumble | `builtin:bumble` | teammate | Verification or Onboarding Assistant |

### Inspection checklist (perform locally)

For each starter agent, record in `receipts/permissions.md`:

| Property | How to inspect |
|---|---|
| Harness | Buzz Desktop → Agents → select agent → Runtime / Command |
| Model | Agent settings → Model / Provider |
| System behavior | Agent settings → System prompt |
| Accessible channels | Channel member list |
| Local tool access | Harness tool surface (MCP servers, CLI tools) |
| Repository access | Harness working directory and git permissions |
| Shell access | Harness documentation; Cursor/Codex/Claude tool policies |
| Network access | Harness and provider data-flow docs |
| Create other agents | Owner-only in Buzz Desktop settings |
| Persistence | Relay-stored messages; local agent config files |
| Disable / delete | Buzz Desktop → Agents → Stop / Delete |

### Default starter configuration (from official source)

Welcome starters are created with:

- `teamId`: `builtin-team:welcome`
- `respondTo`: `owner-only` (teammates later allowlist Fizz's pubkey)
- `spawnAfterCreate`: false
- `startOnAppLaunch`: false

Teammates Honey and Bumble are configured to respond only to Fizz (allowlist) during welcome kickoff.

### Safe mapping procedure

1. Inspect each starter's harness, model, and prompt in Buzz Desktop.
2. If prompts are editable: remap per table above.
3. If not safely editable: leave disabled or confined to `#welcome`.
4. Create dedicated managed agents for Codex Builder, Claude Reviewer, and Cursor Engineer rather than overloading starters.

---

## Agent creation procedure (manual)

1. **Generate keypair** (per agent): `buzz-admin generate-key` on self-hosted relay, or use Buzz Desktop managed-agent key generation.
2. **Register relay member:** `buzz-admin add-member --pubkey <agent pubkey>`.
3. **Create managed agent** in Buzz Desktop: name, harness, model, system prompt, `respondTo` policy.
4. **Add to channels** per [CHANNELS.md](CHANNELS.md).
5. **Record** pubkey, harness command, and channel membership in `receipts/permissions.md`.

## Multi-agent context sharing

Agents in the same channel receive shared context through **channel message history** on the relay. No manual copy-paste is required when:

- all participating agents are channel members;
- work is conducted in the same channel thread;
- agents are invoked via `@mention` with sufficient prior context in the channel.

This model is **documented** per Buzz architecture; local pilot verification is required. See [PILOT_TEST_PLAN.md](PILOT_TEST_PLAN.md).
