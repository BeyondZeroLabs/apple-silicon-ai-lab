# Agent Instructions

Apple Silicon AI Lab is a public Beyond Zero Labs repository for Apple Silicon AI/ML experiments, local-first tooling notes, and synthetic benchmark scaffolds.

## Public-Safe Boundaries

- Use synthetic examples only.
- Do not include secrets, API keys, tokens, passwords, private keys, or credentials.
- Do not include local home-directory paths or private filesystem paths.
- Do not include private data, confidential records, private prompts, or private outputs.
- Do not include sensitive personal materials, confidential records, or dispute-related material.
- Do not download models by default.
- Do not call APIs by default.
- Do not install AI runtimes by default.
- Do not add generated files with private prompts or private outputs.

## Workflow

- Verify repository state before changing files.
- Run a public safety scan before commits.
- Keep examples reproducible and local-first.
- Prefer small documentation and scaffold changes over speculative implementation.
- Do not invent benchmark results.
- Do not push publicly unless explicitly approved.

## Local Pi Routing and Validation

- The M5 Max is the local Pi control and approval node; worker tasks must have bounded scope and produce receipts and handoffs.
- Default local Ollama coding model: `qwen2.5-coder:7b`.
- `qwen2.5-coder:14b` requires explicit task-level approval with a recorded reason and expected benefit.
- 30B models are blocked pending explicit future reassessment.
- Preserve raw model output. Correctness-sensitive output must pass the validated-code-output workflow before acceptance.
- Strip at most one complete outer Markdown code fence. Reject nested or malformed fences and prose outside the fence.
- Require syntax parsing, AST safety checks, and task-appropriate functional tests.
- Reject unsafe or failed output; never silently repair it.

## Commit Gate

Before any commit or push, check for secret-shaped strings, `.env` files, key files, private paths, private project references, unexpected binaries, and non-synthetic content.

## Cursor Cloud specific instructions

This repo is pure Python 3.12 standard library. There are no third-party dependencies, no package manager/lockfile, and no long-running services or servers to start. The "applications" are three offline CLI tools plus their `unittest` suites; the pre-installed `python3` is all that is required to test and run them, so the startup update script has nothing to install.

- Tests (all suites): `python3 -m unittest discover -s tests -v`.
- Syntax check (no linter is configured): `python3 -m py_compile scripts/*.py tests/*.py`.
- CLI tools (see `scripts/README.md` for details):
  - `python3 scripts/validate_public_repository_safety.py --repo "$PWD"` — the public-safety/commit gate; it reads the git index, so `git add` new files before scanning them.
  - `python3 scripts/validate_skill_registry.py --sha256` — validates `config/software-factory/skill-registry.json`.
  - `python3 scripts/m5_policy_cockpit.py {check,record,verify-receipts}` — offline policy gate.
- The `scripts/validate_*.sh` wrappers use `#!/bin/zsh`, and `zsh` is NOT preinstalled on the VM. Either install it (`sudo apt-get update && sudo apt-get install -y zsh`) or just run the underlying `python3` commands above, which need no extra packages.
- `m5_policy_cockpit.py record` writes create-exclusive receipts under the gitignored `.factory-state/` directory. Re-running `record` for the same `request_id` fails by design ("create-exclusive receipt already exists"); delete `.factory-state/` to re-run a clean end-to-end demo.
