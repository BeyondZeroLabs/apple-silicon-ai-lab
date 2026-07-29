from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_fleet_readiness.py"
CONFIG = ROOT / "config/software-factory/fleet-readiness.json"

spec = importlib.util.spec_from_file_location("fleet_readiness_validator", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(validator)


def canonical(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


class FleetReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = json.loads(CONFIG.read_text(encoding="utf-8"))

    def validate(self, value: dict, raw: str | None = None) -> None:
        validator.validate(value, raw if raw is not None else canonical(value))

    def assert_invalid(self, code: str, value: dict, raw: str | None = None) -> None:
        with self.assertRaisesRegex(validator.Invalid, f"^{code}$"):
            self.validate(value, raw)

    def test_contract_is_valid(self) -> None:
        self.validate(self.base, CONFIG.read_text(encoding="utf-8"))

    def test_unknown_top_field_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["unexpected"] = True
        self.assert_invalid("TOP_SCHEMA", value)

    def test_weakened_global_prohibited_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["global_prohibited_authorities"].remove("fleet_service_install")
        self.assert_invalid("GLOBAL_PROHIBITED", value)

    def test_extra_relay_node_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["fleet_ceilings"]["relay_allowed_nodes"].append("mbp-m5-max")
        self.assert_invalid("RELAY_ALLOWED", value)

    def test_openclaw_active_on_mini_fails(self) -> None:
        value = copy.deepcopy(self.base)
        for machine in value["machines"]:
            if machine["id"] == "mac-mini-m4":
                machine["openclaw_active"] = True
        self.assert_invalid("OPENCLAW_INACTIVE", value)

    def test_studio_must_allow_standing_coordination(self) -> None:
        value = copy.deepcopy(self.base)
        for machine in value["machines"]:
            if machine["id"] == "mac-studio-m4-max":
                machine["authority_ceiling"]["standing_coordination"] = False
        self.assert_invalid("STUDIO_CEILING", value)

    def test_m4_pro_must_not_allow_standing_coordination(self) -> None:
        value = copy.deepcopy(self.base)
        for machine in value["machines"]:
            if machine["id"] == "mbp-m4-pro":
                machine["authority_ceiling"]["standing_coordination"] = True
        self.assert_invalid("M4PRO_CEILING", value)

    def test_mobile_must_declare_limitations(self) -> None:
        value = copy.deepcopy(self.base)
        for machine in value["machines"]:
            if machine["id"] == "iphone":
                machine["mobile_limitations"]["code_execution"] = True
        self.assert_invalid("MOBILE_LIMITATION", value)

    def test_mac_must_not_declare_mobile_limitations(self) -> None:
        value = copy.deepcopy(self.base)
        for machine in value["machines"]:
            if machine["id"] == "mbp-m5-max":
                machine["mobile_limitations"] = {"code_execution": False}
        self.assert_invalid("MOBILE_LIMITATIONS", value)

    def test_missing_comprehension_reference_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["comprehension_budget"]["reference"] = "docs/other.yaml"
        self.assert_invalid("COMPREHENSION_REFERENCE", value)

    def test_noncanonical_json_fails(self) -> None:
        self.assert_invalid("NONCANONICAL", self.base, json.dumps(self.base) + "\n")

    def test_duplicate_json_key_fails_closed(self) -> None:
        raw = CONFIG.read_text(encoding="utf-8").replace(
            '  "schema_version": "1.0",', '  "schema_version": "1.0",\n  "schema_version": "1.0",'
        )
        with self.assertRaisesRegex(validator.Invalid, "^DUPLICATE_KEY$"):
            validator.parse_unique(raw)

    def test_cli_rejects_config_outside_approved_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fleet-readiness.json"
            path.write_text(CONFIG.read_text(encoding="utf-8"), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), str(path)], capture_output=True, text=True, check=False
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "FLEET_READINESS_INVALID:CONFIG_PATH")

    def test_cli_emits_stable_success(self) -> None:
        result = subprocess.run(
            ["python3", str(VALIDATOR), str(CONFIG)], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "FLEET_READINESS_VALID")
        self.assertEqual(result.stderr, "")

    def test_all_approved_machines_present(self) -> None:
        ids = [machine["id"] for machine in self.base["machines"]]
        self.assertEqual(ids, sorted(validator.APPROVED_MACHINE_IDS))

    def test_mini_openclaw_is_inactive(self) -> None:
        mini = next(item for item in self.base["machines"] if item["id"] == "mac-mini-m4")
        self.assertFalse(mini["openclaw_active"])


if __name__ == "__main__":
    unittest.main()
