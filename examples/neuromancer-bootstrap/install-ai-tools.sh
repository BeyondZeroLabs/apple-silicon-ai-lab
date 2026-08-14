#!/usr/bin/env bash
# Idempotent AI tooling installer. Host-guarded. Official sources only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/lib/host-guard.sh"
# shellcheck disable=SC1091
source "${ROOT}/lib/common.sh"

neuromancer_require_host
neuromancer_prepare_local_layout
export DEBIAN_FRONTEND=noninteractive

if ! neuromancer_protect_t2_wifi_packages; then
  neuromancer_say "BLOCKER: apple-firmware missing; refuse AI-tool installs."
  exit 3
fi

if ! neuromancer_need_sudo; then
  exit 4
fi

mkdir -p "${HOME}/.local/bin"

install_cursor_desktop() {
  if command -v cursor >/dev/null 2>&1 || dpkg -s cursor >/dev/null 2>&1; then
    neuromancer_say "CURSOR_DESKTOP=PASS already installed"
    return 0
  fi
  neuromancer_say "INSTALL Cursor desktop from official apt repository"
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://downloads.cursor.com/keys/anysphere.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/cursor.gpg >/dev/null
  echo "deb [arch=amd64,arm64 signed-by=/etc/apt/keyrings/cursor.gpg] https://downloads.cursor.com/aptrepo stable main" | sudo tee /etc/apt/sources.list.d/cursor.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y cursor
  neuromancer_say "CURSOR_DESKTOP=INSTALLED"
}

install_cursor_agent() {
  if command -v cursor-agent >/dev/null 2>&1 || command -v agent >/dev/null 2>&1; then
    neuromancer_say "CURSOR_AGENT=PASS already installed"
    return 0
  fi
  neuromancer_say "INSTALL Cursor CLI from official cursor.com/install"
  curl https://cursor.com/install -fsS | bash
  neuromancer_say "CURSOR_AGENT=INSTALLED"
}

install_codex_cli() {
  if command -v codex >/dev/null 2>&1; then
    neuromancer_say "CODEX_CLI=PASS already installed"
    return 0
  fi
  neuromancer_say "INSTALL Codex CLI from official chatgpt.com installer"
  curl -fsSL https://chatgpt.com/codex/install.sh | CODEX_NON_INTERACTIVE=1 sh
  neuromancer_say "CODEX_CLI=INSTALLED"
}

install_chatgpt_desktop() {
  if command -v chatgpt >/dev/null 2>&1 || dpkg -s chatgpt >/dev/null 2>&1; then
    neuromancer_say "CHATGPT_LINUX_DESKTOP=PASS already installed"
    return 0
  fi
  if [[ -n "${CHATGPT_OFFICIAL_DEB:-}" ]]; then
    if [[ ! -f "${CHATGPT_OFFICIAL_DEB}" ]]; then
      neuromancer_say "CHATGPT_LINUX_DESKTOP=BLOCKED_OFFICIAL_SOURCE_NOT_VERIFIED"
      neuromancer_say "CHATGPT_OFFICIAL_DEB path is not a file"
      return 0
    fi
    local mime
    mime="$(file -b --mime-type "${CHATGPT_OFFICIAL_DEB}" 2>/dev/null || true)"
    if [[ "${mime}" != "application/vnd.debian.binary-package" && "${CHATGPT_OFFICIAL_DEB}" != *.deb ]]; then
      neuromancer_say "CHATGPT_LINUX_DESKTOP=BLOCKED_OFFICIAL_SOURCE_NOT_VERIFIED"
      neuromancer_say "provided file is not a Debian package"
      return 0
    fi
    neuromancer_say "INSTALL ChatGPT desktop from owner-provided official Debian package"
    sudo apt-get install -y "${CHATGPT_OFFICIAL_DEB}"
    neuromancer_say "CHATGPT_LINUX_DESKTOP=INSTALLED"
    neuromancer_say "CHATGPT_LOGIN_HUMAN_GATE"
    return 0
  fi
  neuromancer_say "CHATGPT_LINUX_DESKTOP=BLOCKED_OFFICIAL_SOURCE_NOT_VERIFIED"
  neuromancer_say "Official download surface: https://openai.com/codex/"
  neuromancer_say "This installer does not fetch community-posted package URLs."
  neuromancer_say "EXACT_HUMAN_ACTION: in a local browser open the official OpenAI Linux download page, save the amd64 deb, then rerun with CHATGPT_OFFICIAL_DEB set to that file."
}

install_tailscale() {
  if command -v tailscale >/dev/null 2>&1; then
    neuromancer_say "TAILSCALE=PASS already installed"
  else
    neuromancer_say "INSTALL Tailscale from official Linux installer"
    curl -fsSL https://tailscale.com/install.sh | sh
    neuromancer_say "TAILSCALE=INSTALLED"
  fi
  if tailscale status >/dev/null 2>&1; then
    neuromancer_say "TAILSCALE_AUTH=PRESENT"
  else
    neuromancer_say "TAILSCALE_AUTH_HUMAN_GATE"
    neuromancer_say "EXACT_HUMAN_ACTION: run sudo tailscale up and complete browser auth. Do not paste auth keys into chat."
  fi
}

install_cursor_desktop
install_cursor_agent
install_codex_cli
install_chatgpt_desktop
install_tailscale

neuromancer_say "OLLAMA=DEFER do not download models on this Intel T2 node by default"
neuromancer_say "AI_TOOLS_INSTALL_COMPLETE"
neuromancer_say "CURSOR_AUTH_HUMAN_GATE if cursor-agent status requires login"
neuromancer_say "CODEX_LOGIN_HUMAN_GATE if codex requires ChatGPT browser auth"
exit 0
