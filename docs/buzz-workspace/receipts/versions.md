---
id: bz-buzz-receipt-versions-v1
status: DOCUMENTED
truth_classification: PUBLIC_SAFE
---

# Version receipt

## Documented component versions

| Component | Documented version | Source | Verified locally |
|---|---|---|---|
| Buzz Desktop on M5 | _pending About dialog_ | `UNKNOWN` | Screenshot does not show version |
| buzz-acp | Matches Buzz repo release | `crates/buzz-acp/README.md` | **No** |
| ACP spec | Current | https://agentclientprotocol.com/ | N/A |
| codex-acp | `@agentclientprotocol/codex-acp` | buzz-acp README | **No** |
| claude-agent-acp | `@agentclientprotocol/claude-agent-acp` | buzz-acp README | **No** |
| cursor-agent | Must support `acp` subcommand | Buzz PR #2773, v0.5.0 BYOH | **No** |
| apple-silicon-ai-lab docs package | v1 (this package) | `docs/buzz-workspace/` | **Yes** |

## Buzz v0.5.0 relevant features

- Bring Your Own Harness (BYOH) catalog (PR #2773)
- Cursor preset: `cursor-agent acp` (tier-2)
- OpenCode preset: `opencode acp`
- Managed agent runtime refactor (PR #2974)
- Session titles from agent and channel name (PR #3028)

## Software Factory adapter (related, separate lane)

| Artifact | Status |
|---|---|
| `config/software-factory/buzz-adapter.json` | Design-only contract (separate branch) |
| Buzz adapter validator | Sealed candidate on `chore/buzz-adapter-r3-repair-1` |

This workspace setup package is **operational documentation**, not the Software Factory adapter contract.

## Fill after local install

```bash
# Run on M5 after Buzz Desktop install
# Buzz Desktop → About → version
cursor-agent --version
cursor-agent acp --help
npm list -g @agentclientprotocol/codex-acp
npm list -g @agentclientprotocol/claude-agent-acp
```

Record output below (redact any tokens):

| Command | Output |
|---|---|
| Buzz Desktop version | |
| cursor-agent --version | |
| codex-acp version | |
| claude-agent-acp version | |
