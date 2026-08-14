# Neuromancer AI/ML capability

Do not install large models from these notes. This is a capability ceiling, not a benchmark result.

## Hardware family

`MacBookPro16,1` is the 2019 16-inch Intel MacBook Pro with a T2 chip. Public product family ranges:

- CPU: Coffee Lake 6-core or 8-core Intel Core i7/i9
- Memory: historically 16 GB, 32 GB, or 64 GB depending on configuration
- Graphics: Intel UHD 630 plus AMD Radeon Pro 5300M or 5500M
- Storage: internal NVMe, commonly around 1 TB on this node family
- Network: Broadcom BCM4364 Bali over `brcmfmac` after `apple-firmware`

The proposed factory inventory recorded this Intel notebook as a 16 GB machine. That figure is a prior inventory claim, not a fresh on-host measurement. Measure RAM on the laptop before selecting any local model.

## Acceleration under Ubuntu on T2

Do not assume Apple Silicon-style unified memory or MLX.

Expected class:

- CPU: usable for compile, test, and light agent tooling
- Intel iGPU: may provide modest VAAPI/OpenCL depending on the running kernel
- AMD dGPU: historically unreliable or incomplete on T2 Linux; treat as unavailable until an on-host `lspci` plus renderer probe says otherwise
- CUDA: not present
- ROCm/MLX: not a default path on this node

Thermals: this is a thin Intel notebook. Sustained all-core plus GPU inference is a poor fit even if a dGPU probe later succeeds.

## Model-size ceiling

Until on-host RAM is recorded, use the conservative 16 GB class:

- default: no local model runtime and no model downloads
- experimental ceiling if later approved: CPU-only quantized 3B-7B class for smoke tests only
- not worthwhile: 14B+, 30B+, GPU-quantized serving, or anything that contends with the desktop session
- never: treat this node as a replacement for Studio or M5 local inference

If on-host RAM is 32 GB or 64 GB, the ceiling can be revisited. That is a later measurement, not a current promotion.

## Performance class

Expected contribution to the Software Factory:

- x86_64 compatibility builds and tests
- Ubuntu-native Cursor/Codex/ChatGPT desktop workflows
- recovery and archive verification
- browser-side checks that should not occupy Apple Silicon inference nodes

Unexpected contribution:

- high-throughput local generation
- embedding/index serving
- unattended multi-slot inference

## Recommendation

Keep Ollama and other model runtimes deferred. Reassess only after the local inventory records RAM, free disk, GPU renderer status, and a thermal sample under a bounded compile or test workload.
