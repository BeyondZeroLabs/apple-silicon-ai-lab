# T2 Wi-Fi recovery

This is the public-safe recovery record for native Wi-Fi on the Neuromancer Intel T2 Ubuntu node.

Do not print or store Wi-Fi passwords here.

## Known-good repair

Pre-repair failure:

- `brcmfmac` loaded
- Bali firmware files were absent
- direct firmware loads returned error `-2`
- dongle setup failed

Repair:

- installed the verified offline Debian package `apple-firmware` version `14.8.3-1`
- firmware payload was SHA256-verified before installation on the host
- after install, `wlp5s0` appeared, scanning worked, and internet/DNS checks passed

Working stack:

- driver: `brcmfmac`
- chip: Broadcom BCM4364 stepping B3 / Bali
- interface: `wlp5s0`
- package: `apple-firmware 14.8.3-1`

## Provenance

`apple-firmware` is the T2 Linux firmware package described by the [t2linux Wi-Fi guide](https://wiki.t2linux.org/guides/wifi-bluetooth/). It is not an Ubuntu archive package and is not Apple Silicon firmware.

Keep a copy of the verified `.deb` in the machine-local recovery directory:

`$HOME/BeyondZero/neuromancer/recovery/`

Record the SHA256 of that exact file next to it. Do not commit the binary or the hash file to this public repository. Do not depend permanently on removable media.

## Do not

- install `broadcom-wl`
- remove `apple-firmware` while native Wi-Fi is the required path
- replace working Bali/`brcmfmac` firmware without a recorded justification
- copy Apple Silicon firmware onto this Intel T2 Mac
- run `apt autoremove` blindly
- replace the working kernel without `KERNEL_T2_CHANGE_GATE`
- modify EFI or partitions as part of Wi-Fi recovery

## Read-only health check

On the host:

```bash
./examples/neuromancer-bootstrap/network-health.sh
```

The check must remain read-only. It must not print stored NetworkManager secrets.

## Reinstall procedure

Only if native Wi-Fi is broken and the local verified package is present:

1. Confirm `network-health.sh` failures and kernel/`apple-firmware` versions.
2. Confirm the local `.deb` SHA256 matches the locally recorded hash.
3. Install that exact package with `apt`, not a random newer file.
4. Reload is usually unnecessary after reboot; do not unload `brcmfmac` unless the host is already degraded.
5. Re-run `network-health.sh`.

If the local verified package is missing, recover it from the original verified offline copy. Do not substitute Apple Silicon firmware.

## Kernel or firmware changes

Before any kernel, firmware, or T2-stack change, evaluate the effect on this known-good Wi-Fi configuration and stop for:

`KERNEL_T2_CHANGE_GATE`
