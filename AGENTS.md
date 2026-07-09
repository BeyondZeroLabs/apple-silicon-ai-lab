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

## Commit Gate

Before any commit or push, check for secret-shaped strings, `.env` files, key files, private paths, private project references, unexpected binaries, and non-synthetic content.
