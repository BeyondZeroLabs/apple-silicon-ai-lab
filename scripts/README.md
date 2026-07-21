# Scripts

Scripts belong here only after they are reviewed for public safety. Do not add scripts that retrieve secrets, call paid APIs, install runtimes, download models, or process private files without explicit approval.

## M5 policy cockpit

`m5_policy_cockpit.py` is an offline policy gate for the interactive M5 pilot. `validate_m5_policy_cockpit.sh` runs its standard-library test suite and validates the synthetic example request. Neither script starts a service or performs a protected action.
