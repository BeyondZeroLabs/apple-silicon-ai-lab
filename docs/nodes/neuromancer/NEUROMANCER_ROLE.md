# Neuromancer role

Recommended role after public hardware-family evidence. Confirm RAM, CPU SKU, and GPU usefulness on the host before promoting this node.

## Decision

Neuromancer should complement Apple Silicon nodes, not duplicate them.

Primary role:

- x86_64 development and test node
- official desktop/CLI agent surface on Ubuntu
- Intel T2 recovery terminal
- secondary/cold build worker

Not primary:

- local LLM inference node
- standing Software Factory coordinator
- OSIRIS/OpenClaw control gateway

This is a combination of development/test, browser/automation, build worker, and recovery. It is not a substitute for the M5 policy cockpit or Studio inference.

## Factory tension

The proposed Software Factory fleet roadmap listed the 2019 16-inch Intel MacBook Pro as a credential-free recovery-only candidate with no modern local LLM service.

The current owner mission still wants official Cursor, Codex, ChatGPT desktop if verified, GitHub CLI, and Tailscale on this Ubuntu node. Those tools imply standing account sessions.

Keep the factory recovery invariants:

- no production coordination
- no local model service by default
- no unattended merge/promotion authority

Treat authenticated developer tools as explicit human-gated exceptions, not a silent role promotion.

## Capability classes

| Class | Neuromancer |
| --- | --- |
| A. local inference node | DEFER |
| B. development/test node | INSTALL_NOW / CONFIGURE_NOW |
| C. orchestration/control node | UNSUPPORTED as standing coordinator |
| D. browser/automation node | CONFIGURE_NOW after desktop tools |
| E. build worker | INSTALL_NOW for x86_64 |
| F. cold/secondary worker | CONFIGURE_NOW |
| G. combination | B + D + E + F |

## Software Factory integration

| Component | Classification | Reason |
| --- | --- | --- |
| Osiris | DEFER | Proposed Mini gateway role; do not duplicate |
| Horus | DEFER | Not required to finish this Ubuntu baseline |
| Thoth | DEFER | Not required to finish this Ubuntu baseline |
| Isis | DEFER | Not required to finish this Ubuntu baseline |
| Set | DEFER | Not required to finish this Ubuntu baseline |
| Buzz | DEFER | Not required to finish this Ubuntu baseline |
| Prime Agent / Prime Intellect | DEFER | Conditional Intel support; not this baseline |
| Pi | DEFER | Required on Apple Silicon execution nodes first |
| Codex | INSTALL_NOW | Official CLI on Ubuntu x64 after host guard |
| Claude Code | REDUNDANT | Defer unless a later task needs a third harness |
| Cursor | INSTALL_NOW | Official desktop plus local CLI/agent |
| GitHub | INSTALL_NOW tooling; CONFIGURE_NOW auth | Browser auth only |
| Tailscale | INSTALL_NOW client; CONFIGURE_NOW auth | Do not change tailnet ACLs |
| local inference / Ollama | DEFER | See capability note; do not download models |
| ChatGPT Linux desktop | INSTALL_NOW only after official package verification | No unofficial wrappers |
| Docker/Podman | DEFER | Add later if x86_64 isolation is needed |

## On-host confirmation still required

The public notes cannot see the live laptop. Before calling the baseline complete, the local agent must record:

- actual CPU model and thread count
- actual RAM
- whether the AMD dGPU is usable under this T2 Linux stack
- disk free space
- `network-health.sh` pass
- Cursor launch
- remaining auth gates
