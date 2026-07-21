#!/bin/zsh
set -eu

base="${0:A:h}"
required=(
  README.md
  factory-contract.yaml
  model-onboarding.yaml
  trace-event.schema.json
  source-register.md
  validation-receipt.md
)

for file in "${required[@]}"; do
  test -s "$base/$file"
done

/usr/bin/env jq empty "$base/trace-event.schema.json"

secret_pattern='(sk-[A-Za-z0-9]|gh[pousr]_[A-Za-z0-9]|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|api[_-]?key[[:space:]]*[:=][[:space:]]*[^$<{])'
unsafe_pattern='bind:[[:space:]]*0\.0\.0\.0|automatic_merge:[[:space:]]*true|self_approve:[[:space:]]*true'

set +e
if command -v rg >/dev/null 2>&1; then
  rg -n --hidden "$secret_pattern" "$base"
  scan_status=$?
else
  /usr/bin/grep -EnR --exclude-dir=.git "$secret_pattern" "$base"
  scan_status=$?
fi
set -e
if (( scan_status == 0 )); then
  print -u2 'Potential credential material detected'
  exit 1
elif (( scan_status != 1 )); then
  print -u2 "Credential scan failed with status $scan_status"
  exit "$scan_status"
fi

set +e
if command -v rg >/dev/null 2>&1; then
  rg -n "$unsafe_pattern" "$base"/*.yaml
  scan_status=$?
else
  /usr/bin/grep -En "$unsafe_pattern" "$base"/*.yaml
  scan_status=$?
fi
set -e
if (( scan_status == 0 )); then
  print -u2 'Unsafe factory setting detected'
  exit 1
elif (( scan_status != 1 )); then
  print -u2 "Factory-policy scan failed with status $scan_status"
  exit "$scan_status"
fi

print 'BZ_FACTORY_V2_PACKAGE_VALID'
