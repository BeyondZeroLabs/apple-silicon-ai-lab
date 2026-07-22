#!/bin/zsh
set -euo pipefail

root="${0:A:h:h}"
python3 "$root/scripts/validate_skill_registry.py" --sha256
python3 -m unittest discover -s "$root/tests" -p 'test_skill_registry.py' -v
print 'SKILL_SUPPLY_CHAIN_VALID'
