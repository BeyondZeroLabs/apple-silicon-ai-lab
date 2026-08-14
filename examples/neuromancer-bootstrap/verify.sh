#!/usr/bin/env bash
# Record versions and gate status. Safe to rerun. No secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/lib/host-guard.sh"
# shellcheck disable=SC1091
source "${ROOT}/lib/common.sh"

neuromancer_prepare_local_layout
OUT="$(neuromancer_local_root)/evidence/VERIFY.md"
FAILS=0

{
  printf '# Neuromancer verify\n\n'
  printf 'Generated_UTC: %s\n\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  printf '## Host guard\n\n```\n'
  neuromancer_host_guard || true
  printf '```\n\n## Tool versions\n\n```\n'
  for cmd in git gh curl wget python3 uv node npm pnpm rustc cargo jq rg cursor cursor-agent agent chatgpt codex tailscale; do
    if command -v "${cmd}" >/dev/null 2>&1; then
      printf 'FOUND %s ' "${cmd}"
      "${cmd}" --version 2>/dev/null | head -n 1 || printf 'version-unknown\n'
    else
      printf 'MISSING %s\n' "${cmd}"
    fi
  done
  printf '```\n\n## Protected Wi-Fi\n\n```\n'
  dpkg-query -W -f 'apple-firmware %{Version}\n' apple-firmware 2>/dev/null || printf 'apple-firmware missing\n'
  neuromancer_refuse_wifi_hazards || true
  printf '```\n\n## Human gates\n\n```\n'
  neuromancer_git_identity_state
  if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
      printf 'GITHUB_AUTH=PRESENT\n'
    else
      printf 'GITHUB_AUTH_HUMAN_GATE\n'
    fi
  else
    printf 'GITHUB_CLI=MISSING\n'
  fi
  if command -v tailscale >/dev/null 2>&1; then
    if tailscale status >/dev/null 2>&1; then
      printf 'TAILSCALE_AUTH=PRESENT\n'
    else
      printf 'TAILSCALE_AUTH_HUMAN_GATE\n'
    fi
  else
    printf 'TAILSCALE=MISSING\n'
  fi
  if command -v cursor-agent >/dev/null 2>&1; then
    cursor-agent --version 2>/dev/null | head -n 1 || true
    if cursor-agent status >/dev/null 2>&1; then
      printf 'CURSOR_AGENT=PASS\n'
    else
      printf 'CURSOR_AUTH_HUMAN_GATE\n'
    fi
  elif command -v agent >/dev/null 2>&1; then
    agent --version 2>/dev/null | head -n 1 || true
    printf 'CURSOR_AGENT=INSTALLED_AS_agent\n'
  else
    printf 'CURSOR_AGENT=MISSING\n'
  fi
  if command -v chatgpt >/dev/null 2>&1 || dpkg -s chatgpt >/dev/null 2>&1; then
    printf 'CHATGPT_LINUX_DESKTOP=PASS_INSTALLED_LOGIN_UNVERIFIED\n'
    printf 'CHATGPT_LOGIN_HUMAN_GATE\n'
  else
    printf 'CHATGPT_LINUX_DESKTOP=BLOCKED_OR_MISSING\n'
  fi
  if command -v codex >/dev/null 2>&1; then
    printf 'CODEX_CLI=INSTALLED\n'
    printf 'CODEX_LOGIN_HUMAN_GATE unless already authenticated locally\n'
  else
    printf 'CODEX_CLI=MISSING\n'
  fi
  printf '```\n'
} >"${OUT}"

if ! neuromancer_host_guard >/dev/null; then
  FAILS=$((FAILS + 1))
fi

printf 'VERIFY=%s\n' "${OUT}"
if [[ "${FAILS}" -ne 0 ]]; then
  printf 'VERIFY_STATUS=HOST_MISMATCH\n'
  exit 2
fi
printf 'VERIFY_STATUS=RECORDED\n'
exit 0
