#!/usr/bin/env bash
# Read-only T2 Wi-Fi and network survivability checks. Never prints secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/lib/host-guard.sh"
# shellcheck disable=SC1091
source "${ROOT}/lib/common.sh"

neuromancer_prepare_local_layout
FAILS=0

pass() {
  printf 'PASS %s\n' "$1"
}

fail() {
  printf 'FAIL %s\n' "$1"
  FAILS=$((FAILS + 1))
}

printf 'KERNEL=%s\n' "$(uname -r)"

if dpkg -s apple-firmware >/dev/null 2>&1; then
  version="$(dpkg-query -W -f '${Version}' apple-firmware 2>/dev/null || printf unknown)"
  pass "apple-firmware=${version}"
else
  fail "apple-firmware_missing"
fi

if [[ -d /lib/firmware/brcm ]]; then
  if find /lib/firmware/brcm -maxdepth 1 -type f \( -iname '*bali*' -o -iname '*4364*' \) | grep -q .; then
    pass "bali_or_4364_firmware_present"
  else
    fail "bali_or_4364_firmware_missing"
  fi
else
  fail "brcm_firmware_dir_missing"
fi

if modinfo brcmfmac >/dev/null 2>&1; then
  pass "brcmfmac_available"
else
  fail "brcmfmac_unavailable"
fi

if ip -br link show wlp5s0 >/dev/null 2>&1; then
  pass "wlp5s0_exists"
else
  fail "wlp5s0_missing"
fi

if command -v nmcli >/dev/null 2>&1; then
  if nmcli -t -f TYPE,STATE device status 2>/dev/null | grep -q '^wifi:'; then
    pass "networkmanager_wifi_device"
  else
    fail "networkmanager_wifi_device_missing"
  fi
  if nmcli -t device wifi list 2>/dev/null | grep -q .; then
    pass "ssid_scan_nonempty"
  else
    fail "ssid_scan_empty"
  fi
else
  fail "nmcli_missing"
fi

if ip route show default 2>/dev/null | grep -q .; then
  pass "default_route"
else
  fail "default_route_missing"
fi

if ping -c 1 -W 3 1.1.1.1 >/dev/null 2>&1; then
  pass "internet_ip"
else
  fail "internet_ip"
fi

if getent hosts ubuntu.com >/dev/null 2>&1; then
  pass "dns_resolution"
else
  fail "dns_resolution"
fi

neuromancer_refuse_wifi_hazards || fail "wifi_hazard"

if [[ "${FAILS}" -eq 0 ]]; then
  printf 'NETWORK_HEALTH=PASS\n'
  exit 0
fi

printf 'NETWORK_HEALTH=FAIL count=%s\n' "${FAILS}"
exit 1
