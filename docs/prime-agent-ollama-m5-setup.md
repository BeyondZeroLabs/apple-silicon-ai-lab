# Prime Agent (Ollama) on M5

Local-first setup for [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent) using Ollama only. This keeps Homebrew `pi` (`@mariozechner/pi-coding-agent`) separate from Prime Agent by installing the CLI as `prime-agent`.

## Quick setup

From a clone of this repo with `prime-agent` checked out alongside it (or pass the repo path):

```bash
chmod +x scripts/setup_prime_agent_ollama_m5.sh
PRIME_AGENT_REPO=/path/to/prime-agent scripts/setup_prime_agent_ollama_m5.sh
```

The script:

1. Runs `npm run build` in the prime-agent repo
2. Copies `config/prime-agent/{models.json,settings.json}` into `~/.prime/agent`
3. Symlinks `~/.local/bin/prime-agent` to `packages/coding-agent/dist/bundle/cli.js`
4. Runs `PI_OFFLINE=1 prime-agent --offline -p "Reply with exactly: OK"`

Set `FORCE_CONFIG=1` to overwrite existing config files.

## Config layout

| Path | Purpose |
|------|---------|
| `~/.prime/agent/models.json` | Ollama provider + M5 model catalog |
| `~/.prime/agent/settings.json` | Default provider/model |
| `~/.local/bin/prime-agent` | CLI entrypoint (not `pi`) |

Default model: `qwen3.5:35b-a3b-coding-nvfp4` via `http://localhost:11434/v1`.

Registered models:

- `qwen3.5:35b-a3b-coding-nvfp4` (default)
- `qwen3-coder:30b`
- `qwen2.5-coder:7b`

Do not set AWS/Bedrock environment variables for this profile. Prime Agent reads `~/.prime/agent`, not `~/.pi/agent`.

## `pi` vs `prime-agent`

Homebrew installs upstream Pi as `pi`. Prime Agent is a separate fork with its own config directory and runtime. This setup intentionally does **not** replace Homebrew `pi`.

| Command | Binary | Config |
|---------|--------|--------|
| `pi` | Homebrew `@mariozechner/pi-coding-agent` | `~/.pi/agent` |
| `prime-agent` | Local symlink to prime-agent bundle | `~/.prime/agent` |

## Usage

Offline startup (skip update/network checks):

```bash
export PI_OFFLINE=1
prime-agent --offline
```

Interactive session in a project directory:

```bash
cd /path/to/project
PI_OFFLINE=1 prime-agent --offline
```

Non-interactive one-shot:

```bash
PI_OFFLINE=1 prime-agent --offline -p "Summarize README.md"
```

Switch models for a single run:

```bash
PI_OFFLINE=1 prime-agent --offline --model qwen2.5-coder:7b -p "small fix"
```

List configured models:

```bash
PI_OFFLINE=1 prime-agent --offline model list
```

## Prerequisites

- Ollama running locally (`ollama serve`)
- Default model pulled: `ollama pull qwen3.5:35b-a3b-coding-nvfp4`
- `~/.local/bin` on `PATH`
- Built prime-agent repo (`npm install` + `npm run build` at repo root)

## References

- Prime Agent models: `packages/coding-agent/docs/models.md`
- Prime Agent usage: `packages/coding-agent/docs/usage.md`
