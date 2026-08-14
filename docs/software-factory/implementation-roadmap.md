---
id: bz-software-factory-fleet-implementation-roadmap
created: 2026-07-20T20:00:00-04:00
status: PROPOSED_NOT_ACTIVE
truth_classification: ACTUAL_INVENTORY_WITH_PROPOSED_IMPLEMENTATION
authority: ~/TomorrowAI_OS/runtime/agent_bridge/
---

# BeyondZeroLabs Software Factory — fleet implementation roadmap

## Outcome

Build a local-first, multi-machine agentic engineering factory that can use frontier and local models through Pi and Grok Build, keep work alive through Herdr, preserve durable goals outside any one harness, create reviewed pull requests, and improve from evidence without allowing agents to approve their own changes.

## Final logical inventory roles

| Asset | Primary role | Explicit exclusions | Deployment state |
|---|---|---|---|
| MacBook Pro M5 Max, 128 GB | Human policy/model-access cockpit; frontier planning; security and independent review; model benchmarking; PR/model/policy approval | No unattended production coordinator while OS stability remains gated | Controlled interactive pilot only |
| Mac Studio M4 Max, 64 GB | Normal standing coordinator after acceptance; persistent Herdr workers; builds/tests; primary sustained local inference | No independent merge/model promotion; coordinator resources isolated from inference | Proposed production node |
| MacBook Pro 14-inch M4 Pro, 48 GB | Primary mobile executor; isolated worktrees; secondary benchmarks; explicit-lease failover coordinator and fallback approval console | No normal standing coordination; no lease while roaming/on battery; no independent merge | Proposed mobile/failover node |
| Mac mini M4, 16 GB | OSIRIS/OpenClaw control gateway; telemetry; technology radar; health checks; off-coordinator lease watchdog; lightweight CI and utility inference | Never a competing repo coordinator; no large-model service; watchdog isolated from OSIRIS workload | Proposed infrastructure node |
| MacBook Pro 16-inch Intel 2019, 16 GB | Credential-free Intel compatibility, archive verification and recovery terminal | No production coordination, modern local LLM service or standing credentials | Recovery-only candidate |
| iPad Pro M4 | Obsidian, dashboards, PR review and authenticated SSH/Herdr attachment | No persistent runtime or autonomous authority | Review surface |
| iPhone 15 | MFA/passkeys, alerts, capture, emergency stop/acknowledgement | No code, merge or promotion authority | Human-presence surface |
| Apple Watch Ultra 2 | Urgent escalation and safety notification | No protected-action authorization by itself | Notification surface |
| `AI_MODELS` Rugged Mini SSD, 2 TB | Preserve/read-only mixed-content audit | Not an authoritative model store; no approved writer | Mapped; content/backup/ownership gate open |
| `OSIRIS_CORE`, ~3.6 TiB APFS | Preserve existing Osiris/OpenClaw content | No new BZ writes, live sockets, auth, worktrees or mutable runtime state | Role/encryption/backup gate open |
| `LaCie` Rugged SSD4, 2 TB | Preferred candidate clean high-speed model-artifact/benchmark store | No writes until filesystem/encryption/backup/catalog/rollback approval | Mapped; storage acceptance open |
| `LACIE1` Rugged THB USB3 HDD, 2 TB | Preserve Solidity mirrors/artifacts/notes/releases/backups; proposed offline repository/release recovery archive | No model store, credentials, live worktrees or runtime databases | Mapped; encryption/ownership/restore gate open |

## Factory planes

1. **Human authority plane — M5 with M4 Pro fallback:** intent, risk, approvals, incident acceptance and rollback decisions.
2. **Coordination plane — Studio:** one renewable coordinator lease per repository; task decomposition and dispatch; no merge authority.
3. **Execution plane — Studio and M4 Pro:** one goal/task, branch and isolated worktree per worker. Mini performs only lightweight infrastructure work.
4. **Model plane — Studio with M5 evaluation:** pinned llama.cpp/MLX/Ollama/provider routes. Pi is the broad provider reference; Grok Build is the peer coding/research harness.
5. **Observation plane — Mini:** external health observation, alerts, technology radar and lease watchdog. Studio also watches Mini heartbeat to avoid silent observer failure.
6. **Evidence plane — `agent_bridge`:** append-only sanitized events, goal records, checkpoints, evaluations, receipts and approvals.
7. **Knowledge plane — reviewed Git docs and private Obsidian projection:** derived summaries never override the evidence or policy planes. GBrain is a quarantined candidate retrieval layer only; it is not authoritative memory and is not yet installed.

