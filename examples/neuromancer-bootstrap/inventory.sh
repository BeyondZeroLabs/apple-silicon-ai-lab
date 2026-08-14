#!/usr/bin/env bash
# Read-only inventory. Safe to run on any host. Does not install packages.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/lib/host-guard.sh"
# shellcheck disable=SC1091
source "${ROOT}/lib/common.sh"

neuromancer_prepare_local_layout
OUT="$(neuromancer_local_root)/evidence/BASELINE.md"

{
  printf '# Neuromancer baseline inventory\n\n'
  printf 'Generated_UTC: %s\n\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  printf '## Host identity\n\n'
  printf '```\n'
  neuromancer_read_identity
  printf 'hostname=%s\n' "${NM_HOSTNAME}"
  printf 'product=%s\n' "${NM_PRODUCT:-empty}"
  printf 'arch=%s\n' "${NM_ARCH}"
  printf 'virt=%s\n' "${NM_VIRT}"
  printf 'os_id=%s\n' "${NM_OS_ID:-unknown}"
  printf 'os_version=%s\n' "${NM_OS_VERSION:-unknown}"
  uname -a
  printf '```\n\n'
  printf '## Host guard\n\n'
  printf '```\n'
  neuromancer_host_guard || true
  printf '```\n\n'
  printf '## Kernel and OS\n\n'
  printf '```\n'
  if command -v hostnamectl >/dev/null 2>&1; then
    hostnamectl 2>/dev/null || printf 'hostnamectl_unavailable\n'
  else
    printf 'hostnamectl_missing\n'
  fi
  if [[ -r /etc/os-release ]]; then
    cat /etc/os-release
  fi
  printf '```\n\n'
  printf '## Storage\n\n'
  printf '```\n'
  lsblk -o NAME,SIZE,MODEL,TRAN,FSTYPE,MOUNTPOINTS 2>/dev/null || printf 'lsblk_unavailable\n'
  df -hT / 2>/dev/null || true
  printf '```\n\n'
  printf '## CPU and memory\n\n'
  printf '```\n'
  lscpu 2>/dev/null | sed -n '1,40p' || true
  free -h 2>/dev/null || true
  printf '```\n\n'
  printf '## PCI, USB, GPU\n\n'
  printf '```\n'
  if command -v lspci >/dev/null 2>&1; then
    lspci -nnk 2>/dev/null || printf 'lspci_failed\n'
  else
    printf 'lspci_missing\n'
  fi
  if command -v lsusb >/dev/null 2>&1; then
    lsusb 2>/dev/null || printf 'lsusb_failed\n'
  else
    printf 'lsusb_missing\n'
  fi
  printf '```\n\n'
  printf '## Network (no secrets)\n\n'
  printf '```\n'
  ip -br link 2>/dev/null || printf 'ip_link_unavailable\n'
  if command -v nmcli >/dev/null 2>&1; then
    nmcli -f DEVICE,TYPE,STATE,CONNECTION device status 2>/dev/null || printf 'nmcli_failed\n'
  else
    printf 'nmcli_missing\n'
  fi
  printf '```\n\n'
  printf '## T2 and firmware packages\n\n'
  printf '```\n'
  dpkg -l 2>/dev/null | grep -E 'apple-firmware|linux-image|linux-headers' || printf 'no_matching_packages\n'
  apt-cache policy apple-firmware 2>/dev/null || printf 'apple-firmware_policy_unavailable\n'
  if [[ -d /lib/firmware/brcm ]]; then
    printf 'brcm_firmware_dir=present\n'
    find /lib/firmware/brcm -maxdepth 1 -type f -iname '*bali*' -printf '%f\n' 2>/dev/null || true
    find /lib/firmware/brcm -maxdepth 1 -type f -iname '*4364*' -printf '%f\n' 2>/dev/null || true
  else
    printf 'brcm_firmware_dir=absent\n'
  fi
  neuromancer_protect_t2_wifi_packages || true
  neuromancer_refuse_wifi_hazards || true
  printf '```\n\n'
  printf '## Device classes\n\n'
  printf '```\n'
  printf 'bluetooth_sysfs=%s\n' "$( [[ -d /sys/class/bluetooth ]] && printf present || printf absent )"
  printf 'sound_sysfs=%s\n' "$( [[ -d /sys/class/sound ]] && printf present || printf absent )"
  printf 'video_nodes=%s\n' "$( ls /dev/video* >/dev/null 2>&1 && printf present || printf absent )"
  printf 'power_supply=%s\n' "$( ls /sys/class/power_supply >/dev/null 2>&1 && printf present || printf absent )"
  printf 'thermal=%s\n' "$( ls /sys/class/thermal >/dev/null 2>&1 && printf present || printf absent )"
  printf '```\n\n'
  printf '## Developer tooling\n\n'
  printf '```\n'
  for cmd in git gh curl wget python3 pip uv node npm corepack pnpm bun rustc cargo docker podman tailscale ollama codex cursor cursor-agent agent jq rg fd cmake pkg-config pipx rustup; do
    neuromancer_cmd_version "${cmd}"
  done
  neuromancer_git_identity_state
  printf '```\n\n'
  printf '## Notes\n\n'
  printf -- '- This inventory is read-only.\n'
  printf -- '- Wi-Fi credentials are never printed.\n'
  printf -- '- Git identity values are not copied into this file.\n'
  printf -- '- Mutating installers refuse to run unless HOST_GUARD=PASS.\n'
} >"${OUT}"

neuromancer_say "INVENTORY_WRITTEN"
printf 'INVENTORY=%s\n' "${OUT}"
neuromancer_host_guard || true
