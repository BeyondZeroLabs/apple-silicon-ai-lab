---
id: bz-buzz-discovery-phase1-v1
phase: 2A
status: PHASE_2A_PARTIAL_APPROVED
truth_classification: PUBLIC_SAFE
discovery_date: 2026-08-01
phase_2a_update: 2026-08-01
discovery_host: cursor-cloud-agent-vm
bryant_approval: 2026-08-01
---

# Buzz discovery report — Phase 1 + Phase 2A

## Scope and boundary

This report records **read-only discovery** performed from the Cursor Cloud Agent VM assigned to Bryant Crowe (`bc-7b601cee-c383-4d40-b0ec-73b5246d6b67`), supplemented by **Phase 2A UI evidence** supplied by Bryant (Buzz Desktop screenshot, 2026-07-31 local time).

Phase 1 covered the cloud VM only. Phase 2A adds `REPORTED_BY_UI` findings from the live `beyondzero-labs` community. Relay URL, exact Buzz version, agent inventory, and mobile pairing remain incomplete until Bryant completes the checklist in [PHASE_2B_EXECUTION_CHECKLIST.md](PHASE_2B_EXECUTION_CHECKLIST.md) Steps 1 and 6.

**Phase 1 prohibitions observed:** no channels created or modified; no agents created, edited, activated, disabled, or deleted; no packages installed; no credentials entered; no relay changes; no device pairing; no pilot launched; no push, merge, deploy, invite, or external messaging.

## Evidence classification key

| Label | Meaning |
|---|---|
| `LOCALLY_VERIFIED` | Directly observed in this discovery environment |
| `SOURCE_VERIFIED_AT_PINNED_VERSION` | Confirmed from official Buzz source/docs at pinned release |
| `REPORTED_BY_UI` | Observed in Buzz Desktop UI (not available in this pass) |
| `INFERENCE` | Reasoned from verified facts; not directly observed |
| `UNKNOWN` | Not determined; requires Bryant-local inspection |

---

## 1. Discovery environment

| Finding | Classification | Evidence |
|---|---|---|
| Host OS is Linux x86_64 cloud VM (`Linux cursor 6.12.94+`) | `LOCALLY_VERIFIED` | `uname -a` |
| This is **not** the M5 Max control node | `INFERENCE` | Cloud agent run metadata; no macOS paths present |
| Cursor Cloud run: `bc-7b601cee-c383-4d40-b0ec-73b5246d6b67` | `LOCALLY_VERIFIED` | cursor-cloud `run-info` |
| Owning user: Bryant Crowe | `LOCALLY_VERIFIED` | cursor-cloud `run-info` |
| No saved Cursor environment build for this run | `LOCALLY_VERIFIED` | cursor-cloud `environment-info` (`environment: null`, `build: null`) |
| Network egress unrestricted in cloud VM | `LOCALLY_VERIFIED` | cursor-cloud `environment-info` |

**Implication (`INFERENCE`):** Live Buzz workspace state (relay, channels, agents, mobile pairing) cannot be discovered from this host. Phase 1 findings for those items are absent or sourced from official documentation only.

---

## 2. Installed Buzz version and executable provenance

| Finding | Classification | Evidence |
|---|---|---|
| `buzz` CLI not on PATH | `LOCALLY_VERIFIED` | `command -v buzz` → not found |
| `buzz-acp` not on PATH | `LOCALLY_VERIFIED` | `command -v buzz-acp` → not found |
| `buzz-admin` not on PATH | `LOCALLY_VERIFIED` | `command -v buzz-admin` → not found |
| `cursor-agent` not on PATH | `LOCALLY_VERIFIED` | `command -v cursor-agent` → not found |
| No Buzz Desktop app bundle | `LOCALLY_VERIFIED` | `/Applications/Buzz.app` missing; Linux VM |
| No Buzz config directories | `LOCALLY_VERIFIED` | `~/.buzz`, `~/.config/buzz` missing |
| No `BUZZ_*` environment variables set | `LOCALLY_VERIFIED` | `env \| rg '^BUZZ_'` → empty |
| No Buzz packages in dpkg/snap/flatpak | `LOCALLY_VERIFIED` | package manager scans |
| **Installed Buzz version on this host** | `UNKNOWN` | Nothing installed |

### Official release pin (reference target, not installed here)