## Dual-harness access requirement

Pi and Grok Build are mandatory peers on the M5, Studio, M4 Pro and Mini. Intel support remains conditional on its supported runtime and security posture; iPad, iPhone and Watch attach to Mac-hosted sessions rather than installing the CLIs.

Grok Build is not a conventional desktop GUI. Its primary interactive surface is a fullscreen, mouse-capable TUI. It also exposes an Agent Dashboard and ACP mode for graphical host applications. Pi remains a TUI-oriented, programmable provider reference. The value of keeping both is independent harness behavior, not simply visual preference.

Every **approved conversational/tool-capable model** must be available through both harnesses. “Available” has four levels:

1. **Cataloged:** artifact or endpoint, revision, license and hash are registered.
2. **Connectable:** the harness can authenticate and receive a text response.
3. **Agent-compatible:** tool calling, structured output, bounded file edits, tests, context handling, stopping and error behavior pass.
4. **Fleet-approved:** the model/harness/machine route passes the required regression matrix.

Raw embedding models, rerankers, image encoders and training-only checkpoints are cataloged services/artifacts rather than interactive Grok Build chat models. Models without a compatible conversational API require an approved adapter and must not be falsely reported as Grok-accessible.

The factory generates machine-local Pi and Grok Build configurations from the reviewed model catalog. Secrets remain machine-local. The Studio model service stays loopback-bound; other Macs reach it through authenticated tunnelling. No shared mutable config or credential directory is synchronized across the fleet.

## Long-running goal model

The durable goal record is factory-owned. Pi, Grok Build, Codex, Hermes and other agents are replaceable executors. Herdr preserves live terminal processes while its server is alive and can resume supported native agent sessions after restart, but it does not preserve arbitrary processes across a cold server restart. Therefore Herdr is not the goal database.

Every long-running goal uses `goal-contract.yaml` and includes:

- immutable goal ID, human owner, repository and accepted specification;
- risk/data classification and acceptance tests;
- one coordinator lease with expiry and heartbeat;
- current state, task tree, branch/worktree and Herdr/session references;
- model, harness and tool policy;
- token, cost, wall-time, concurrency and retry budgets;
- checkpoint and idempotency keys;
- stop, pause, escalation and rollback conditions;
- independent validation and human approval evidence;
- sanitized receipt links and final disposition.

State machine:

```text
DRAFT -> APPROVED -> LEASED -> RUNNING
  -> CHECKPOINTED -> VALIDATING -> REVIEW_REQUIRED
  -> COMPLETED

RUNNING/CHECKPOINTED/VALIDATING
  -> PAUSED | BLOCKED | QUARANTINED | ROLLING_BACK | FAILED
```

Only the human owner can move a goal into `APPROVED`, accept a material risk exception, merge/promote, or declare an incident accepted. Agents may pause, quarantine, roll back to an already approved artifact, or open a draft remediation PR.

## Rollout phases

### Phase 0 — close deployment gates

- Run the redacted inventory collector independently on Studio, M4 Pro, Mini and Intel; reconcile the M5 follow-up.
- Verify OS channels, batteries, Ethernet, services, free space, backups and Git worktree cleanliness.
- Define Studio acceptance: UPS/power, resource reservation, network stability, backup, soak test and rollback.
- Verify Mini watchdog isolation and independent alert egress.
- Close external-drive ownership, encryption, backup and restore gates. Do not format or migrate during this phase.

### Phase 1 — ratify contracts through a PR

- Review and approve `factory-contract.yaml`, `goal-contract.yaml`, `trace-event.schema.json` and `model-onboarding.yaml`.
- Define the coordinator lease location, atomic update semantics, stale-lease recovery and fail-closed behavior.
- Add redaction tests and append-only local receipts before enabling any unattended goal.

### Phase 2 — M5 single-repository pilot

- Use one public-safe BeyondZeroLabs repository and one reversible documentation/test goal.
- Install/pin Herdr, Pi and Grok Build only after version, source and rollback approval.
- Run separate Pi and Grok Build smoke tests against the same approved model endpoint.
- Validate Grok Build TUI model selection, headless mode, Agent Dashboard discovery and ACP availability without treating the dashboard as the authoritative control plane.
- Exercise branch/worktree creation, deterministic tests, fresh-context review, draft PR and human rejection/approval without automatic merge.
- Test Herdr detach/reattach, native session restore and cmux rollback.
- Evaluate GBrain only in an attended, loopback-bound, read-only profile over a disposable public/synthetic corpus. Do not run its autonomous installer, load its skill pack, enable write tools/background jobs, provide credentials, or import any private Obsidian, communication, legal/case or external-drive content.

