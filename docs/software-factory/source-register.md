# Source register

Retrieved 2026-07-19. Primary implementation sources support architecture claims; X posts are discovery and practitioner signals, not proof of product performance.

## Primary sources

- Brace Sproul, “LangChain's Open-Source Software Factory”: https://x.com/BraceSproul/status/2078558852921094253
- Deep Agents overview: https://docs.langchain.com/oss/python/deepagents/overview
- Deep Agents Code / dcode: https://docs.langchain.com/oss/python/deepagents/code/overview
- OpenSWE repository: https://github.com/langchain-ai/open-swe
- OpenSWE reviewer implementation: https://github.com/langchain-ai/open-swe/blob/main/agent/reviewer.py
- OpenWiki repository: https://github.com/langchain-ai/openwiki
- LangSmith evaluators: https://docs.langchain.com/langsmith/evaluators
- LangSmith trajectory evaluations: https://docs.langchain.com/langsmith/trajectory-evals
- LangSmith Engine: https://docs.langchain.com/langsmith/engine
- Imbue Vet: https://github.com/imbue-ai/vet
- OpenInference: https://github.com/Arize-ai/openinference
- Phoenix: https://github.com/Arize-ai/phoenix
- Ollama API: https://docs.ollama.com/api/introduction
- llama.cpp server: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
- Hugging Face Hub pinned downloads: https://huggingface.co/docs/huggingface_hub/guides/download

## Phase 2 skill supply-chain sources

Retrieved 2026-07-21. These sources are discovery inputs only; no external skill content is imported or approved by the registry.

- Addy Osmani practitioner signal: https://x.com/addyosmani/status/2079442194449232227
- Agent Skills repository: https://github.com/addyosmani/agent-skills
- Agent Skills anatomy: https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md
- Agent Skills cross-agent installation notes: https://github.com/addyosmani/agent-skills/blob/main/agents/README.md
- Context engineering example: https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md
- GBrain repository: https://github.com/garrytan/gbrain
- GBrain product/architecture overview: https://gbrain.homes/
- GBrain security policy: https://github.com/garrytan/gbrain/blob/master/SECURITY.md

## X practitioner signals

- Runtime traces as proposals for harness improvements: https://x.com/tetsuoai/status/2032031965575332172
- Independent agent-output verification and CI: https://x.com/imbue_ai/status/2031762951343100411
- Long-running agents need decomposition, fresh context, validators, and telemetry: https://x.com/systematicls/status/2038241033755168959
- Agent-speed infrastructure and permission/version-control complexity: https://x.com/levie/status/2038468564500537416
- Local inference concurrency can exhaust context/KV capacity: https://x.com/alexdolbun/status/2062999902158807085
- Review bottlenecks and silent failures remain human-accountability problems: https://x.com/kaxil/status/2037503513350005134
- Planner/worker/validator structure is preferred over unconstrained swarms: https://x.com/mihail_eric/status/2032145866614849665

## Verification notes

- OpenWiki can maintain repository documentation and open automated documentation PRs, but it also writes marked blocks to `AGENTS.md` and `CLAUDE.md`, stores provider secrets in a local `.env`, and enables anonymous telemetry by default. A BZ pilot must disable telemetry and protect human-authored authority blocks.
- OpenSWE Review treats traces and historical review text as untrusted, uses bounded diff materialization, ranks concrete failure modes by severity/confidence, supports dry-run semantics, and prohibits review agents from committing or pushing. These are adoptable controls independent of the framework.
- Vet is AGPL-3.0, supports terminal/skill/CI use, structured exit codes, custom issue guides, and OpenAI-compatible model endpoints. License and process-isolation review are required before adoption.
- OpenInference is an OpenTelemetry-compatible convention. Phoenix can run locally and supports traces, datasets, experiments, replay, and evaluation, but is Elastic License 2.0 and enables basic product telemetry by default. Use only after license/data review and set `PHOENIX_TELEMETRY_ENABLED=false`.
- Ollama serves a local API at `127.0.0.1:11434`; llama.cpp exposes OpenAI-compatible routes, monitoring, continuous batching, and structured JSON. BZ should normalize both behind one adapter contract.
- Hugging Face downloads must be pinned to a commit revision. Production routing must also record artifact hashes because a repository revision can contain multiple files and quantizations.
- External skill collections demonstrate reusable lifecycle guidance across harnesses, but their installation mechanisms and mutable upstream content are not authority. BeyondZeroLabs must use immutable provenance, local quarantine, deny-only capabilities, per-harness validation, explicit human promotion and rollback before any candidate is enabled.
- GBrain supports a local PGLite database and MCP clients including Codex and Cursor, while its full setup can also load skills, request API credentials, ingest personal communications and notes, and schedule autonomous background work. It therefore enters as a disabled memory candidate with separate runtime/data and skill-supply-chain gates; the public/synthetic pilot must not use its autonomous installer or ingest protected material.