| Field | Value | Classification |
|---|---|---|
| Release tag | `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Release name | Buzz Desktop v0.5.0 | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Tag commit SHA | `4a977c588a540be38bd8ddb268cd24437bac8165` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Published | 2026-07-28T14:23:22Z | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Official release URL | https://github.com/block/buzz/releases/tag/v0.5.0 | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| macOS Apple Silicon asset | `Buzz_0.5.0_aarch64.dmg` (sha256:a096767f08f5528d780335b58b4bebc948becaa8855c5093107edf16e45a497c) | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| macOS Intel asset | `Buzz_0.5.0_x64.dmg` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Linux amd64 asset | `Buzz_0.5.0_amd64.deb`, `Buzz_0.5.0_amd64.AppImage` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

| Finding | Classification |
|---|---|
| Buzz Desktop running on macOS (M5) | `REPORTED_BY_UI` | Screenshot: macOS menu bar shows Buzz active |
| Buzz version installed on Bryant M5 | `UNKNOWN` | About dialog not shown; Cursor task title references v0.5.0 but that is the agent run name, not proof of installed Buzz version |
| Executable provenance on M5 | `UNKNOWN` | Verify via Buzz → About and `/Applications/Buzz.app` on M5 |

---

## 3. Active relay / community configuration

| Finding | Classification | Evidence |
|---|---|---|
| No relay URL configured in cloud VM | `LOCALLY_VERIFIED` | No config files; no `BUZZ_RELAY_URL` |
| No WebSocket connection to any Buzz relay attempted | `LOCALLY_VERIFIED` | Phase 1 prohibition; no relay tools installed |
| Community slug visible in UI | `beyondzero-labs` | `REPORTED_BY_UI` | Screenshot: sidebar user label |
| BeyondZero Labs community relay URL | `UNKNOWN` | Not visible in screenshot; record from Settings → Communities |
| Hosted vs self-hosted deployment | `UNKNOWN` | Requires relay URL from Buzz Desktop settings |
| Community identity / host binding | `beyondzero-labs` (display) | `REPORTED_BY_UI` | Sidebar; relay host not confirmed |

### Architecture facts (reference only)

| Finding | Classification | Source |
|---|---|---|
| Relay is single source of truth; clients connect via WebSocket | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `block/buzz` `ARCHITECTURE.md` @ v0.5.0 |
| Authentication: NIP-42 (WS), NIP-98 (HTTP) | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `block/buzz` `SECURITY.md` @ v0.5.0 |
| Channel membership is sole access-control gate | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `block/buzz` `SECURITY.md` @ v0.5.0 |

---

## 4. Current channels

| Finding | Classification | Evidence |
|---|---|---|
| Live channel: `#general` | Present; Bryant created; only system message visible | `REPORTED_BY_UI` |
| Live channel: `#Welcome` | Present; padlock icon (private) | `REPORTED_BY_UI` |
| Live channel: `#welcome-everyone` | Present | `REPORTED_BY_UI` |
| Recommended BZ channels (`#dev-command`, etc.) | **Not present** in visible channel list | `REPORTED_BY_UI` |
| Default welcome channels in new workspace | Consistent with onboarding pattern | `INFERENCE` | `#Welcome` + `#welcome-everyone` match v0.5.0 welcome flow |
| Recommended BZ channel creation status | Not started | `INFERENCE` | Absent from sidebar; Phase 2B pending |

**Note:** Files under `docs/buzz-workspace/CHANNELS.md` describe **intended** layout only. They are not evidence of installed channels (`INFERENCE`).

---

## 5. Current agents and visible permissions

| Finding | Classification | Evidence |
|---|---|---|
| Agents navigation present in sidebar | Yes | `REPORTED_BY_UI` |
| "Create agent" action visible | Yes | `REPORTED_BY_UI` |
| Live managed-agent inventory (names, pubkeys, harnesses) | `UNKNOWN` | Agents list not expanded in screenshot |
| Fizz / Honey / Bumble visible | `UNKNOWN` | Not shown in screenshot |
| Starter Welcome Team personas | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `welcomeGuide.ts` @ v0.5.0 |

### Starter agents (official v0.5.0 source)

| Agent | Persona ID | Default role | Default `respondTo` | Classification |
|---|---|---|---|---|
| Fizz | `builtin:fizz` | lead | `owner-only` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Honey | `builtin:honey` | teammate | `owner-only` (then allowlist Fizz) | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Bumble | `builtin:bumble` | teammate | `owner-only` (then allowlist Fizz) | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