### Phase 3 — Mini infrastructure pilot

- Establish a dedicated non-admin OSIRIS account.
- Run OpenClaw as the primary OSIRIS gateway with loopback binding, authentication, pairing and minimum tool policy.
- Keep Hermes as an isolated evaluation profile, not a second unrestricted scheduler.
- Deploy read-only observability, goal/lease watchdog and daily technology radar with strict resource limits.
- Verify that stopping or exhausting OSIRIS cannot stop the watchdog.
- If the M5 GBrain evaluation passes its separate runtime, privacy, poisoning, backup/restore and rollback gates, canary it under a dedicated non-admin Mini service account. Keep it isolated from OSIRIS and the lease watchdog; expose only approved authenticated retrieval, and keep writes, ingestion, cron/dream cycles and skill optimization disabled until separately promoted.

### Phase 4 — Studio acceptance and coordinator canary

- Install/pin Herdr, Pi, Grok Build and the first approved local model adapter.
- Start with llama.cpp as the reference adapter; evaluate Ollama afterward against the same health/structured-output contract.
- Register each approved endpoint in both Pi and `~/.grok/config.toml`; run the complete dual-harness tool/regression matrix before routing work.
- Reserve coordinator resources; start with one local generation slot.
- Rehearse lease acquire, heartbeat, expiry, stale recovery, no-active-coordinator state and rollback.
- Run a 24–72 hour observed canary before standing coordination.

### Phase 5 — M4 Pro mobile/failover canary

- Install matching pinned harness/integration versions.
- Validate authenticated Studio model access, local 7B-class fallback and isolated worktrees.
- Rehearse explicit failover only when Studio lease is absent, M5 approval is recorded, trusted-network presence is verified and the notebook is on AC power.
- Rehearse rollback from M4 Pro to no coordinator, then to an approved Studio lease.

### Phase 6 — recovery and human surfaces

- Keep Intel credential-free; verify read-only Git bundles/archive restoration and documented recovery commands.
- Public-safe host-guarded Ubuntu bootstrap for the Intel T2 node lives in `examples/neuromancer-bootstrap`; on-host inventory and authenticated developer tools remain host-local human gates.
- Validate iPad authenticated attachment and fallback review workflow.
- Validate iPhone alert and emergency-stop delivery end-to-end; Watch remains notification-only.

### Phase 7 — continuous improvement and model onboarding

- Mini discovers changes from official releases, Hugging Face papers/models, arXiv and approved X/Reddit APIs; social sources are leads, not evidence.
- Candidate technology enters quarantine and cannot auto-install.
- Studio/M5 run license, provenance, security, compatibility, benchmark, memory and regression evaluations.
- Independent judge compares the candidate with the approved baseline.
- Human approves canary, staged promotion or rejection. Every promotion has a pinned version and rollback artifact.

## First executable milestone

The first milestone is complete when one public-safe goal can:

1. be approved from the M5;
2. acquire a single lease;
3. create an isolated worktree and Herdr agent pane;
4. execute through Pi or Grok Build;
5. checkpoint and survive agent-session restart;
6. run deterministic validation and independent read-only review;
7. open a draft PR;
8. require human merge approval;
9. produce a redacted receipt; and
10. roll back cleanly.

No model promotion, external-drive migration, automatic merge or private-data workload belongs in this milestone.

## Definition of fleet-ready

- All Mac inventories and backup/restore checks completed.
- Studio/Mini power and network failure paths tested.
- One coordinator per repository enforced and failover rehearsed.
- Pi and Grok Build pass per-machine/per-model regression matrices.
- Herdr restore behavior and cmux rollback proven.
- Model endpoints remain loopback-bound with authenticated tunnelling.
- Emergency stop, quarantine and last-known-good rollback verified.
- Long-running goals have bounded budgets, durable checkpoints and human ownership.
- Obsidian remains a reviewed projection; mutable runtime state is never synchronized.

## Sources

- Herdr session persistence and native restore: https://herdr.dev/docs/session-state/
- Herdr agent state/integrations: https://herdr.dev/docs/agents/
- Herdr socket API and waits: https://herdr.dev/docs/socket-api/
- Grok Build interactive, headless and ACP modes: https://docs.x.ai/build/overview
- Pi agent toolkit: https://github.com/earendil-works/pi
