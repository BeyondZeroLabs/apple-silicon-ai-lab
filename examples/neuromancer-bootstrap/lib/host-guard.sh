#!/usr/bin/env bash
# Host identity gate for the Neuromancer Intel T2 Ubuntu bootstrap.
# Refuse cloud VMs, hypervisors, and non-matching hardware.
# shellcheck disable=SC2034

neuromancer_expected_hostname() {
  printf '%s\n' "${NEUROMANCER_EXPECTED_HOSTNAME:-neuromancer}"
}

neuromancer_expected_product() {
  printf '%s\n' "${NEUROMANCER_EXPECTED_PRODUCT:-MacBookPro16,1}"
}

neuromancer_read_identity() {
  if [[ -n "${NEUROMANCER_IDENTITY_FILE:-}" ]]; then
    # Test-only identity injection. Production hosts must not set this.
    # shellcheck disable=SC1090
    source "${NEUROMANCER_IDENTITY_FILE}"
    return 0
  fi

  NM_HOSTNAME="$(hostname -s 2>/dev/null || hostname 2>/dev/null || printf 'unknown\n')"
  NM_PRODUCT=""
  if [[ -r /sys/class/dmi/id/product_name ]]; then
    NM_PRODUCT="$(tr -d '\0\n' </sys/class/dmi/id/product_name)"
  fi
  NM_ARCH="$(uname -m 2>/dev/null || printf 'unknown\n')"
  NM_VIRT="unknown"
  if command -v systemd-detect-virt >/dev/null 2>&1; then
    NM_VIRT="$(systemd-detect-virt 2>/dev/null || printf 'unknown\n')"
  fi
  NM_OS_ID=""
  NM_OS_VERSION=""
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    NM_OS_ID="${ID:-}"
    NM_OS_VERSION="${VERSION_ID:-}"
  fi
}

neuromancer_host_guard() {
  neuromancer_read_identity
  local expected_host expected_product
  expected_host="$(neuromancer_expected_hostname)"
  expected_product="$(neuromancer_expected_product)"

  case "${NM_VIRT}" in
    none|"")
      ;;
    unknown)
      printf 'HOST_GUARD=FAIL:VIRT_UNKNOWN\n'
      return 1
      ;;
    *)
      printf 'HOST_GUARD=FAIL:HYPERVISOR:%s\n' "${NM_VIRT}"
      return 1
      ;;
  esac

  if [[ "${NM_ARCH}" != "x86_64" && "${NM_ARCH}" != "amd64" ]]; then
    printf 'HOST_GUARD=FAIL:ARCH:%s\n' "${NM_ARCH}"
    return 1
  fi

  if [[ -z "${NM_PRODUCT}" || "${NM_PRODUCT}" != "${expected_product}" ]]; then
    printf 'HOST_GUARD=FAIL:PRODUCT:%s\n' "${NM_PRODUCT:-empty}"
    return 1
  fi

  if [[ "${NM_HOSTNAME}" != "${expected_host}" ]]; then
    printf 'HOST_GUARD=FAIL:HOSTNAME:%s\n' "${NM_HOSTNAME}"
    return 1
  fi

  printf 'HOST_GUARD=PASS\n'
  return 0
}

neuromancer_require_host() {
  if ! neuromancer_host_guard; then
    printf 'REFUSE: mutating Neuromancer bootstrap is local-host only.\n' >&2
    printf 'NEXT: run this from Cursor desktop on the Intel T2 Ubuntu node.\n' >&2
    return 2
  fi
}
