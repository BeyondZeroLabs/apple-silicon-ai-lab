# Repository Safety Policy

Apple Silicon AI Lab is a public-safe repository. Content must be suitable for public GitHub publication.

## Allowed

- Synthetic prompts
- Fictional examples
- Local-first notes
- Public documentation
- Small scripts that do not retrieve secrets or process private files
- Benchmark templates that do not require model downloads by default

## Not Allowed

- Secrets or credentials
- Private filesystem paths
- Private prompts or outputs
- Confidential, personal, proprietary, or legal material
- Cloud-synced private file contents
- Model weights or generated runtime artifacts unless approved later
- Real bridge receipts, private logs, or private handoff records

## Review Gate

Before each public push, run a safety scan for secret-shaped strings, private paths, disallowed content, unexpected binary files, and local-only artifacts.
