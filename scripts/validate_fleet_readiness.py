#!/usr/bin/env python3
"""Fail-closed validator for install-free Software Factory fleet readiness contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/software-factory/fleet-readiness.json"

TOP_KEYS = {
    "authority",
    "comprehension_budget",
    "fleet_ceilings",
    "global_prohibited_authorities",
    "id",
    "machines",
    "policy_revision",
    "schema_version",
    "status",
}
AUTHORITY_KEYS = {"goal_budget_reference", "operational_reference"}
BUDGET_KEYS = {
    "exhaustion_behavior",
    "machines_must_declare_budget_compliance",
    "optional_fields",
    "reference",
    "required_fields",
}
CEILING_KEYS = {
    "comprehension_budget_reference",
    "maximum_active_coordinator_leases_per_repository",
    "maximum_concurrent_goals_per_repository",
    "model_endpoint_binding",
    "relay_allowed_nodes",
}
MACHINE_KEYS = {
    "authority_ceiling",
    "deployment_state",
    "id",
    "mobile_limitations",
    "openclaw_active",
    "primary_role",
    "readiness_checklist",
    "role_exclusions",
}
CEILING_FIELD_KEYS = {
    "coordinator_lease",
    "independent_merge",
    "model_promotion",
    "network_bind",
    "protected_storage_write",
    "service_install",
    "standing_coordination",
}
MOBILE_KEYS = {
    "attach_to_mac_hosted_sessions_only",
    "autonomous_authority",
    "code_execution",
    "merge_authority",
    "persistent_runtime",
    "promotion_authority",
}
WATCH_MOBILE_KEYS = MOBILE_KEYS | {"protected_action_authorization"}
APPROVED_MACHINE_IDS = [
    "ipad",
    "iphone",
    "mac-mini-m4",
    "mac-studio-m4-max",
    "mbp-intel-2019",
    "mbp-m4-pro",
    "mbp-m5-max",
    "watch",
]
MOBILE_MACHINE_IDS = {"ipad", "iphone", "watch"}
GLOBAL_PROHIBITED = {
    "automatic_merge",
    "coordinator_lease_without_human_approval",
    "credential_export",
    "fleet_service_install",
    "model_download",
    "network_service_bind",
    "protected_storage_write",
    "remote_exposure",
}
BUDGET_REQUIRED = ["maximum_attempts", "maximum_concurrency", "wall_clock_seconds"]
BUDGET_OPTIONAL = [
    "maximum_cost_usd",
    "maximum_energy_proxy",
    "maximum_input_tokens",
    "maximum_output_tokens",
]
RELAY_ALLOWED = ["mac-studio-m4-max"]
OPENCLAW_INACTIVE_MACHINE = "mac-mini-m4"
POLICY_REVISION = "2561e4bbbf7a21f9989d11df0e29b54ffae7d266"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


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


def sorted_unique(items: list[str], code: str) -> None:
    if items != sorted(items):
        fail(code)


def approved_config_path(path: Path) -> Path:
    if path.absolute() != DEFAULT_CONFIG:
        fail("CONFIG_PATH")
    return path


def parse_unique(raw: str) -> dict:
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
    approved_config_path(path)
    raw = DEFAULT_CONFIG.read_text(encoding="utf-8")
    return parse_unique(raw), raw


def validate_mobile_limitations(machine_id: str, value: object) -> None:
    if machine_id in MOBILE_MACHINE_IDS:
        keys = WATCH_MOBILE_KEYS if machine_id == "watch" else MOBILE_KEYS
        limits = exact_keys(value, keys, "MOBILE_LIMITATIONS")
        for key, expected in limits.items():
            if key == "attach_to_mac_hosted_sessions_only":
                if expected is not True:
                    fail("MOBILE_LIMITATION")
            elif expected is not False:
                fail("MOBILE_LIMITATION")
        return
    if value is not None:
        fail("MOBILE_LIMITATIONS")


def validate_openclaw(machine_id: str, value: object) -> None:
    if machine_id == OPENCLAW_INACTIVE_MACHINE:
        if value is not False:
            fail("OPENCLAW_INACTIVE")
        return
    if value is not None:
        fail("OPENCLAW_FIELD")


def validate_authority_ceiling(machine_id: str, value: object) -> None:
    ceiling = exact_keys(value, CEILING_FIELD_KEYS, "AUTHORITY_CEILING")
    if any(not isinstance(item, bool) for item in ceiling.values()):
        fail("AUTHORITY_CEILING")
    if machine_id == "mac-studio-m4-max":
        if not ceiling["coordinator_lease"] or not ceiling["standing_coordination"]:
            fail("STUDIO_CEILING")
        return
    if machine_id == "mbp-m4-pro":
        if not ceiling["coordinator_lease"] or ceiling["standing_coordination"]:
            fail("M4PRO_CEILING")
        return
    if any(ceiling[key] for key in CEILING_FIELD_KEYS):
        fail("AUTHORITY_CEILING")


def validate_machine(machine: object) -> None:
    machine = exact_keys(machine, MACHINE_KEYS, "MACHINE_SCHEMA")
    machine_id = machine["id"]
    if not isinstance(machine_id, str) or machine_id not in APPROVED_MACHINE_IDS:
        fail("MACHINE_ID")

    exclusions = string_list(machine["role_exclusions"], "ROLE_EXCLUSIONS")
    sorted_unique(exclusions, "ROLE_EXCLUSIONS")
    checklist = string_list(machine["readiness_checklist"], "READINESS_CHECKLIST")
    sorted_unique(checklist, "READINESS_CHECKLIST")
    if not checklist:
        fail("READINESS_CHECKLIST")

    required = {"network_service_bind", "protected_storage_write"}
    required.add("service_install" if machine_id in MOBILE_MACHINE_IDS else "fleet_service_install")
    if not required.issubset(set(exclusions)):
        fail("ROLE_EXCLUSION_REQUIRED")

    if machine_id in MOBILE_MACHINE_IDS and not {
        "autonomous_authority",
        "code_execution",
        "coordinator_lease",
        "merge_authority",
        "model_promotion",
        "persistent_runtime",
        "service_install",
    }.issubset(set(exclusions)):
        fail("MOBILE_ROLE_EXCLUSIONS")

    validate_mobile_limitations(machine_id, machine["mobile_limitations"])
    validate_openclaw(machine_id, machine["openclaw_active"])
    validate_authority_ceiling(machine_id, machine["authority_ceiling"])


def validate(value: dict, raw: str) -> None:
    exact_keys(value, TOP_KEYS, "TOP_SCHEMA")
    if value["schema_version"] != "1.0" or value["id"] != "bz-fleet-readiness-contract":
        fail("IDENTITY")
    if value["status"] != "DESIGN_ONLY_INSTALL_FREE":
        fail("STATUS")
    if value["policy_revision"] != POLICY_REVISION or not SHA40.fullmatch(value["policy_revision"]):
        fail("POLICY_REVISION")

    authority = exact_keys(value["authority"], AUTHORITY_KEYS, "AUTHORITY")
    if authority != {
        "goal_budget_reference": "docs/software-factory/goal-contract.yaml",
        "operational_reference": "docs/software-factory/implementation-roadmap.md",
    }:
        fail("AUTHORITY_REFERENCE")

    budget = exact_keys(value["comprehension_budget"], BUDGET_KEYS, "COMPREHENSION_BUDGET")
    if budget["reference"] != "docs/software-factory/goal-contract.yaml":
        fail("COMPREHENSION_REFERENCE")
    if budget["exhaustion_behavior"] != "PAUSED" or budget["machines_must_declare_budget_compliance"] is not True:
        fail("COMPREHENSION_BEHAVIOR")
    if string_list(budget["required_fields"], "COMPREHENSION_REQUIRED") != BUDGET_REQUIRED:
        fail("COMPREHENSION_REQUIRED")
    if string_list(budget["optional_fields"], "COMPREHENSION_OPTIONAL") != BUDGET_OPTIONAL:
        fail("COMPREHENSION_OPTIONAL")

    ceilings = exact_keys(value["fleet_ceilings"], CEILING_KEYS, "FLEET_CEILINGS")
    if ceilings["maximum_active_coordinator_leases_per_repository"] != 1:
        fail("LEASE_CEILING")
    if ceilings["maximum_concurrent_goals_per_repository"] != 1:
        fail("GOAL_CEILING")
    if ceilings["model_endpoint_binding"] != "loopback_only":
        fail("MODEL_BINDING")
    if ceilings["comprehension_budget_reference"] != "goal-contract.yaml:budget":
        fail("COMPREHENSION_REFERENCE")
    if string_list(ceilings["relay_allowed_nodes"], "RELAY_ALLOWED") != RELAY_ALLOWED:
        fail("RELAY_ALLOWED")

    prohibited = string_list(value["global_prohibited_authorities"], "GLOBAL_PROHIBITED")
    sorted_unique(prohibited, "GLOBAL_PROHIBITED")
    if set(prohibited) != GLOBAL_PROHIBITED:
        fail("GLOBAL_PROHIBITED")

    if not isinstance(value["machines"], list):
        fail("MACHINES")
    ids = [machine["id"] for machine in value["machines"]]
    if ids != sorted(APPROVED_MACHINE_IDS) or len(ids) != len(set(ids)):
        fail("MACHINE_ORDER")
    for machine in value["machines"]:
        validate_machine(machine)

    canonical = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if raw != canonical:
        fail("NONCANONICAL")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--sha256", action="store_true")
    try:
        args = parser.parse_args(argv)
        value, raw = load_unique(args.config)
        validate(value, raw)
        print("FLEET_READINESS_VALID")
        if args.sha256:
            print(f"FLEET_READINESS_SHA256={hashlib.sha256(raw.encode()).hexdigest()}")
        return 0
    except (Invalid, SystemExit) as exc:
        code = str(exc) if isinstance(exc, Invalid) else "ARGUMENTS"
        print(f"FLEET_READINESS_INVALID:{code}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
