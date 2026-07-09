---
name: public-safety-review
description: "Review public repository changes before commits, pushes, exports, or session sharing. Use to check for secrets, private paths, confidential material, non-synthetic data, and unexpected binary artifacts."
---

# Public Safety Review

Use this skill before public commits, pushes, exports, or session sharing.

Check for:

- Secrets or secret-shaped strings
- `.env`, key, certificate, or credential files
- Local home-directory paths or private filesystem paths
- Private project names or private bridge traces
- Sensitive personal materials, confidential records, or dispute-related material
- Non-synthetic prompts, outputs, or examples
- Unexpected screenshots, images, PDFs, or binary artifacts

Return GREEN only when no blocking public-safety issues are found.