| Finding | Classification | Evidence |
|---|---|---|
| Starters created with `spawnAfterCreate: false`, `startOnAppLaunch: false` | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `buildWelcomeStarterCreateInput()` @ v0.5.0 |
| Starters added to welcome channel with role `bot` | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `ensureWelcomeTeamMembership()` @ v0.5.0 |
| Codex Builder / Claude Reviewer / Cursor Engineer agents exist live | `UNKNOWN` | Not inspectable from cloud |
| Agent pubkeys, harness commands, channel memberships | `UNKNOWN` | Fill from M5 Buzz Desktop → Agents |

### buzz-acp permission model (reference)

| Control | Default | Classification |
|---|---|---|
| `respondTo` | `owner-only` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Owner commands `!shutdown`, `!cancel`, `!rotate` | Owner-only, kind:9 + `p` tag | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `BUZZ_MANAGED_AGENT` env cannot be overridden in custom harness | Stripped before merge | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

---

## 6. Available harness / runtime settings

Discovery of **installed** harness availability on PATH: none (no Buzz, no harness CLIs). Below is the **official v0.5.0 runtime catalog** from source.

### Tier-1 compiled-in runtimes

| ID | Commands | Classification |
|---|---|---|
| `goose` | `goose` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `claude` | `claude-agent-acp`, `claude-code-acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `codex` | codex-acp adapter | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `buzz-agent` | buzz-agent | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

### Tier-2 preset harnesses (`PRESET_HARNESSES` @ v0.5.0)

| ID | Label | Command | Args | Classification |
|---|---|---|---|---|
| `cursor` | Cursor | `cursor-agent` | `acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `omp` | Oh My Pi | `omp` | `acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `grok` | Grok Build | `grok` | `agent`, `--always-approve`, `stdio` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `opencode` | OpenCode | `opencode` | `acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `kimi` | Kimi Code | `kimi` | `acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `amp` | Amp | `amp-acp` | (empty) | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `hermes` | Hermes Agent | `hermes-acp` | (empty) | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| `openclaw` | OpenClaw | `openclaw` | `acp` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

| Finding | Classification |
|---|---|
| Tier-2 presets are PATH-probed; not editable/deletable in UI | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Tier-3 custom harnesses live in `custom_harnesses/*.json` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Which runtimes show **Available** on M5 | `UNKNOWN` — requires Buzz Desktop → Agents → Runtime settings |
| Default agent parallelism lowered to 10 in v0.5.0 | `SOURCE_VERIFIED_AT_PINNED_VERSION` | Release notes PR #3038 |

---

## 7. Current repository context

| Finding | Classification | Evidence |
|---|---|---|
| Repository | `BeyondZeroLabs/apple-silicon-ai-lab` | `LOCALLY_VERIFIED` |
| Remote | `github.com/BeyondZeroLabs/apple-silicon-ai-lab` | `LOCALLY_VERIFIED` |
| Current branch | `cursor/buzz-workspace-setup-6b67` | `LOCALLY_VERIFIED` |
| HEAD commit | `e847f82` — docs: add BeyondZero Labs Buzz workspace setup package | `LOCALLY_VERIFIED` |
| Working tree clean at discovery time | `LOCALLY_VERIFIED` | `git status --short` empty |
| `main` tip | `2561e4b` Add public-safe factory validation workflow (#4) | `LOCALLY_VERIFIED` |
| Branch delta vs `main` | Includes fleet-readiness lane + `docs/buzz-workspace/*` (14 files) | `LOCALLY_VERIFIED` |

### `docs/buzz-workspace/` package status

| Finding | Classification |
|---|---|
| Setup package exists (13 markdown files + receipts/) | `LOCALLY_VERIFIED` |
| Package status: `DOCUMENTATION_ONLY_NOT_LIVE_CONFIGURED` | `LOCALLY_VERIFIED` — `README.md` front matter |
| Prior security gate doc records `APPROVED_FOR_SYNTHETIC_ONLY` | `LOCALLY_VERIFIED` — file content; **not** proof of live Buzz security posture |
| No `config/software-factory/buzz-adapter.json` on this branch | `LOCALLY_VERIFIED` | `rg` scan |
| Software Factory buzz adapter exists on separate factory branches | `INFERENCE` | Prior conversation context; not re-verified on this branch |

### Repository purpose (reference)

| Finding | Classification |
|---|---|
| Public Apple Silicon AI Lab experiments and factory scaffolds | `LOCALLY_VERIFIED` | `AGENTS.md`, `README.md` |
| Public-safe / synthetic-only boundary enforced | `LOCALLY_VERIFIED` | `AGENTS.md` |

---

## 8. Mobile-pairing status

| Finding | Classification | Evidence |
|---|---|---|
| Mobile client type listed in architecture | `SOURCE_VERIFIED_AT_PINNED_VERSION` | `ARCHITECTURE.md` client diagram |
| v0.5.0 release includes "Polish community rail and mobile pairing" (PR #2972) | `SOURCE_VERIFIED_AT_PINNED_VERSION` | GitHub release v0.5.0 body |
| Mobile pairing mechanism (QR, credential type, expiry) | `UNKNOWN` | Not found in `SECURITY.md` or `buzz-acp/README.md` @ v0.5.0 |
| Whether Bryant has paired a mobile device | `UNKNOWN` | Requires Buzz Desktop on M5 |
| Whether mobile preserves same channel access restrictions | `INFERENCE` | Same relay auth model assumed; not locally verified |

**Phase 1 action:** No device pairing attempted.

---

## 9. Official source and documentation pinned to release

### Pin record

| Artifact | Location | SHA / tag | Classification |
|---|---|---|---|
| Release tag | `block/buzz` | `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Tag commit | `block/buzz` | `4a977c588a540be38bd8ddb268cd24437bac8165` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Security policy | `SECURITY.md` | @ `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Architecture | `ARCHITECTURE.md` | @ `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| ACP harness docs | `crates/buzz-acp/README.md` | @ `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Preset harnesses | `desktop/.../managed_agents/discovery.rs` | @ `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Welcome Team | `desktop/.../onboarding/welcomeGuide.ts` | @ `v0.5.0` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

### What is **not** proof of installed behavior

| Item | Classification |
|---|---|
| `docs/buzz-workspace/*` setup package | Documentation only — `INFERENCE` when cited for live state |
| `main` branch of `block/buzz` | May differ from installed v0.5.0 — do not treat as installed behavior |
| Open issues / roadmap / vision docs | Not used in this report |
| Third-party tutorials (Hostinger, etc.) | Not used as primary evidence |

---

## 10. Discovery summary matrix

| Inspection target | Result | Primary classification |
|---|---|---|
| Installed Buzz version (this host) | Not installed | `LOCALLY_VERIFIED` |
| Installed Buzz version (M5) | Not inspected | `UNKNOWN` |
| Relay / community config | Not present / not accessible | `UNKNOWN` (live) |
| Current channels | Not inspectable | `UNKNOWN` |
| Current agents / permissions | Not inspectable | `UNKNOWN` |
| Harness catalog @ v0.5.0 | Documented from source | `SOURCE_VERIFIED_AT_PINNED_VERSION` |
| Repository context | `apple-silicon-ai-lab` @ `e847f82` | `LOCALLY_VERIFIED` |
| Mobile pairing status | Not inspectable | `UNKNOWN` |
| Official docs pin | `v0.5.0` / `4a977c58…` | `SOURCE_VERIFIED_AT_PINNED_VERSION` |

---

## 11. Proposed Phase 2 actions (require Bryant approval)

Phase 2 must run on **M5 with Buzz Desktop**, not the cloud VM. Proposed actions in dependency order:

### 2A — Local environment verification (read-only on M5)

1. Record Buzz Desktop version from **About** → `receipts/versions.md`.
2. Record relay URL, community name, hosting type (hosted/self-hosted) → `receipts/environment.md`.
3. Export channel list and visibility (names only; no sensitive content) → `receipts/permissions.md`.
4. Export managed-agent inventory: name, pubkey, harness, `respondTo`, status, channels → `receipts/permissions.md`.
5. Record which tier-1/tier-2 runtimes show **Available** vs missing → `receipts/versions.md`.
6. Record mobile pairing status from Buzz Desktop settings → `receipts/permissions.md`.
7. Update this report with `REPORTED_BY_UI` findings.

### 2B — Workspace configuration (mutating; separate approval)

1. Create recommended channels per `CHANNELS.md`.
2. Confine Fizz/Honey/Bumble to `#welcome` until inspected.
3. Create dedicated agents: Coordinator, Codex Builder, Claude Reviewer, Cursor Engineer, Verification.
4. Set `respondTo` allowlists per `AGENT_ROLES.md`.
5. Do **not** create `#case-brain-private` until security gate re-confirmed.

### 2C — Integration smoke tests (mutating; separate approval)

1. Cursor: `cursor-agent acp --help` + Buzz `@mention` test in `#local-ai-lab`.
2. Codex + Claude: shared-context test without copy-paste per `PILOT_TEST_PLAN.md`.
3. Record in `PILOT_RESULTS.md` and `receipts/test-results.md`.

### 2D — Synthetic pilot PILOT-001 (mutating; separate approval)

1. Execute full workflow per `PILOT_TEST_PLAN.md`.
2. Post final receipt in `#decisions-receipts`.
3. Re-assess security gate if harness file boundaries differ from assumptions.

---

## 12. Blockers before Phase 2

| Blocker | Classification | Resolution |
|---|---|---|
| No Buzz installation on discovery host | `LOCALLY_VERIFIED` | Run Phase 2A on M5 |
| No access to private Buzz community from cloud | `LOCALLY_VERIFIED` | Bryant provides UI read-only export or runs checklist |
| Installed version on M5 unconfirmed | `UNKNOWN` | Compare to pin `v0.5.0` / `4a977c58…` |
| Live channels and agents unconfirmed | `UNKNOWN` | Phase 2A inventory |
| Mobile pairing unconfirmed | `UNKNOWN` | Phase 2A mobile settings check |

---

## 13. Phase 1 compliance attestation

| Prohibited action | Complied |
|---|---|
| Create/modify channels | Yes — none performed |
| Create/edit/activate/disable/delete agents | Yes — none performed |
| Install packages | Yes — none performed |
| Authenticate providers / enter credentials | Yes — none performed |
| Change relay settings | Yes — none performed |
| Pair devices | Yes — none performed |
| Modify files outside staging report | Yes — only this report added |
| Launch synthetic pilot | Yes — not launched |
| Push / merge / deploy / invite / external message | Yes — none performed |

---

## 14. Phase 2A UI evidence (Bryant screenshot — 2026-07-31 local)

Screenshot reviewed: Buzz Desktop on macOS, `beyondzero-labs` community, `#general` channel active.

| Observation | Classification |
|---|---|
| Buzz application running; macOS menu bar active app | `REPORTED_BY_UI` |
| Human user: Bryant (bee emoji) in `beyondzero-labs` community | `REPORTED_BY_UI` |
| Sidebar sections: Inbox, Agents, Channels | `REPORTED_BY_UI` |
| Channels visible: `#general`, `#Welcome` (private), `#welcome-everyone` | `REPORTED_BY_UI` |
| `#general` description: "General conversation and community updates" | `REPORTED_BY_UI` |
| `#general` history: single system message — Bryant created channel | `REPORTED_BY_UI` |
| Prominent actions: "Create agent", "Add people" | `REPORTED_BY_UI` |
| Recommended BZ channels absent from sidebar | `REPORTED_BY_UI` |
| Relay URL, Buzz About version, agent details, mobile pairing | `UNKNOWN` | Not in screenshot |

**Screenshot does not prove:** Buzz Desktop version (Cursor window title is cloud agent task name), relay host, starter agent provisioning, or harness availability.

---

## 15. Phase 2 approval and next actions

| Item | Status |
|---|---|
| Bryant approval received | Yes — 2026-08-01 |
| Phase 2A (UI inventory) | **Partial** — screenshot recorded; Steps 1 and 6 of checklist remain |
| Phase 2B (channel + agent configuration) | **Ready** — see [PHASE_2B_EXECUTION_CHECKLIST.md](PHASE_2B_EXECUTION_CHECKLIST.md) |
| Phase 2C (smoke tests) | Blocked on 2B |
| Phase 2D (PILOT-001) | Blocked on 2C |

---

## Status

**`PHASE_2A_PARTIAL — EXECUTE PHASE_2B_CHECKLIST`**

Phase 1 complete. Bryant approved Phase 2. Phase 2A partial inventory recorded from UI screenshot. Bryant should execute [PHASE_2B_EXECUTION_CHECKLIST.md](PHASE_2B_EXECUTION_CHECKLIST.md) on M5, then reply with completion or a follow-up screenshot of Agents + Settings for remaining `UNKNOWN` fields.
