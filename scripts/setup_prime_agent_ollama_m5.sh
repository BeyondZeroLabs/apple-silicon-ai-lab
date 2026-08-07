#!/usr/bin/env bash
# Configure Prime Agent for local Ollama on Apple Silicon (M5).
# Idempotent: safe to re-run. Does not modify Homebrew's `pi` binary.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup_prime_agent_ollama_m5.sh [prime-agent-repo]

Configures ~/.prime/agent for Ollama-only use and installs a `prime-agent`
symlink (not `pi`) into ~/.local/bin.

Arguments:
  prime-agent-repo   Path to a built prime-agent clone. When omitted, uses
                     PRIME_AGENT_REPO or ./prime-agent relative to this script.

Environment:
  PRIME_AGENT_REPO   Override the repo path.
  FORCE_CONFIG=1     Overwrite existing ~/.prime/agent/models.json and settings.json.

Prerequisites:
  - Node.js and npm
  - Ollama listening on http://localhost:11434
  - prime-agent repo cloned and built (`npm run build` in repo root)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PRIME_AGENT_REPO="${1:-${PRIME_AGENT_REPO:-${REPO_ROOT}/prime-agent}}"
CLI_BUNDLE="${PRIME_AGENT_REPO}/packages/coding-agent/dist/bundle/cli.js"
CONFIG_SRC="${REPO_ROOT}/config/prime-agent"
AGENT_DIR="${HOME}/.prime/agent"
LOCAL_BIN="${HOME}/.local/bin"
PRIME_AGENT_BIN="${LOCAL_BIN}/prime-agent"

echo "==> Prime Agent Ollama setup"
echo "    repo:       ${PRIME_AGENT_REPO}"
echo "    config dir: ${AGENT_DIR}"
echo "    binary:     ${PRIME_AGENT_BIN}"

if [[ ! -d "${PRIME_AGENT_REPO}/packages/coding-agent" ]]; then
  echo "error: prime-agent repo not found at ${PRIME_AGENT_REPO}" >&2
  echo "       clone PrimeIntellect-ai/prime-agent and pass the path, or set PRIME_AGENT_REPO." >&2
  exit 1
fi

echo "==> Verifying build"
(
  cd "${PRIME_AGENT_REPO}"
  npm run build
)

if [[ ! -f "${CLI_BUNDLE}" ]]; then
  echo "error: bundled CLI missing at ${CLI_BUNDLE}" >&2
  exit 1
fi

mkdir -p "${AGENT_DIR}" "${LOCAL_BIN}"

install_config() {
  local name="$1"
  local dest="${AGENT_DIR}/${name}"
  if [[ -f "${dest}" && "${FORCE_CONFIG:-0}" != "1" ]]; then
    echo "    keeping existing ${dest} (set FORCE_CONFIG=1 to overwrite)"
    return
  fi
  cp "${CONFIG_SRC}/${name}" "${dest}"
  echo "    wrote ${dest}"
}

echo "==> Installing Ollama config templates"
install_config models.json
install_config settings.json

echo "==> Installing prime-agent CLI symlink (leaving Homebrew pi untouched)"
if command -v pi >/dev/null 2>&1; then
  echo "    Homebrew pi: $(command -v pi)"
fi
ln -sf "${CLI_BUNDLE}" "${PRIME_AGENT_BIN}"
chmod +x "${CLI_BUNDLE}"
echo "    linked ${PRIME_AGENT_BIN} -> ${CLI_BUNDLE}"

if ! echo ":${PATH}:" | grep -q ":${LOCAL_BIN}:"; then
  echo "note: add ${LOCAL_BIN} to PATH if prime-agent is not found"
fi

echo "==> Clearing AWS/Bedrock env vars for this session"
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_BEARER_TOKEN_BEDROCK AWS_REGION

echo "==> Smoke test (requires Ollama + default model)"
set +e
SMOKE_OUTPUT="$(
  PI_OFFLINE=1 "${PRIME_AGENT_BIN}" --offline -p "Reply with exactly: OK" 2>&1
)"
SMOKE_STATUS=$?
set -e
echo "${SMOKE_OUTPUT}"

if [[ "${SMOKE_STATUS}" -eq 0 ]]; then
  echo "==> Smoke test passed"
else
  echo "==> Smoke test failed (exit ${SMOKE_STATUS})"
  echo "    Ensure Ollama is running and the default model is available:"
  echo "      ollama serve"
  echo "      ollama pull qwen3.5:35b-a3b-coding-nvfp4"
  exit "${SMOKE_STATUS}"
fi

cat <<EOF

Setup complete.

Binary:      ${PRIME_AGENT_BIN}
Config:      ${AGENT_DIR}/models.json
             ${AGENT_DIR}/settings.json
Default:     ollama / qwen3.5:35b-a3b-coding-nvfp4 @ http://localhost:11434/v1

pi conflict: Homebrew pi remains at $(command -v pi 2>/dev/null || echo 'not installed').
             Use prime-agent for Prime Agent; use pi for upstream pi-coding-agent.

Interactive:
  cd /path/to/your/project
  PI_OFFLINE=1 prime-agent --offline

Non-interactive:
  PI_OFFLINE=1 prime-agent --offline -p "your prompt"

Other models:
  PI_OFFLINE=1 prime-agent --offline --model qwen2.5-coder:7b -p "quick task"
EOF
