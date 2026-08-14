# Neuromancer host-guarded bootstrap

Public-safe, idempotent bootstrap for the BeyondZero Intel T2 Ubuntu node named Neuromancer.

These scripts are designed to run on that machine only. They refuse cloud VMs, hypervisors, and non-matching hardware.

## What this is

A local-first recovery and developer-node scaffold:

- read-only inventory
- T2 Wi-Fi survivability checks
- core toolchain install
- official Cursor, Codex CLI, Tailscale, and optional official ChatGPT desktop install
- version recording

It does not download models, call paid APIs, or store credentials.

## Host requirements

Mutating installers require all of:

- hostname `neuromancer`
- DMI product `MacBookPro16,1`
- architecture `x86_64`
- `systemd-detect-virt` reporting `none`

Read-only `inventory.sh`, `network-health.sh`, and `verify.sh` may run anywhere. They record a host mismatch instead of installing software.

## Local evidence directory

On the target machine, scripts write to:

`$HOME/BeyondZero/neuromancer/`

That directory is local evidence. Do not copy it into this public repository.

## Scripts

| Script | Mutates the system | Notes |
| --- | --- | --- |
| `inventory.sh` | no | Writes `evidence/BASELINE.md` under the local evidence root |
| `network-health.sh` | no | Checks apple-firmware, Bali/4364 firmware, `brcmfmac`, `wlp5s0`, routing, IP, DNS |
| `install-core.sh` | yes | Host-guarded apt/tool install; never runs `apt autoremove` |
| `install-ai-tools.sh` | yes | Official Cursor, Codex CLI, Tailscale; ChatGPT desktop only from an owner-verified official deb |
| `verify.sh` | no | Records versions and remaining human gates |

## Absolute protections

Do not:

- install `broadcom-wl`
- remove `apple-firmware`
- replace a working kernel
- modify EFI or partitions
- copy Apple Silicon firmware onto this Intel T2 Mac
- paste API keys, Tailscale auth keys, or Wi-Fi passwords into chat
- install unofficial ChatGPT wrappers

## ChatGPT Linux desktop

Official OpenAI communications describe a Linux desktop preview for Ubuntu 26.04 x64, downloaded from `https://openai.com/codex/`.

This bootstrap does not fetch community-posted package URLs. If the official page cannot be verified from the installer, status is:

`CHATGPT_LINUX_DESKTOP=BLOCKED_OFFICIAL_SOURCE_NOT_VERIFIED`

To continue on the host, save the official amd64 Debian package from the OpenAI download surface and rerun:

`CHATGPT_OFFICIAL_DEB=/path/to/official.deb ./install-ai-tools.sh`

Replace the path with the local official file. Do not commit that package.

## Human gates

Installers stop for:

- `SUDO_HUMAN_GATE`
- `GIT_IDENTITY_HUMAN_GATE`
- `GITHUB_AUTH_HUMAN_GATE`
- `CURSOR_AUTH_HUMAN_GATE`
- `CHATGPT_LOGIN_HUMAN_GATE`
- `CODEX_LOGIN_HUMAN_GATE`
- `TAILSCALE_AUTH_HUMAN_GATE`
- `READY_FOR_CONTROLLED_REBOOT`

Do not reboot from these scripts.

## Cloud agents

Do not run `install-core.sh` or `install-ai-tools.sh` from Cursor Cloud Agents or other remote VMs. Those environments will fail `HOST_GUARD` by design.
