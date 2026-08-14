#!/usr/bin/env bash
# Idempotent core developer tooling installer. Host-guarded. No secrets.
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
  neuromancer_say "BLOCKER: apple-firmware missing; refuse package changes that could affect T2 Wi-Fi."
  exit 3
fi
neuromancer_refuse_wifi_hazards

if ! neuromancer_need_sudo; then
  exit 4
fi

apt_install_if_missing() {
  local pkg="$1"
  if dpkg -s "${pkg}" >/dev/null 2>&1; then
    neuromancer_say "SKIP apt ${pkg} already installed"
    return 0
  fi
  neuromancer_say "INSTALL apt ${pkg}"
  sudo apt-get install -y --no-install-recommends "${pkg}"
}

neuromancer_say "APT_UPDATE"
sudo apt-get update -y

CORE_PACKAGES=(
  git
  curl
  wget
  jq
  ripgrep
  fd-find
  build-essential
  pkg-config
  cmake
  python3
  python3-venv
  python3-pip
  pipx
  ca-certificates
  gnupg
)

for pkg in "${CORE_PACKAGES[@]}"; do
  apt_install_if_missing "${pkg}"
done

if dpkg -s gh >/dev/null 2>&1 || command -v gh >/dev/null 2>&1; then
  neuromancer_say "SKIP gh already present"
else
  if apt-cache policy gh 2>/dev/null | grep -q 'Candidate: .*[0-9]'; then
    apt_install_if_missing gh
  else
    neuromancer_say "INSTALL gh from official GitHub apt repository"
    sudo mkdir -p -m 755 /etc/apt/keyrings
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
    sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
    sudo apt-get update -y
    apt_install_if_missing gh
  fi
fi

if command -v node >/dev/null 2>&1; then
  neuromancer_say "SKIP node already present"
else
  apt_install_if_missing nodejs
  apt_install_if_missing npm || true
fi

if command -v corepack >/dev/null 2>&1; then
  corepack enable >/dev/null 2>&1 || true
  corepack prepare pnpm@latest --activate >/dev/null 2>&1 || true
  neuromancer_say "COREPACK_ENABLED"
fi

if command -v uv >/dev/null 2>&1; then
  neuromancer_say "SKIP uv already present"
else
  neuromancer_say "INSTALL uv official installer"
  curl -fsSL https://astral.sh/uv/install.sh | sh
fi

if command -v rustc >/dev/null 2>&1 && command -v cargo >/dev/null 2>&1; then
  neuromancer_say "SKIP rust already present"
else
  neuromancer_say "INSTALL rustup official installer"
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
fi

mkdir -p "${HOME}/.local/bin"
case ":${PATH}:" in
  *":${HOME}/.local/bin:"*) ;;
  *)
    if [[ -f "${HOME}/.bashrc" ]] && ! grep -q 'HOME/.local/bin' "${HOME}/.bashrc"; then
      printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >>"${HOME}/.bashrc"
      neuromancer_say "PATH_UPDATED bashrc"
    fi
    ;;
esac

neuromancer_git_identity_state
if [[ "$(neuromancer_git_identity_state)" != "GIT_IDENTITY=SET" ]]; then
  neuromancer_say "GIT_IDENTITY_HUMAN_GATE"
  neuromancer_say "Do not invent a Git email. Set user.name and user.email locally, then rerun verify."
fi

if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    neuromancer_say "GITHUB_AUTH=PRESENT"
  else
    neuromancer_say "GITHUB_AUTH_HUMAN_GATE"
    neuromancer_say "EXACT_HUMAN_ACTION: run gh auth login in a local terminal and complete browser auth."
  fi
fi

neuromancer_say "CORE_INSTALL_COMPLETE"
exit 0
