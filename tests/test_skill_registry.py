from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_skill_registry.py"
REGISTRY = ROOT / "config/software-factory/skill-registry.json"

spec = importlib.util.spec_from_file_location("skill_registry_validator", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(validator)


def canonical(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def valid_entry() -> dict:
    return {
        "artifact_type": "INSTRUCTION_ONLY",
        "deployment_enabled": False,
        "effective_capabilities": {"filesystem_write": "DENY", "network": "DENY"},
        "evidence": {
            "cross_harness_parity": "NOT_RUN",
            "human_approval": "NOT_RUN",
            "independent_review": "NOT_RUN",
            "privacy_review": "NOT_RUN",
            "rollback_rehearsal": "NOT_RUN",
            "sandbox_test": "NOT_RUN",
            "static_security_review": "NOT_RUN",
        },
        "id": "synthetic-candidate",
        "license": "MIT",
        "manifest": ["SKILL.md", "references/public-example.md"],
        "requested_capabilities": ["filesystem_write", "network"],
        "source": {
            "artifact_sha256": "b" * 64,
            "repository": "https://github.com/example/public-skills",
            "revision": "a" * 40,
        },
        "state": "QUARANTINED",
    }


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def validate(self, value: dict, raw: str | None = None) -> None:
        validator.validate(value, raw if raw is not None else canonical(value))

    def assert_invalid(self, code: str, value: dict, raw: str | None = None) -> None:
        with self.assertRaisesRegex(validator.Invalid, f"^{code}$"):
            self.validate(value, raw)

    def test_empty_design_registry_is_valid(self) -> None:
        self.validate(self.base, REGISTRY.read_text(encoding="utf-8"))

    def test_quarantined_deny_only_candidate_is_valid(self) -> None:
        value = copy.deepcopy(self.base)
        value["entries"] = [valid_entry()]
        self.validate(value)

    def test_unknown_top_field_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["unexpected"] = True
        self.assert_invalid("TOP_SCHEMA", value)

    def test_weakened_data_boundary_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["data_boundary"]["prohibited"].remove("PII")
        self.assert_invalid("PROHIBITED_DATA", value)

    def test_enabled_harness_fails(self) -> None:
        value = copy.deepcopy(self.base)
        value["harnesses"]["pi"]["deployment_enabled"] = True
        self.assert_invalid("HARNESS_ENABLED", value)

    def test_enabled_entry_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["deployment_enabled"] = True
        value["entries"] = [entry]
        self.assert_invalid("DEPLOYMENT_ENABLED", value)

    def test_capability_grant_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["effective_capabilities"]["network"] = "ALLOW"
        value["entries"] = [entry]
        self.assert_invalid("CAPABILITY_GRANT", value)

    def test_mutable_revision_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["source"]["revision"] = "main"
        value["entries"] = [entry]
        self.assert_invalid("SOURCE_REVISION", value)

    def test_non_github_or_credentialed_url_fails(self) -> None:
        for url in ("http://github.com/example/repo", "https://example.com/a/b", "https://user@github.com/a/b"):
            with self.subTest(url=url):
                value = copy.deepcopy(self.base)
                entry = valid_entry()
                entry["source"]["repository"] = url
                value["entries"] = [entry]
                self.assert_invalid("SOURCE_URL", value)

    def test_manifest_traversal_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["manifest"] = ["../private.txt"]
        value["entries"] = [entry]
        self.assert_invalid("MANIFEST_PATH", value)

    def test_unsorted_manifest_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["manifest"] = ["z.md", "a.md"]
        value["entries"] = [entry]
        self.assert_invalid("MANIFEST_ORDER", value)

    def test_premature_pass_fails(self) -> None:
        value = copy.deepcopy(self.base)
        entry = valid_entry()
        entry["evidence"]["privacy_review"] = "PASS"
        value["entries"] = [entry]
        self.assert_invalid("PREMATURE_EVIDENCE", value)

    def test_noncanonical_json_fails(self) -> None:
        self.assert_invalid("NONCANONICAL", self.base, json.dumps(self.base) + "\n")

    def test_duplicate_json_key_fails_closed(self) -> None:
        raw = REGISTRY.read_text(encoding="utf-8").replace(
            '  "schema_version": 1,', '  "schema_version": 1,\n  "schema_version": 1,'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(raw, encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), str(path)], capture_output=True, text=True, check=False
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "SKILL_REGISTRY_INVALID:DUPLICATE_KEY")

    def test_cli_emits_stable_success(self) -> None:
        result = subprocess.run(
            ["python3", str(VALIDATOR), str(REGISTRY)], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "SKILL_REGISTRY_VALID")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
