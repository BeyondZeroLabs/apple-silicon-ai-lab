---
id: bz-buzz-rollback-v1
status: ACTIVE
truth_classification: PUBLIC_SAFE
---

# Rollback and unwind procedures

## When to roll back

- pilot fails or produces unsafe behavior;
- agent harness misconfigured or over-permissioned;
- secret accidentally posted to a channel;
- wrong agent added to restricted channel;
- Cursor/Codex/Claude exfiltrates unexpected files;
- Bryant decides to pause Buzz coordination.

## Rollback levels

| Level | Scope | Downtime |
|---|---|---|
| L1 — Stop agents | Pause managed agents | Minutes |
| L2 — Remove channel access | Remove agents from channels | Minutes |
| L3 — Delete managed agents | Remove agent identities from desktop | Minutes |
| L4 — Disable community | Disconnect from relay | Immediate |
| L5 — Relay teardown | Self-hosted relay shutdown | Hours |

---

## L1 — Stop all managed agents

1. Buzz Desktop → **Agents**.
2. For each managed agent: click **Stop**.
3. Confirm no agents show status `running`.
4. Post in `#agent-coordination`:

```text
ROLLBACK L1 — All managed agents stopped. Reason: <reason>. Status: BLOCKED
```

## L2 — Remove channel memberships

1. For each channel in [CHANNELS.md](CHANNELS.md):
   - Open channel settings → Members.
   - Remove worker agent pubkeys (keep Bryant only).
2. For `#case-brain-private`: remove **all** agents except Bryant.
3. Record changes in `receipts/permissions.md`.

## L3 — Delete managed agents

1. Buzz Desktop → **Agents** → select agent → **Delete**.
2. Delete in order: Cursor Engineer, Codex Builder, Claude Reviewer, Verification, Coordinator.
3. **Optional:** retain Welcome Team (Fizz, Honey, Bumble) in `#welcome` only.
4. Starter agent keys on relay persist as historical members until removed via `buzz-admin`.

### Relay member cleanup (self-hosted)

```bash
# List members (deployment-specific)
# Remove agent pubkey from relay if buzz-admin supports remove-member on your version
```

Consult current `buzz-admin --help` for member removal commands on your relay version.

## L4 — Disconnect Buzz Desktop

1. Buzz Desktop → Settings → Communities → Disconnect or remove community.
2. Revoke API tokens if any were created.
3. Clear `BUZZ_PRIVATE_KEY` from shell profiles if set for testing.

## L5 — Self-hosted relay teardown

Only if BeyondZero runs a self-hosted relay:

1. Export audit log if needed for compliance (before destruction).
2. Stop relay process / Docker compose.
3. Snapshot or destroy Postgres volume per data retention policy.
4. Destroy S3/MinIO media bucket per policy.
5. Rotate any relay signing keys that were exposed.

**Do not destroy relay data without Bryant approval.**

---

## Cursor-specific rollback

1. Stop Cursor Engineer managed agent (L1).
2. Remove from `#dev-command`, `#local-ai-lab`, `#agent-coordination` (L2).
3. Delete Cursor Engineer agent (L3).
4. If using standalone `buzz-acp`:
   - Kill `buzz-acp` process.
   - Unset `BUZZ_ACP_AGENT_COMMAND`, `BUZZ_PRIVATE_KEY`.
5. Optional: `npm uninstall -g` any ACP adapters installed for testing.

See [CURSOR_BUZZ_INTEGRATION.md](CURSOR_BUZZ_INTEGRATION.md).

---

## Secret exposure rollback

If a secret is posted to any channel:

1. **Immediately** stop all agents (L1).
2. **Rotate** the exposed credential at the provider.
3. Do **not** attempt to "delete" messages unless relay supports it — assume persistence.
4. Status: `SECURITY_GATE_REQUIRED`.
5. Document incident in `#decisions-receipts` (redact secret value).
6. Re-assess [BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md](BUZZ_SECURITY_AND_CASE_BRAIN_READINESS.md).

---

## Starter agent confinement

If Fizz, Honey, or Bumble were added to production channels by mistake:

1. Remove them from all channels except `#welcome`.
2. Set `respondTo` to `owner-only`.
3. Stop agents.
4. Create dedicated role agents per [AGENT_ROLES.md](AGENT_ROLES.md) instead of remapping starters.

---

## Documentation rollback

If this setup package is merged but must be reverted in git:

```bash
git revert <commit-sha>
# or
git checkout main -- docs/buzz-workspace/
```

No Buzz runtime state is affected by git rollback.

---

## Post-rollback verification

- [ ] No managed agents running
- [ ] Restricted channels contain only Bryant
- [ ] Rotated credentials if exposure occurred
- [ ] `receipts/permissions.md` updated
- [ ] `#decisions-receipts` records rollback reason and status

---

## Recovery

To resume after rollback:

1. Fix root cause documented in `#decisions-receipts`.
2. Re-run channel and agent setup from [README.md](README.md).
3. Re-run pilot per [PILOT_TEST_PLAN.md](PILOT_TEST_PLAN.md).
4. Update [PILOT_RESULTS.md](PILOT_RESULTS.md).
