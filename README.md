# Apple Silicon AI Lab

Public Apple Silicon AI/ML experiments, local-first tooling notes, and synthetic benchmark scaffolds from Beyond Zero Labs.

## What This Is

Apple Silicon AI Lab is a small public workspace for exploring AI/ML development patterns on Apple Silicon. It starts with reproducible notes, benchmark templates, and lightweight project structure before introducing runtime-specific code.

The project is intentionally local-first: examples should be understandable without cloud infrastructure, paid services, or large model artifacts by default.

## What Is Included

- Apple Silicon AI/ML experiment notes
- Local-first tooling observations
- Synthetic benchmark scaffolds
- Public-safe examples and documentation
- Reproducibility checklists for future approved runs
- Repository safety and contribution guidelines

## Current Status

Initial public scaffold is live. Runtime installs, model downloads, benchmark execution, and API calls are intentionally gated until the benchmark harness is finalized.

The first bounded Software Factory implementation is the offline [M5 policy cockpit](docs/software-factory/m5-policy-cockpit.md). It validates public-safe approval requests and can create append-only local receipts without installing services, contacting model providers, or touching external storage.

## Roadmap

- Expand synthetic benchmark templates
- Add local setup notes for approved Apple Silicon tooling
- Define benchmark result formats with invented sample data
- Add runtime-specific adapters after explicit approval gates
- Document reproducibility practices for local experiments

## Safety Note

This repository uses synthetic examples only. Please see [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and data-safety guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
