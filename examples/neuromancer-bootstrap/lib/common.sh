#!/usr/bin/env bash
# Shared helpers for the Neuromancer bootstrap. No secrets. No private paths.

neuromancer_local_root() {
  printf '%s\n' "${NEUROMANCER_LOCAL_ROOT:-$HOME/BeyondZero/neuromancer}"
}

neuromancer_prepare_local_layout() {
  local root
  root="$(neuromancer_local_root)"
  mkdir -p "${root}/evidence" "${root}/scripts" "${root}/recovery" "${root}/bootstrap"
}

neuromancer_log() {
  local root log_file
  root="$(neuromancer_local_root)"
  log_file="${root}/evidence/bootstrap.log"
  mkdir -p "${root}/evidence"
  printf '%s %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*" >>"${log_file}"
}

neuromancer_say() {
  printf '%s\n' "$*"
  neuromancer_log "$*"
}

neuromancer_cmd_version() {
  local cmd="$1"
  if command -v "${cmd}" >/dev/null 2>&1; then
    printf 'FOUND %s\n' "${cmd}"
  else
    printf 'MISSING %s\n' "${cmd}"
  fi
}

neuromancer_git_identity_state() {
  local name email
  name="$(git config --global --get user.name 2>/dev/null || true)"
  email="$(git config --global --get user.email 2>/dev/null || true)"
  if [[ -n "${name}" && -n "${email}" ]]; then
    printf 'GIT_IDENTITY=SET\n'
  elif [[ -n "${name}" || -n "${email}" ]]; then
    printf 'GIT_IDENTITY=PARTIAL\n'
  else
    printf 'GIT_IDENTITY=UNSET\n'
  fi
}

neuromancer_need_sudo() {
  if sudo -n true >/dev/null 2>&1; then
    return 0
  fi
  printf 'SUDO_HUMAN_GATE\n'
  printf 'EXACT_HUMAN_ACTION: authenticate sudo in the local password UI, then rerun.\n'
  return 1
}

neuromancer_protect_t2_wifi_packages() {
  if dpkg -s apple-firmware >/dev/null 2>&1; then
    printf 'APPLE_FIRMWARE=PRESENT\n'
    return 0
  fi
  printf 'APPLE_FIRMWARE=ABSENT\n'
  return 1
}

neuromancer_refuse_wifi_hazards() {
  if dpkg -s broadcom-wl >/dev/null 2>&1; then
    printf 'WIFI_HAZARD=broadcom-wl_installed\n'
    return 1
  fi
  printf 'WIFI_HAZARD=NONE\n'
  return 0
}
