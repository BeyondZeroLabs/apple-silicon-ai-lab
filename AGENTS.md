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

- The workspace is standard-library Python 3.10+ with `zsh` and `jq`. Do not install Ollama, model weights, or other AI runtimes.
- Nothing starts on boot. There is no database, dev server, or package lockfile.
- From the repository root, the checks are `./scripts/validate_m5_policy_cockpit.sh`, `./scripts/validate_skill_supply_chain.sh`, `docs/software-factory/validate_package.sh`, and `python3 -I scripts/validate_public_repository_safety.py --repo . --trusted-root .`.
- The core action is `python3 scripts/m5_policy_cockpit.py check examples/m5-policy-cockpit/public-safe-approval-request.json`. A passing check prints `APPROVED_FOR_HUMAN_ACTION` and does not execute the requested action. Receipts written with `record --human-confirm` stay in ignored `.factory-state/` and are not authoritative.
