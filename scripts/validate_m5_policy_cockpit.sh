#!/bin/zsh
set -eu

root="${0:A:h:h}"

python3 -m unittest discover -s "$root/tests" -p 'test_m5_policy_cockpit.py' -v
python3 "$root/scripts/m5_policy_cockpit.py" check \
  "$root/examples/m5-policy-cockpit/public-safe-approval-request.json" >/dev/null
python3 "$root/scripts/m5_policy_cockpit.py" verify-receipts >/dev/null

print 'M5_POLICY_COCKPIT_VALID'
