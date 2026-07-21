#!/usr/bin/env python3
"""Deterministically validate the design-only Software Factory skill registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "config/software-factory/skill-registry.json"

TOP_KEYS = {
    "authority", "data_boundary", "entries", "harnesses", "lifecycle",
    "memory_candidates", "prohibited_defaults", "promotion_gates", "registry_id",
    "schema_version", "status",
}
HARNESS_KEYS = {"codex", "cursor", "grok_build", "hermes", "openclaw", "pi"}
ENTRY_KEYS = {
    "artifact_type", "deployment_enabled", "effective_capabilities", "evidence",
    "id", "license", "manifest", "requested_capabilities", "source", "state",
}
SOURCE_KEYS = {"artifact_sha256", "repository", "revision"}
EVIDENCE_KEYS = {
    "cross_harness_parity", "human_approval", "independent_review", "privacy_review",
    "rollback_rehearsal", "sandbox_test", "static_security_review",
}
MEMORY_KEYS = {
    "access_mode", "allowed_data", "deployment_enabled", "disabled_features", "id",
    "network_mode", "pilot_host", "prohibited_data", "runtime_accepted",
    "skill_pack_accepted", "source_repository", "source_revision",
    "standing_host_candidate", "state",
}
LIFECYCLE = [
    "DISCOVERED", "QUARANTINED", "STATIC_REVIEWED", "SANDBOX_TESTED",
    "HUMAN_APPROVED", "STAGED_READ_ONLY", "ENABLED_PER_HARNESS", "MONITORED", "REVOKED",
]
PROHIBITED = {
    "AUTOMATIC_INSTALL_OR_UPDATE", "CREDENTIAL_ACCESS", "HOOK_OR_PLUGIN_EXECUTION",
    "MCP_ENABLEMENT", "PERMISSION_EXPANSION", "PROTECTED_STORAGE_ACCESS",
    "SELF_APPROVAL", "SKILL_MANAGED_MERGE_OR_PROMOTION", "UNREVIEWED_NETWORK_ACCESS",
}
GATES = {
    "IMMUTABLE_PROVENANCE", "LICENSE_REVIEW", "STATIC_SECURITY_REVIEW", "PRIVACY_REVIEW",
    "ISOLATED_SANDBOX_TEST", "CROSS_HARNESS_PARITY", "ROLLBACK_REHEARSAL",
    "INDEPENDENT_REVIEW", "M5_HUMAN_PROMOTION",
}
GBRAIN_DISABLED = {
    "AUTONOMOUS_INSTALLER", "BACKGROUND_JOBS", "BULK_IMPORT", "CRON_DREAM_CYCLE",
    "EXTERNAL_INTEGRATIONS", "SKILL_OPTIMIZER", "SKILL_PACK", "WRITE_TOOLS",
}
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,79}\Z")


class Invalid(ValueError):
    """A stable, content-free validation failure."""


def fail(code: str) -> None:
    raise Invalid(code)


def exact_keys(value: object, keys: set[str], code: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        fail(code)
    return value


def string_list(value: object, code: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        fail(code)
    if len(value) != len(set(value)):
        fail(code)
    return value


def safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def safe_source_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    try:
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https" and parsed.hostname == "github.com" and port is None
        and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment
        and len([part for part in parsed.path.split("/") if part]) == 2
    )


def approved_registry_path(path: Path) -> Path:
    """Return the one approved registry path without following caller-selected links."""
    try:
        root = ROOT.resolve(strict=True)
        approved = DEFAULT_REGISTRY.resolve(strict=True)
        lexical = path.absolute()
        relative = lexical.relative_to(root)
    except (OSError, ValueError):
        fail("REGISTRY_PATH")

    cursor = root
    for part in relative.parts:
        cursor /= part
        try:
            if cursor.is_symlink():
                fail("REGISTRY_PATH")
        except OSError:
            fail("REGISTRY_PATH")

    try:
        resolved = lexical.resolve(strict=True)
        mode = resolved.stat().st_mode
    except OSError:
        fail("REGISTRY_PATH")
    if resolved != approved or not stat.S_ISREG(mode):
        fail("REGISTRY_PATH")
    return resolved


def parse_unique(raw: str) -> dict:
    """Parse JSON while rejecting duplicate object keys."""
    def pairs(items: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in items:
            if key in result:
                fail("DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (json.JSONDecodeError, UnicodeError):
        fail("JSON")
    if not isinstance(value, dict):
        fail("ROOT")
    return value


def load_unique(path: Path) -> tuple[dict, str]:
    path = approved_registry_path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        fail("READ")
    return parse_unique(raw), raw


def validate_entry(entry: object) -> None:
    entry = exact_keys(entry, ENTRY_KEYS, "ENTRY_SCHEMA")
    if not isinstance(entry["id"], str) or not SAFE_ID.fullmatch(entry["id"]):
        fail("ENTRY_ID")
    if entry["artifact_type"] != "INSTRUCTION_ONLY":
        fail("ARTIFACT_TYPE")
    if entry["deployment_enabled"] is not False:
        fail("DEPLOYMENT_ENABLED")
    if entry["state"] not in LIFECYCLE:
        fail("ENTRY_STATE")
    if not isinstance(entry["license"], str) or not entry["license"]:
        fail("LICENSE")

    source = exact_keys(entry["source"], SOURCE_KEYS, "SOURCE_SCHEMA")
    if not safe_source_url(source["repository"]):
        fail("SOURCE_URL")
    if not isinstance(source["revision"], str) or not SHA40.fullmatch(source["revision"]):
        fail("SOURCE_REVISION")
    if not isinstance(source["artifact_sha256"], str) or not SHA64.fullmatch(source["artifact_sha256"]):
        fail("ARTIFACT_HASH")

    manifest = entry["manifest"]
    if not isinstance(manifest, list) or not manifest or len(manifest) > 64:
        fail("MANIFEST")
    if manifest != sorted(manifest) or len(manifest) != len(set(manifest)):
        fail("MANIFEST_ORDER")
    if any(not safe_relative_path(item) for item in manifest):
        fail("MANIFEST_PATH")

    requested = string_list(entry["requested_capabilities"], "REQUESTED_CAPABILITIES")
    if any(not SAFE_ID.fullmatch(item) for item in requested):
        fail("REQUESTED_CAPABILITY")
    effective = entry["effective_capabilities"]
    if not isinstance(effective, dict) or set(effective) != set(requested):
        fail("EFFECTIVE_CAPABILITIES")
    if any(value != "DENY" for value in effective.values()):
        fail("CAPABILITY_GRANT")

    evidence = exact_keys(entry["evidence"], EVIDENCE_KEYS, "EVIDENCE_SCHEMA")
    if any(value not in {"NOT_RUN", "PASS", "FAIL"} for value in evidence.values()):
        fail("EVIDENCE_VALUE")
    if entry["state"] in {"DISCOVERED", "QUARANTINED"} and any(value == "PASS" for value in evidence.values()):
        fail("PREMATURE_EVIDENCE")


def validate_memory_candidate(candidate: object) -> None:
    candidate = exact_keys(candidate, MEMORY_KEYS, "MEMORY_SCHEMA")
    if candidate["id"] != "gbrain" or candidate["state"] != "QUARANTINED":
        fail("MEMORY_IDENTITY")
    if candidate["deployment_enabled"] is not False:
        fail("MEMORY_DEPLOYMENT")
    if candidate["runtime_accepted"] is not False or candidate["skill_pack_accepted"] is not False:
        fail("MEMORY_ACCEPTANCE")
    if candidate["source_repository"] != "https://github.com/garrytan/gbrain":
        fail("MEMORY_SOURCE")
    if candidate["source_revision"] != "UNPINNED":
        fail("MEMORY_REVISION")
    if candidate["access_mode"] != "READ_ONLY" or candidate["network_mode"] != "LOOPBACK_ONLY":
        fail("MEMORY_ACCESS")
    if candidate["pilot_host"] != "M5_ATTENDED" or candidate["standing_host_candidate"] != "MAC_MINI_ISOLATED":
        fail("MEMORY_HOST")
    if candidate["allowed_data"] != ["PUBLIC", "SYNTHETIC"]:
        fail("MEMORY_ALLOWED_DATA")
    if candidate["prohibited_data"] != ["CASE_BRAIN", "CREDENTIALS", "LEGAL_PRIVILEGED", "PII", "PRIVATE_STORAGE"]:
        fail("MEMORY_PROHIBITED_DATA")
    if set(string_list(candidate["disabled_features"], "MEMORY_DISABLED_FEATURES")) != GBRAIN_DISABLED:
        fail("MEMORY_DISABLED_FEATURES")


def validate(value: dict, raw: str) -> None:
    exact_keys(value, TOP_KEYS, "TOP_SCHEMA")
    if value["schema_version"] != 1 or value["registry_id"] != "bz-public-skill-registry":
        fail("IDENTITY")
    if value["status"] != "DESIGN_ONLY_NO_SKILLS_APPROVED":
        fail("STATUS")
    if value["lifecycle"] != LIFECYCLE:
        fail("LIFECYCLE")
    if set(string_list(value["promotion_gates"], "PROMOTION_GATES")) != GATES:
        fail("PROMOTION_GATES")
    if set(string_list(value["prohibited_defaults"], "PROHIBITED_DEFAULTS")) != PROHIBITED:
        fail("PROHIBITED_DEFAULTS")

    authority = exact_keys(value["authority"], {"human_promotion_required", "skills_may_grant_authority"}, "AUTHORITY")
    if authority != {"human_promotion_required": True, "skills_may_grant_authority": False}:
        fail("AUTHORITY_VALUE")
    boundary = exact_keys(value["data_boundary"], {"allowed", "prohibited"}, "DATA_BOUNDARY")
    if boundary["allowed"] != ["PUBLIC", "SYNTHETIC"]:
        fail("ALLOWED_DATA")
    if boundary["prohibited"] != ["CASE_BRAIN", "CREDENTIALS", "LEGAL_PRIVILEGED", "PII", "PRIVATE_STORAGE"]:
        fail("PROHIBITED_DATA")

    harnesses = exact_keys(value["harnesses"], HARNESS_KEYS, "HARNESSES")
    for harness in harnesses.values():
        harness = exact_keys(harness, {"deployment_enabled", "mode"}, "HARNESS_SCHEMA")
        if harness["deployment_enabled"] is not False or not isinstance(harness["mode"], str) or not harness["mode"].endswith("DESIGN_ONLY"):
            fail("HARNESS_ENABLED")

    if not isinstance(value["entries"], list):
        fail("ENTRIES")
    for entry in value["entries"]:
        validate_entry(entry)
    ids = [entry["id"] for entry in value["entries"]]
    if len(ids) != len(set(ids)):
        fail("DUPLICATE_ENTRY")

    if not isinstance(value["memory_candidates"], list) or len(value["memory_candidates"]) != 1:
        fail("MEMORY_CANDIDATES")
    validate_memory_candidate(value["memory_candidates"][0])

    canonical = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if raw != canonical:
        fail("NONCANONICAL")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("registry", nargs="?", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--sha256", action="store_true")
    try:
        args = parser.parse_args(argv)
        value, raw = load_unique(args.registry)
        validate(value, raw)
        print("SKILL_REGISTRY_VALID")
        if args.sha256:
            print(f"SKILL_REGISTRY_SHA256={hashlib.sha256(raw.encode()).hexdigest()}")
        return 0
    except (Invalid, SystemExit) as exc:
        code = str(exc) if isinstance(exc, Invalid) else "ARGUMENTS"
        print(f"SKILL_REGISTRY_INVALID:{code}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
