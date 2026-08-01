---
id: bz-buzz-receipt-test-results-v1
status: NOT_EXECUTED
truth_classification: PUBLIC_SAFE
---

# Test results receipt

## Pilot PILOT-001

| Field | Value |
|---|---|
| Status | **NOT EXECUTED** |
| Reason | Buzz not available in cloud VM; local pilot required |
| Test plan | [PILOT_TEST_PLAN.md](../PILOT_TEST_PLAN.md) |
| Results doc | [PILOT_RESULTS.md](../PILOT_RESULTS.md) |

---

## Cloud documentation validation (2026-08-01)

Checks performed without live Buzz:

| Test | Command / action | Expected | Actual |
|---|---|---|---|
| Package structure | `ls docs/buzz-workspace/` | All required files present | _run at commit_ |
| No secrets in package | manual review | No tokens/keys | Pass |
| Official docs reachable | fetch block/buzz SECURITY.md | HTTP 200 | Pass |
| Buzz CLI absent | `which buzz` | not found | Pass (expected) |
| README links resolve | markdown link check | all files exist | _run at commit_ |

---

## Local pilot tests (fill after execution)

### Test commands

```bash
# Example for apple-silicon-ai-lab — adjust per actual change
python -m pytest tests/ -q
python scripts/validate_buzz_adapter.py  # if adapter lane files present
```

### Results

| Test | Command | Exit code | Output summary |
|---|---|---|---|
| Unit tests | | | |
| Lint | | | |
| Validator | | | |

### Security checks

| Check | Result |
|---|---|
| Credentials printed to channel | Must be **no** |
| Files outside repo read | Must be **no** |
| Network calls unauthorized | Must be **no** |
| Push performed | Must be **no** |
| Merge performed | Must be **no** |

### Cursor integration smoke test

| Step | Result |
|---|---|
| `cursor-agent acp --help` | |
| Buzz shows Cursor Available | |
| @mention response in channel | |
| `!cancel` stops turn | |
| Output in Buzz without manual relay | |

### Codex + Claude context sharing

| Step | Result |
|---|---|
| Codex sees Bryant goal without paste | |
| Claude sees Codex plan in #review-verification | |
| Separate sessions confirmed | |

---

## Hashes (fill after local pilot)

| Artifact | SHA-256 |
|---|---|
| Local commit (if any) | |
| Changed file hash | |
| Pilot decision receipt message ID | |

---

## Verdict

| Field | Value |
|---|---|
| Final pilot status | _BLOCKED until local run_ |
| Recorded in #decisions-receipts | No |
| Repeatable | _unknown_ |
