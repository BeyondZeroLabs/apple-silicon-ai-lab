---
id: bz-buzz-receipt-environment-v1
status: PHASE_2A_PARTIAL
truth_classification: PUBLIC_SAFE
---

# Environment receipt

## Assessment context

| Field | Value |
|---|---|
| Assessment date | 2026-08-01 |
| Assessor | Cursor Cloud Agent + Bryant UI screenshot |
| Repository | BeyondZeroLabs/apple-silicon-ai-lab |
| Branch | cursor/buzz-workspace-setup-6b67 |
| Workspace path | `/workspace` |

## Buzz runtime — cloud VM

| Check | Result | Classification |
|---|---|---|
| `buzz` CLI installed | **No** | `LOCALLY_VERIFIED` |
| Buzz Desktop installed | **No** | `LOCALLY_VERIFIED` |
| `cursor-agent` on PATH | **No** | `LOCALLY_VERIFIED` |
| `buzz-acp` available | **No** | `LOCALLY_VERIFIED` |
| Relay URL configured | **No** | `LOCALLY_VERIFIED` |

## Buzz runtime — M5 (Bryant)

| Field | Value | Classification |
|---|---|---|
| Buzz Desktop running | **Yes** | `REPORTED_BY_UI` |
| Host OS | macOS | `REPORTED_BY_UI` |
| Community display name | `beyondzero-labs` | `REPORTED_BY_UI` |
| Human identity | Bryant (owner) | `REPORTED_BY_UI` |
| Buzz Desktop version | _pending About dialog_ | `UNKNOWN` |
| Relay URL | _pending Settings → Communities_ | `UNKNOWN` |
| Hosted vs self-hosted | _pending relay URL_ | `UNKNOWN` |
| OS keyring backend | macOS Keychain (expected per Buzz SECURITY.md) | `INFERENCE` |

## Cloud agent constraints

Per workspace `AGENTS.md` and cloud task instructions:

- No Buzz installation or runtime activation in cloud VM
- No credentials or protected storage access
- Synthetic/public-safe material only
- Documentation and procedure package is the deliverable

## Intended local environment (M5 control node)

| Component | Expected location |
|---|---|
| Buzz Desktop | Bryant M5 Max |
| Relay | Self-hosted or Block hosted — **TBD by Bryant** |
| Codex harness | `codex-acp` or Buzz tier-1 Codex |
| Claude harness | `claude-agent-acp` |
| Cursor harness | `cursor-agent acp` |
| Local Ollama | M5 — `qwen2.5-coder:7b` default |

## Network

| Check | Result |
|---|---|
| Egress to github.com | Available (docs fetched) |
| Egress to block/buzz raw content | Available |
| Relay WebSocket test | **Not performed** |

## Fill after local setup

| Field | Value |
|---|---|
| Buzz Desktop version | |
| Relay URL | |
| Community name | |
| OS keyring backend | |
| M5 hostname (non-sensitive label) | |
