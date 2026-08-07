# Scripts

Scripts belong here only after they are reviewed for public safety. Do not add scripts that retrieve secrets, call paid APIs, install runtimes, download models, or process private files without explicit approval.

## M5 policy cockpit

`m5_policy_cockpit.py` is an offline policy gate for the interactive M5 pilot. `validate_m5_policy_cockpit.sh` runs its standard-library test suite and validates the synthetic example request. Neither script starts a service or performs a protected action.

## Skill supply-chain gate

`validate_skill_registry.py` validates the canonical design-only registry with Python's standard library. `validate_skill_supply_chain.sh` runs the validator and its negative security tests. Neither script downloads, installs, imports, or enables a skill.

## Prime Agent (Ollama) setup

`setup_prime_agent_ollama_m5.sh` configures `~/.prime/agent` for local Ollama, installs a `prime-agent` symlink (not Homebrew `pi`), and runs an offline smoke test. See [docs/prime-agent-ollama-m5-setup.md](../docs/prime-agent-ollama-m5-setup.md).
