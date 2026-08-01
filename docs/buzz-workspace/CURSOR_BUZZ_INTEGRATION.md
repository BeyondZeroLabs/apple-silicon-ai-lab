---
id: bz-cursor-buzz-integration-v1
status: DOCUMENTED_NOT_VERIFIED
truth_classification: PUBLIC_SAFE
integration_verdict: DOCUMENTED_PATH_AVAILABLE_VERIFICATION_PENDING
---

# Cursor ↔ Buzz integration

## Summary

Buzz Desktop **v0.5.0+** supports Cursor through the **Bring Your Own Harness (BYOH)** tier-2 preset catalog. The documented integration path is:

```text
command: cursor-agent
args:    acp
```

This uses the Agent Client Protocol (ACP) over stdio, the same seam as Codex and Claude Code.

**Integration verdict:** Documented path available; **not verified** in the cloud agent environment (Buzz and `cursor-agent` not installed).

---

## Supported integration paths

| Path | Status | Notes |
|---|---|---|
| Native Buzz harness preset (tier-2) | **Documented** | `cursor-agent acp` in `PRESET_HARNESSES` |
| ACP via `buzz-acp` standalone | **Documented** | Set `BUZZ_ACP_AGENT_COMMAND=cursor-agent` |
| `cursor-agent` direct | **Documented** | Requires Cursor CLI installed on PATH |
| Custom harness JSON (tier-3) | **Supported** | `custom_harnesses/*.json` in Buzz Desktop |
| Native Buzz-only agent (no ACP) | **Not applicable** | Cursor requires ACP bridge |

**Official sources:**

- https://github.com/block/buzz/releases/tag/v0.5.0
- https://github.com/block/buzz/pull/2773 (BYOH catalog)
- https://github.com/block/buzz/pull/2418 (Cursor runtime, superseded by BYOH)
- https://github.com/block/buzz/blob/main/crates/buzz-acp/README.md

---

## Exact setup steps (Buzz Desktop)

### Prerequisites

1. Buzz Desktop **v0.5.0 or later** installed from official Block release channel.
2. Cursor CLI (`cursor-agent`) installed and on `PATH`.
3. Verify ACP entrypoint:

```bash
cursor-agent acp --help
```

4. BeyondZero Labs community relay configured in Buzz Desktop.
5. Bryant human identity authenticated (Nostr key in OS keyring).

### Create Cursor Engineer managed agent

1. Open Buzz Desktop → **Agents** → **Create agent**.
2. Set name: `Cursor Engineer` (or team convention).
3. Select runtime: **Cursor** from harness gallery (tier-2 preset).
   - If not on PATH, Buzz shows install hint with docs link.
4. Configure:
   - **respondTo:** `allowlist` — Bryant pubkey + Coordinator pubkey
   - **System prompt:** implementation-focused; must not self-review
   - **Model:** per Cursor subscription/policy
5. Save agent identity key per Buzz keyring policy.
6. Add agent to channels: `#dev-command`, `#agent-coordination`, `#local-ai-lab`.
7. Start agent from Agents panel.

### Alternative: standalone buzz-acp

For headless or scripted use:

```bash
export BUZZ_PRIVATE_KEY="nsec1..."   # agent key — never commit
export BUZZ_RELAY_URL="wss://<relay-host>"
export BUZZ_ACP_AGENT_COMMAND="cursor-agent"
export BUZZ_ACP_AGENT_ARGS="acp"
export BUZZ_ACP_RESPOND_TO="allowlist"
export BUZZ_ACP_RESPOND_TO_ALLOWLIST="<bryant-pubkey-hex>"

buzz-acp
```

---

## Required dependencies

| Dependency | Version | Source |
|---|---|---|
| Buzz Desktop | ≥ 0.5.0 | https://github.com/block/buzz/releases |
| cursor-agent CLI | Current stable | Cursor official install |
| Buzz relay | Compatible with desktop | Self-hosted or hosted |
| OS keyring | Platform default | macOS Keychain / Secret Service |

**Do not install** unverified third-party ACP wrappers unless Bryant explicitly approves after source inspection.

---

## Security implications

| Topic | Implication |
|---|---|
| File exposure | Cursor agent may read repository files within its project scope and send content to Cursor cloud per Cursor policy |
| Shell access | Subject to Cursor agent tool permissions — verify on Bryant's machine |
| Network access | Cursor cloud inference; unrestricted local network per Cursor config |
| Credentials | Do not store API keys in Buzz messages; Cursor uses its own auth |
| Buzz identity | `BUZZ_MANAGED_AGENT` and private keys cannot be overridden via harness env |
| Channel scope | Agent sees only member channel history |
| Independent review | Cursor session must not also serve as Claude Reviewer for same change |

