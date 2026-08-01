---
id: bz-buzz-receipt-environment-v1
status: CLOUD_DISCOVERY_PASS
truth_classification: PUBLIC_SAFE
---

# Environment receipt

## Assessment context

| Field | Value |
|---|---|
| Assessment date | 2026-08-01 |
| Assessor | Cursor Cloud Agent |
| Repository | BeyondZeroLabs/apple-silicon-ai-lab |
| Branch | cursor/buzz-workspace-setup-6b67 |
| Workspace path | `/workspace` |

## Buzz runtime

| Check | Result |
|---|---|
| `buzz` CLI installed | **No** |
| Buzz Desktop installed | **No** |
| `cursor-agent` on PATH | **Not verified** (not in cloud PATH) |
| `buzz-acp` available | **No** |
| Relay URL configured | **No** |
| BeyondZero community accessible | **No** |

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
