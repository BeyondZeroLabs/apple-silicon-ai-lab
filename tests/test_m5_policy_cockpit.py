from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "m5_policy_cockpit", ROOT / "scripts/m5_policy_cockpit.py"
)
assert SPEC and SPEC.loader
COCKPIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COCKPIT)


def valid_request() -> dict:
    return {
        "schema_version": "1.0",
        "request_id": "public-doc-pilot-001",
        "action": "approve_goal",
        "repository": "BeyondZeroLabs/apple-silicon-ai-lab",
        "data_classification": "PUBLIC",
        "risk_class": "LOW",
        "human_owner_role": "m5_policy_owner",
        "human_confirmation": True,
        "candidate_ref": "synthetic-documentation-change",
        "rollback_ref": "documented-git-revert-plan",
        "evidence": {
            "contracts_accepted": True,
            "deterministic_tests_passed": True,
            "privacy_scan_passed": True,
            "independent_review_passed": True,
            "rollback_documented": True,
            "scope_is_public_safe": True,
        },
    }


class PolicyCockpitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (ROOT / ".factory-state").mkdir(mode=0o700, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            (ROOT / ".factory-state").rmdir()
        except OSError:
            pass

    def setUp(self) -> None:
        self.policy = COCKPIT.load_policy()

    def test_valid_request_is_approved_without_execution(self) -> None:
        decision = COCKPIT.evaluate(valid_request(), self.policy)
        self.assertEqual(decision["decision"], "APPROVED_FOR_HUMAN_ACTION")
        self.assertFalse(decision["executes_action"])
        self.assertFalse(decision["network_used"])
        self.assertFalse(decision["protected_storage_accessed"])

    def test_non_public_request_is_denied(self) -> None:
        request = valid_request()
        request["data_classification"] = "PRIVATE"
        self.assertEqual(COCKPIT.evaluate(request, self.policy)["decision"], "DENIED")

    def test_missing_human_confirmation_is_denied(self) -> None:
        request = valid_request()
        request["human_confirmation"] = False
        self.assertEqual(COCKPIT.evaluate(request, self.policy)["decision"], "DENIED")

    def test_model_promotion_is_denied(self) -> None:
        request = valid_request()
        request["action"] = "promote_model"
        self.assertEqual(COCKPIT.evaluate(request, self.policy)["decision"], "DENIED")

    def test_unknown_fields_are_denied(self) -> None:
        request = valid_request()
        request["command"] = "merge-now"
        self.assertEqual(COCKPIT.evaluate(request, self.policy)["decision"], "DENIED")

    def test_sensitive_request_file_is_rejected(self) -> None:
        path = ROOT / "examples/m5-policy-cockpit/test-sensitive-request.json"
        try:
            request = valid_request()
            request["candidate_ref"] = "/" + "Users" + "/private/protected-input"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT._read_public_json(path)
        finally:
            path.unlink(missing_ok=True)

    def test_create_exclusive_receipt_refuses_overwrite(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            root = Path(directory) / "receipts"
            policy = dict(self.policy, receipt_root=str(root.relative_to(ROOT)))
            first, _ = COCKPIT.record_receipt(
                request, "a" * 64, decision, policy, human_confirmed=True
            )
            self.assertTrue(first.exists())
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.record_receipt(
                    request, "a" * 64, decision, policy, human_confirmed=True
                )
            self.assertEqual(COCKPIT.verify_receipts(policy)["receipt_count"], 1)

    def test_policy_rejects_missing_unknown_and_weakened_fields(self) -> None:
        variants = []
        missing = dict(self.policy)
        missing.pop("prohibited_capabilities")
        variants.append(missing)
        unknown = dict(self.policy, override=True)
        variants.append(unknown)
        weakened = dict(self.policy, prohibited_capabilities=[])
        variants.append(weakened)
        for index, value in enumerate(variants):
            path = ROOT / f"config/software-factory/test-policy-{index}.json"
            try:
                path.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(COCKPIT.CockpitError):
                    COCKPIT.load_policy(path)
            finally:
                path.unlink(missing_ok=True)

    def test_duplicate_policy_field_is_rejected(self) -> None:
        path = ROOT / "config/software-factory/test-duplicate-policy.json"
        raw = json.dumps(self.policy)
        raw = raw[:-1] + ', "mode": "interactive_only"}'
        try:
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.load_policy(path)
        finally:
            path.unlink(missing_ok=True)

    def test_broad_receipt_directory_permissions_are_rejected(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            root = Path(directory) / "receipts"
            root.mkdir(mode=0o700)
            root.chmod(0o755)
            policy = dict(self.policy, receipt_root=str(root.relative_to(ROOT)))
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.record_receipt(
                    request, "a" * 64, decision, policy, human_confirmed=True
                )

    def test_intermediate_receipt_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            parent = Path(directory)
            outside = parent / "outside"
            outside.mkdir(mode=0o700)
            link = parent / "link"
            link.symlink_to(outside, target_is_directory=True)
            policy = dict(
                self.policy,
                receipt_root=str((link / "receipts").relative_to(ROOT)),
            )
            with self.assertRaises((COCKPIT.CockpitError, OSError)):
                COCKPIT.verify_receipts(policy)

    def test_modified_receipt_fields_and_filename_are_rejected(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            root = Path(directory) / "receipts"
            policy = dict(self.policy, receipt_root=str(root.relative_to(ROOT)))
            receipt, _ = COCKPIT.record_receipt(
                request, "a" * 64, decision, policy, human_confirmed=True
            )
            original = json.loads(receipt.read_text(encoding="utf-8"))
            altered = dict(original, decision="DENIED")
            receipt.write_text(json.dumps(altered), encoding="utf-8")
            receipt.chmod(0o600)
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.verify_receipts(policy)
            receipt.write_text(json.dumps(original), encoding="utf-8")
            receipt.chmod(0o600)
            renamed = receipt.with_name("different-request.json")
            receipt.rename(renamed)
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.verify_receipts(policy)

    def test_receipt_with_broad_file_permissions_is_rejected(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            root = Path(directory) / "receipts"
            policy = dict(self.policy, receipt_root=str(root.relative_to(ROOT)))
            receipt, _ = COCKPIT.record_receipt(
                request, "a" * 64, decision, policy, human_confirmed=True
            )
            receipt.chmod(0o644)
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT.verify_receipts(policy)

    def test_directory_replacement_cannot_redirect_receipt_write(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with tempfile.TemporaryDirectory(dir=ROOT / ".factory-state") as directory:
            parent = Path(directory)
            receipts = parent / "receipts"
            receipts.mkdir(mode=0o700)
            moved = parent / "receipts-opened"
            outside = parent / "outside"
            outside.mkdir(mode=0o700)
            policy = dict(self.policy, receipt_root=str(receipts.relative_to(ROOT)))
            real_open = os.open
            replaced = False

            def racing_open(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal replaced
                if (
                    not replaced
                    and isinstance(path, str)
                    and path.endswith(".json")
                    and dir_fd is not None
                ):
                    receipts.rename(moved)
                    receipts.symlink_to(outside, target_is_directory=True)
                    replaced = True
                return real_open(path, flags, mode, dir_fd=dir_fd)

            with mock.patch.object(COCKPIT.os, "open", side_effect=racing_open):
                COCKPIT.record_receipt(
                    request, "a" * 64, decision, policy, human_confirmed=True
                )
            self.assertTrue((moved / f'{request["request_id"]}.json').is_file())
            self.assertEqual(list(outside.iterdir()), [])

    def test_raw_oserror_is_sanitized(self) -> None:
        stderr = io.StringIO()
        with mock.patch.object(
            COCKPIT, "load_policy", side_effect=OSError("/private/sensitive/path")
        ):
            with redirect_stderr(stderr):
                status = COCKPIT.main(["verify-receipts"])
        self.assertEqual(status, 2)
        self.assertIn("filesystem or encoding operation failed", stderr.getvalue())
        self.assertNotIn("/private/sensitive/path", stderr.getvalue())

    def test_receipt_requires_live_human_confirmation_flag(self) -> None:
        request = valid_request()
        decision = COCKPIT.evaluate(request, self.policy)
        with self.assertRaises(COCKPIT.CockpitError):
            COCKPIT.record_receipt(
                request, "a" * 64, decision, self.policy, human_confirmed=False
            )

    def test_receipt_root_cannot_escape_factory_state(self) -> None:
        policy = dict(self.policy, receipt_root="receipts")
        with self.assertRaises(COCKPIT.CockpitError):
            COCKPIT.verify_receipts(policy)

    def test_input_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            temp = Path(directory)
            target = temp / "request.json"
            target.write_text(json.dumps(valid_request()), encoding="utf-8")
            link = temp / "link.json"
            link.symlink_to(target)
            with self.assertRaises(COCKPIT.CockpitError):
                COCKPIT._read_public_json(link)


if __name__ == "__main__":
    unittest.main()
