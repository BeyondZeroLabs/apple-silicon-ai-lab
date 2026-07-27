from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_public_repository_safety",
    ROOT / "scripts" / "validate_public_repository_safety.py",
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class PublicRepositorySafetyTests(unittest.TestCase):
    def assert_text_rejected(self, value: str, code: str) -> None:
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_text(value)
        self.assertEqual(str(caught.exception), code)

    def assert_path_rejected(self, value: str, code: str) -> None:
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_relative_path(value)
        self.assertEqual(str(caught.exception), code)

    def test_public_safe_text_passes(self) -> None:
        VALIDATOR.validate_text("Synthetic public benchmark documentation.")

    def test_github_token_shape_fails(self) -> None:
        self.assert_text_rejected(
            "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "CREDENTIAL_SHAPE",
        )

    def test_api_token_shape_fails(self) -> None:
        self.assert_text_rejected(
            "sk-" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "CREDENTIAL_SHAPE",
        )

    def test_private_key_header_fails(self) -> None:
        self.assert_text_rejected(
            "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
            "PRIVATE_KEY_MATERIAL",
        )

    def test_private_home_path_fails(self) -> None:
        self.assert_text_rejected(
            "/" + "Users" + "/example/private.txt",
            "PRIVATE_HOME_PATH",
        )

    def test_private_chat_link_fails(self) -> None:
        self.assert_text_rejected(
            "https://" + "chatgpt.com" + "/c/example-private-id",
            "PRIVATE_CHAT_LINK",
        )

    def test_protected_runtime_path_fails(self) -> None:
        self.assert_path_rejected(
            "agent_bridge/runtime.json",
            "PROHIBITED_PATH",
        )

    def test_case_memory_path_fails(self) -> None:
        self.assert_path_rejected(
            "CASE_BRAIN/index.json",
            "PROHIBITED_PATH",
        )

    def test_archive_path_fails(self) -> None:
        self.assert_path_rejected(
            "fixtures/evidence.zip",
            "PROHIBITED_FILE_TYPE",
        )

    def test_binary_content_fails(self) -> None:
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_bytes(b"safe\x00binary")
        self.assertEqual(str(caught.exception), "BINARY_FILE")

    def test_oversized_content_fails(self) -> None:
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_bytes(b"a" * (VALIDATOR.MAX_FILE_BYTES + 1))
        self.assertEqual(str(caught.exception), "FILE_TOO_LARGE")


if __name__ == "__main__":
    unittest.main()
