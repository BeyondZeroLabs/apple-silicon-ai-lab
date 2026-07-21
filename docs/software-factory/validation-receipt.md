---
id: bz-software-factory-v2-validation-20260719
created: 2026-07-19T14:02:14-04:00
updated: 2026-07-20T23:50:00-04:00
status: VALIDATED_PROPOSAL_ONLY
truth_classification: ACTUAL
---

# Validation receipt

Validated and revalidated on the M5 on 2026-07-19 and 2026-07-20:

- all required package files exist and are non-empty;
- `trace-event.schema.json` parses as JSON;
- all three YAML contracts parse with Ruby SafeYAML;
- the package scan found no common API-token/private-key patterns;
- the repository package contains no machine-specific absolute home-directory paths;
- YAML safety scan found no `0.0.0.0` bind, automatic merge, or self-approval setting;
- the trace schema rejects undeclared top-level properties;
- current Qwen routing/model-size gates remain explicitly preserved.

Only proposed documentation was staged in an isolated Git worktree. No runtime, external disk, model route, API, browser account, or Obsidian synchronization setting was changed.
