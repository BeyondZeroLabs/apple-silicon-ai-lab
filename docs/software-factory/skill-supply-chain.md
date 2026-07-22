# Skill supply-chain gate

This Phase 2 lane defines how the Software Factory may evaluate third-party agent skills without installing or enabling them. The registry is intentionally empty and every harness remains disabled.

## Trust boundary

Treat every external skill, prompt pack, adapter, plugin, hook, MCP server, and update as untrusted input. Discovery never grants execution or deployment authority. Skills cannot authenticate, install software, expand permissions, access protected storage, start services, acquire coordinator leases, commit, push, merge, promote models, or update authoritative memory.

Only public or synthetic material may enter this lane. Prohibited data classes are named as policy labels only; their contents must never be supplied to this repository, a skill, a prompt, a trace, or a review artifact.

## Lifecycle

`DISCOVERED → QUARANTINED → STATIC_REVIEWED → SANDBOX_TESTED → HUMAN_APPROVED → STAGED_READ_ONLY → ENABLED_PER_HARNESS → MONITORED`

Any failed review, provenance drift, hash change, permission change, or behavioral regression moves the entry to `REVOKED`. There is no direct path from discovery to enablement.

## Required promotion evidence

1. Immutable source repository, revision, artifact hashes, manifest, and license review.
2. Static security and semantic privacy review with no hooks, plugins, credential use, protected-path access, or unreviewed network behavior.
3. Isolated sandbox testing with synthetic inputs, no credentials, no private mounts, and recorded deterministic results.
4. Cross-harness parity tests for every approved adapter and harness.
5. A disable/remove rollback rehearsal and independent review.
6. Explicit human promotion from the M5 policy cockpit. Human approval does not make a skill authoritative; it only permits the separately bounded deployment step.

## Harness mapping

- Pi and Codex: explicit invocation of canonical BeyondZeroLabs instruction-only rewrites.
- Grok Build: hash-checked generated adapter; no hooks or plugins.
- Cursor: manual command or thin rule for read-only independent review.
- OpenClaw: later allowlisted adapter after its separate role gate.
- Hermes: later isolated profile; no self-management or self-promotion.

The canonical behavior contract remains harness-neutral. A skill must not silently gain capabilities when translated to another harness.

## GBrain integration boundary

GBrain is included as a `QUARANTINED_MEMORY_CANDIDATE`, not as an installed runtime or approved skill source. Its retrieval, citation, gap-analysis and local PGLite options could improve durable context for Pi, Grok Build, Codex, Cursor, OpenClaw and Hermes, but its runtime and bundled skills cross two separate trust boundaries:

1. GBrain runtime/MCP is a memory service and must pass a dedicated data, authentication, storage, tenancy, backup, deletion, poisoning and prompt-injection review.
2. Every bundled or generated GBrain skill must independently pass this skill supply-chain lifecycle. Runtime acceptance never bulk-approves a skill pack.

The first evaluation is M5-attended, read-only, loopback-only and limited to a disposable public/synthetic corpus. The autonomous installer, agent-provided setup instructions, external integrations, write-capable MCP tools, background jobs, cron/dream cycle, skill optimizer and bulk note import remain disabled. No credential, private Obsidian vault, external drive, `OSIRIS_CORE`, personal communication, meeting record or protected legal/case material may enter the pilot.

If the pilot passes, the proposed standing location is an isolated non-admin service on the Mac mini, separate from its lease watchdog and OSIRIS/OpenClaw process. Clients attach through an authenticated approved surface. GBrain remains a derived retrieval layer: `agent_bridge` retains operational authority, Git retains reviewed repository truth, and human-reviewed knowledge remains authoritative. Revocation must stop the service, remove every harness adapter and restore the last verified snapshot without deleting source material.

## Initial capability candidates

The first candidates should be narrow, public-safe workflow aids: specification drafting, bounded planning, context-boundary checks, test-driven changes, deterministic verification, independent security review, independent code review, and draft handoff. No third-party content is vendored by this phase.

## Validation

Run:

```sh
zsh scripts/validate_skill_supply_chain.sh
```

The validator rejects unknown fields, mutable provenance, unsafe paths, non-canonical JSON, capability grants, or any enabled deployment. This is a design/validation contract only; it performs no network calls, installs, service activation, model access, or external-storage writes.
