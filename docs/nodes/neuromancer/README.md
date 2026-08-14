# Neuromancer node notes

Neuromancer is the BeyondZero Intel T2 MacBook Pro node running Ubuntu on x86_64.

This documentation is public-safe. It does not include Wi-Fi passwords, account identifiers, local home paths, or measured private inventory dumps.

## Execution rule

Finish configuration on the machine itself with a local Cursor desktop agent.

Do not migrate this bootstrap to Cursor Cloud Agents or other remote VMs. Remote environments fail the host guard in `examples/neuromancer-bootstrap`.

## Contents

- [T2 Wi-Fi recovery](T2_WIFI_RECOVERY.md)
- [Recommended role](NEUROMANCER_ROLE.md)
- [AI/ML capability ceiling](AI_ML_CAPABILITY.md)
- Host-guarded scripts: `examples/neuromancer-bootstrap/`

## Known-good invariants

These are the protected facts from the completed Ubuntu install and Wi-Fi repair. Re-measure on the host before treating them as current.

- Product: `MacBookPro16,1`
- Chipset: Intel T2
- Native Wi-Fi: Broadcom BCM4364 stepping B3 / Bali
- Driver: in-kernel `brcmfmac`
- Interface: `wlp5s0`
- Firmware package: `apple-firmware` `14.8.3-1`
- Native Wi-Fi after that package: pass

## What a cloud agent can do

A cloud agent can maintain these public-safe notes and scripts. It cannot:

- protect or test the live T2 Wi-Fi stack
- install Cursor desktop on the laptop
- complete browser authentication
- measure RAM, thermals, or GPU usefulness on the laptop
