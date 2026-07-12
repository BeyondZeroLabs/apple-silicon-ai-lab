---
name: validated-code-output
description: "Validate local model-generated code while preserving raw output, separating format compliance from correctness, and enforcing syntax, AST safety, functional tests, and model-routing gates."
---

# Validated Code Output

Use this skill for model-generated code, configuration, shell or migration scripts, tests, and correctness-sensitive output.

1. Default to `qwen2.5-coder:7b`.
2. Permit `qwen2.5-coder:14b` only with explicit task-level M5 approval recording the reason and expected benefit.
3. Block every 30B model pending explicit future reassessment.
4. Preserve the original raw response unchanged and report raw-format compliance separately from semantic correctness.
5. Invoke the shared safe code-output validator. Its location must come from approved local configuration; do not embed a private machine path here.
6. Strip exactly one complete outer Markdown code fence when present. Reject prose outside it, nested fences, malformed fences, and mixed code/prose responses.
7. Require syntax parsing and AST safety checks before any functional test. Require task-appropriate functional tests for correctness-sensitive work.
8. Reject unsafe or failed output. Do not bypass validation or silently auto-fix a failure.
9. Keep worker tasks bounded and write start/final receipts, validation status, and a handoff.