---

## Test procedure (synthetic pilot)

Perform on M5 with a **public or synthetic** repository (e.g., `apple-silicon-ai-lab`).

### Pre-test checklist

- [ ] `cursor-agent acp --help` succeeds
- [ ] Buzz Desktop shows Cursor runtime as **Available**
- [ ] Cursor Engineer agent created and running
- [ ] Agent added to `#dev-command` and `#local-ai-lab`
- [ ] No secrets in repository or channel history

### Test steps

1. Bryant posts in `#dev-command`:

```text
@Cursor Engineer Pilot task: read README.md only. Propose one typo or clarity fix.
Do not commit, push, or modify files. Reply with file path and suggested change only.
Status: AWAITING_BRYANT
```

2. Confirm Cursor agent responds in-channel without manual copy-paste of prior messages.
3. Claude Reviewer (separate agent/session) critiques the proposal in `#review-verification`.
4. If Bryant approves, Cursor implements bounded change locally.
5. Verification Agent runs tests and posts evidence.
6. Record final status in `#decisions-receipts`.

### Observations to record

| Item | Record in |
|---|---|
| Response latency | `PILOT_RESULTS.md` |
| Files read by agent | `PILOT_RESULTS.md` |
| Credentials printed? (must be no) | `receipts/test-results.md` |
| Cancellation (`!cancel`) works? | `receipts/test-results.md` |
| Timeout behavior | `receipts/test-results.md` |
| Output returned to Buzz channel? | `receipts/test-results.md` |

---

## Acceptance criteria

| Criterion | Required |
|---|---|
| Cursor preset visible in Buzz Desktop v0.5.0+ | Yes |
| `cursor-agent acp` starts without error | Yes |
| Agent responds to `@mention` in member channel | Yes |
| Agent output appears in Buzz without manual relay | Yes |
| No credentials in stdout/stderr/channel | Yes |
| File exposure limited to stated project scope | Yes |
| `!cancel` stops in-flight turn | Yes |
| Independent reviewer is separate session | Yes |
| No push/merge/deploy during pilot | Yes |

---

## Version compatibility

| Component | Documented compatible version |
|---|---|
| Buzz Desktop | v0.5.0+ |
| buzz-acp | Bundled with Buzz repo; matches desktop version |
| cursor-agent | Must support `acp` subcommand (verify with `--help`) |
| ACP spec | https://agentclientprotocol.com/ |

---

## Permissions inspection

Before production use, record in `receipts/permissions.md`:

1. Cursor project root configured for agent.
2. Tool list enabled for Cursor agent session.
3. Network egress policy on M5.
4. Whether Cursor cloud or local model is used.
5. Buzz `respondTo` policy on managed agent.

---

## Cancellation and timeout

Per `buzz-acp` documentation:

| Control | Behavior |
|---|---|
| `!cancel` | Cancels current in-flight turn for channel (owner only) |
| `!rotate` | Invalidates ACP session; next event starts fresh session |
| `!shutdown` | Gracefully exits harness |
| `BUZZ_ACP_IDLE_TIMEOUT` | Default 620s silence before cancel |
| `BUZZ_ACP_MAX_TURN_DURATION` | Default 7200s wall-clock cap |

Cursor-specific cancel behavior must be verified during local pilot.

---

## How agent output returns to Buzz

1. Relay delivers `@mention` event to `buzz-acp` over WebSocket.
2. Harness batches events into ACP `session/prompt`.
3. Cursor agent processes prompt; may invoke tools.
4. Agent uses Buzz CLI (`send_message`, etc.) injected by harness.
5. Signed agent message persists on relay and fans out to channel members.

---

## Rollback

See [ROLLBACK.md](ROLLBACK.md). Cursor-specific steps:

1. Stop Cursor Engineer managed agent in Buzz Desktop.
2. Remove agent from sensitive channels.
3. Delete managed agent (optional; preserves relay history).
4. Unset `BUZZ_ACP_AGENT_COMMAND` if using standalone harness.
5. Remove `cursor-agent` from PATH or uninstall Cursor CLI if desired.

---

## Blocked alternatives (not recommended without review)

| Path | Status |
|---|---|
| `blowmage/cursor-agent-acp-npm` third-party wrapper | Not inspected; use official `cursor-agent acp` first |
| OpenClaw Gateway bridge | Different execution locus; env vars do not propagate from Desktop |
| Custom shell install scripts | Buzz explicitly disallows in preset definitions |

---

## Current status

| Item | Status |
|---|---|
| Official integration path identified | Yes |
| Version compatibility documented | Yes |
| Local smoke test executed | **No** — cloud VM lacks Buzz and Cursor CLI |
| Bryant acceptance | Pending local pilot |
