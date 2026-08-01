---
id: bz-buzz-handoff-template-v1
status: ACTIVE_TEMPLATE
truth_classification: PUBLIC_SAFE
---

# Standard agent handoff template

Copy this structure for every agent handoff in Buzz channels.

---

## Goal

What was requested.

## Scope inspected

Repositories, files, tools, and evidence actually inspected.

## Work completed

What was changed or analyzed.

## Evidence

Tests, hashes, screenshots, logs, file paths, commits, or exact observations.

## Findings

### Verified facts

- 

### Inferred conclusions

- 

### Unresolved unknowns

- 

## Risks

Privacy, security, correctness, architectural, operational, or legal risks.

## Recommendation

One clear next action.

## Status

One of: `PASS` | `PASS_WITH_FOLLOWUPS` | `BLOCKED` | `REJECTED` | `AWAITING_BRYANT` | `SECURITY_GATE_REQUIRED` | `PRIVACY_GATE_REQUIRED`

## Prohibited actions confirmed

Explicitly state whether the agent avoided:

- [ ] push
- [ ] merge
- [ ] deploy
- [ ] publish
- [ ] external messaging
- [ ] credential access
- [ ] sensitive-data upload
- [ ] destructive changes

---

## Example (synthetic pilot)

## Goal

Inspect `docs/buzz-workspace/README.md` and propose one clarity improvement without modifying files.

## Scope inspected

- Repository: `BeyondZeroLabs/apple-silicon-ai-lab`
- File: `docs/buzz-workspace/README.md` (58 lines)
- Tools: read_file

## Work completed

Identified ambiguous phrase "approved machine" — recommend specifying "Buzz Desktop on M5 control node."

## Evidence

- File read succeeded
- No writes performed
- No git status change

## Findings

### Verified facts

- README exists and lists package contents.
- Line 13 uses "approved machine" without naming M5.

### Inferred conclusions

- Clarifying M5 would reduce setup ambiguity.

### Unresolved unknowns

- Whether Bryant prefers "M5 Max" or "M5 control node" naming.

## Risks

None for this read-only analysis.

## Recommendation

Bryant approves wording change; Cursor Engineer implements in separate session.

## Status

`AWAITING_BRYANT`

## Prohibited actions confirmed

- [x] push
- [x] merge
- [x] deploy
- [x] publish
- [x] external messaging
- [x] credential access
- [x] sensitive-data upload
- [x] destructive changes
