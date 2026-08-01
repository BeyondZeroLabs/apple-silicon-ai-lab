---
id: bz-buzz-receipt-permissions-v1
status: PHASE_2A_PARTIAL
truth_classification: PUBLIC_SAFE
---

# Permissions receipt

## Observed channels (2026-08-01 — UI screenshot)

| Channel | Visibility | Bryant member | Notes | Classification |
|---|---|---|---|---|
| `#general` | Regular | Yes | Created by Bryant; no agent messages yet | `REPORTED_BY_UI` |
| `#Welcome` | Private (padlock) | Yes | Default onboarding channel | `REPORTED_BY_UI` |
| `#welcome-everyone` | Regular | Yes | Default onboarding channel | `REPORTED_BY_UI` |

## Recommended channels — not yet created

| Channel | Status |
|---|---|
| `#dev-command` | Not observed |
| `#agent-coordination` | Not observed |
| `#review-verification` | Not observed |
| `#decisions-receipts` | Not observed |
| `#local-ai-lab` | Not observed |
| `#bz-university` | Not observed |
| `#case-brain-private` | Deferred per security gate |

## Human identity

| Field | Value | Classification |
|---|---|---|
| Name | Bryant Crowe | `REPORTED_BY_UI` |
| Role | Owner | `INFERENCE` |
| Display in community | Bryant (bee emoji), `beyondzero-labs` | `REPORTED_BY_UI` |
| Pubkey (hex) | _pending export from Buzz settings_ | `UNKNOWN` |
| MFA | _unknown_ | `UNKNOWN` |

---

## Channel membership matrix

Fill after channel creation. Use `Y` = member, `—` = not member.

| Channel | Bryant | Coordinator | Codex | Claude | Cursor | Verifier | Fizz | Honey | Bumble |
|---|---|---|---|---|---|---|---|---|---|
| `#dev-command` | Y | | | | | | | | |
| `#agent-coordination` | Y | | | | | | | | |
| `#review-verification` | Y | | | | | | | | |
| `#decisions-receipts` | Y | | | | | | | | |
| `#local-ai-lab` | Y | | | | | | | | |
| `#bz-university` | Y | | | | | | | | |
| `#case-brain-private` | Y | — | — | — | — | — | — | — | — |
| `#welcome` | Y | | | | | | | | |

---

## Managed agents

### Coordinator (suggested: dedicated agent or remapped Fizz)

| Field | Value |
|---|---|
| Name | |
| Pubkey | |
| Harness command | |
| Harness args | |
| Model | |
| respondTo | |
| respondToAllowlist | |
| Channels | |

### Codex Builder

| Field | Value |
|---|---|
| Name | |
| Pubkey | |
| Harness | `codex-acp` or Buzz Codex tier-1 |
| Model | |
| respondTo | |
| Channels | |

### Claude Reviewer

| Field | Value |
|---|---|
| Name | |
| Pubkey | |
| Harness | `claude-agent-acp` |
| Model | |
| respondTo | |
| Channels | |

### Cursor Engineer

| Field | Value |
|---|---|
| Name | |
| Pubkey | |
| Harness | `cursor-agent` |
| Args | `acp` |
| respondTo | |
| Channels | |

### Verification Agent

| Field | Value |
|---|---|
| Name | |
| Pubkey | |
| Harness | |
| respondTo | |
| Channels | |

---

## Starter agents (inspect before remapping)

| Agent | Persona ID | Default respondTo | Remapped role | Confined to #welcome? |
|---|---|---|---|---|
| Fizz | builtin:fizz | owner-only | | |
| Honey | builtin:honey | allowlist (Fizz) | | |
| Bumble | builtin:bumble | allowlist (Fizz) | | |

---

## Harness permission notes

Record after local inspection:

| Agent | Shell access | Git write | Network | MCP servers |
|---|---|---|---|---|
| Codex | | | | |
| Claude | | | | |
| Cursor | | | | |
| Verifier | | | | |

---

## Mobile pairing

| Field | Value |
|---|---|
| Mobile client installed | _yes/no_ |
| Pairing method | _fill after test_ |
| Same channel restrictions verified | _yes/no/unknown_ |
| Session revocation tested | _yes/no/unknown_ |

---

## Audit event

| Field | Value |
|---|---|
| Recorded by | |
| Date | |
| Relay URL | |
| Notes | |
