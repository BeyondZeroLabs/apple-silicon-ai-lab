from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

    def create_repository(
        self,
        root: Path,
        files: dict[str, str | bytes],
    ) -> Path:
        repository = root / "repo"
        repository.mkdir(parents=True)
        subprocess.run(
            ["git", "init", "-q", str(repository)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for raw_path, payload in files.items():
            path = repository / raw_path
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(payload, bytes):
                path.write_bytes(payload)
            else:
                path.write_text(payload, encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repository), "add", "."],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return repository

    def create_control_tree(self, root: Path, marker: str) -> Path:
        files = {
            path: f"{marker}:{path}\n"
            for path in VALIDATOR.PROTECTED_CONTROL_PATHS
        }
        return self.create_repository(root, files)

    def test_public_safe_text_passes(self) -> None:
        VALIDATOR.validate_text("Synthetic public benchmark documentation.")

    def test_common_credential_variants_fail(self) -> None:
        samples = (
            "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "glpat-" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "npm_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "sk-proj-" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            "AIza" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789",
            "AKIA" + "ABCDEFGHIJKLMNOP",
            "eyJ" + "A" * 15 + "." + "B" * 15 + "." + "C" * 15,
        )
        for sample in samples:
            with self.subTest(sample=sample[:4]):
                self.assert_text_rejected(sample, "CREDENTIAL_SHAPE")

    def test_secret_assignment_fails(self) -> None:
        self.assert_text_rejected(
            "client_" + "secret=" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "SECRET_ASSIGNMENT",
        )

    def test_private_key_header_fails(self) -> None:
        self.assert_text_rejected(
            "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
            "PRIVATE_KEY_MATERIAL",
        )

    def test_private_home_variants_fail(self) -> None:
        for sample in (
            "/" + "Users" + "/example/private.txt",
            "/" + "home" + "/example/private.txt",
            "C:\\\\" + "Users" + "\\\\example\\\\private.txt",
        ):
            with self.subTest(sample=sample[:3]):
                self.assert_text_rejected(sample, "PRIVATE_HOME_PATH")

    def test_private_chat_link_variants_fail(self) -> None:
        for sample in (
            "https://" + "chatgpt.com" + "/c/example-private-id",
            "https://" + "claude.ai" + "/epitaxy/example-private-id",
        ):
            with self.subTest(sample=sample[:8]):
                self.assert_text_rejected(sample, "PRIVATE_CHAT_LINK")

    def test_personal_identifier_shape_fails(self) -> None:
        for sample in (
            "123-" + "45-" + "6789",
            "person" + "@" + "example.com",
            "202" + "-555-" + "0147",
            "AA:BB:CC" + ":DD:EE:FF",
            "123e4567-" + "e89b-12d3-a456-426614174000",
        ):
            with self.subTest(sample=sample[:3]):
                self.assert_text_rejected(sample, "PERSONAL_IDENTIFIER_SHAPE")

    def test_sensitive_paths_fail(self) -> None:
        cases = (
            ("agent_bridge/runtime.json", "PROHIBITED_PATH"),
            ("CASE_BRAIN/index.json", "PROHIBITED_PATH"),
            (".env.production", "PROHIBITED_FILENAME"),
            ("fixtures/.git-credentials", "PROHIBITED_FILENAME"),
            ("fixtures/auth.json", "PROHIBITED_FILENAME"),
            ("fixtures/id_ed25519", "PROHIBITED_FILENAME"),
            ("fixtures/customer-secrets.txt", "PROHIBITED_FILENAME"),
            ("fixtures/service_account.json", "PROHIBITED_FILENAME"),
            ("fixtures/private.db", "PROHIBITED_FILE_TYPE"),
            ("fixtures/private.rdb", "PROHIBITED_FILE_TYPE"),
            ("fixtures/evidence.zip", "PROHIBITED_FILE_TYPE"),
            ("bad\nname.txt", "PATH_CONTROL_CHARACTER"),
        )
        for path, code in cases:
            with self.subTest(path=path):
                self.assert_path_rejected(path, code)

    def test_private_network_address_fails(self) -> None:
        self.assert_text_rejected(
            "192" + ".168.22.15",
            "PRIVATE_NETWORK_ADDRESS",
        )

    def test_binary_and_oversized_content_fail(self) -> None:
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_bytes(b"safe\x00binary")
        self.assertEqual(str(caught.exception), "BINARY_FILE")
        with self.assertRaises(VALIDATOR.SafetyError) as caught:
            VALIDATOR.validate_bytes(b"a" * (VALIDATOR.MAX_FILE_BYTES + 1))
        self.assertEqual(str(caught.exception), "FILE_TOO_LARGE")

    def test_valid_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.create_repository(
                Path(temporary),
                {"README.md": "Public synthetic documentation.\n"},
            )
            self.assertEqual(VALIDATOR.validate_repository(repository), 1)

    def test_tracked_symlink_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = self.create_repository(
                root,
                {"target.txt": "Public synthetic documentation.\n"},
            )
            link = repository / "link.txt"
            link.symlink_to("target.txt")
            subprocess.run(
                ["git", "-C", str(repository), "add", "link.txt"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self.assertRaises(VALIDATOR.SafetyError) as caught:
                VALIDATOR.validate_repository(repository)
            self.assertEqual(str(caught.exception), "UNSAFE_GIT_MODE")

    def test_parent_symlink_fails_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = self.create_repository(
                root,
                {"docs/public.txt": "Public synthetic documentation.\n"},
            )
            outside = root / "outside"
            outside.mkdir()
            (outside / "public.txt").write_text("outside\n", encoding="utf-8")
            original = repository / "docs"
            original.rename(repository / "docs-original")
            original.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(VALIDATOR.SafetyError) as caught:
                VALIDATOR.validate_repository(repository)
            self.assertEqual(str(caught.exception), "PARENT_UNAVAILABLE")

    def test_same_inode_mutation_during_read_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.create_repository(
                Path(temporary),
                {"public.txt": "public-one\n"},
            )
            original_read = os.read
            changed = False

            def mutate_then_read(descriptor: int, size: int) -> bytes:
                nonlocal changed
                if not changed and os.path.isfile(f"/dev/fd/{descriptor}"):
                    changed = True
                    (repository / "public.txt").write_text(
                        "public-two\n",
                        encoding="utf-8",
                    )
                return original_read(descriptor, size)

            with mock.patch.object(VALIDATOR.os, "read", side_effect=mutate_then_read):
                with self.assertRaises(VALIDATOR.SafetyError) as caught:
                    VALIDATOR.validate_repository(repository)
            self.assertEqual(str(caught.exception), "TRACKED_FILE_CHANGED")

    def test_tracked_file_count_bound_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.create_repository(
                Path(temporary),
                {"one.txt": "one\n", "two.txt": "two\n"},
            )
            with mock.patch.object(VALIDATOR, "MAX_TRACKED_FILES", 1):
                with self.assertRaises(VALIDATOR.SafetyError) as caught:
                    VALIDATOR.validate_repository(repository)
            self.assertEqual(str(caught.exception), "TRACKED_FILE_COUNT_EXCEEDED")

    def test_aggregate_byte_bound_fails_before_reading_excess(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.create_repository(
                Path(temporary),
                {"one.txt": "1234", "two.txt": "5678"},
            )
            with mock.patch.object(VALIDATOR, "MAX_TOTAL_BYTES", 6):
                with self.assertRaises(VALIDATOR.SafetyError) as caught:
                    VALIDATOR.validate_repository(repository)
            self.assertEqual(str(caught.exception), "TOTAL_BYTES_EXCEEDED")

    def test_git_output_bound_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.create_repository(
                Path(temporary),
                {"public.txt": "Public synthetic documentation.\n"},
            )
            descriptor = VALIDATOR.open_repository(repository)
            try:
                with mock.patch.object(VALIDATOR, "MAX_GIT_OUTPUT_BYTES", 8):
                    with self.assertRaises(VALIDATOR.SafetyError) as caught:
                        VALIDATOR.tracked_entries(descriptor)
            finally:
                os.close(descriptor)
            self.assertEqual(str(caught.exception), "GIT_INDEX_TOO_LARGE")

    def test_control_files_must_match_trusted_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trusted = self.create_control_tree(root / "trusted-root", "stable")
            candidate = self.create_control_tree(root / "candidate-root", "stable")
            VALIDATOR.validate_control_files(candidate, trusted)
            changed = candidate / VALIDATOR.PROTECTED_CONTROL_PATHS[-1]
            changed.write_text("weakened\n", encoding="utf-8")
            with self.assertRaises(VALIDATOR.SafetyError) as caught:
                VALIDATOR.validate_control_files(candidate, trusted)
            self.assertEqual(str(caught.exception), "CONTROL_FILE_CHANGED")

    def test_added_workflow_cannot_spoof_required_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trusted = self.create_control_tree(root / "trusted-root", "stable")
            candidate = self.create_control_tree(root / "candidate-root", "stable")
            injected = candidate / ".github/workflows/spoof.yml"
            injected.write_text(
                "name: factory-contracts\njobs:\n  validate:\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "-C", str(candidate), "add", "."],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self.assertRaises(VALIDATOR.SafetyError) as caught:
                VALIDATOR.validate_control_files(candidate, trusted)
            self.assertEqual(str(caught.exception), "WORKFLOW_SET_CHANGED")

    def test_repository_symlink_fails_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = self.create_repository(
                root,
                {"public.txt": "Public synthetic documentation.\n"},
            )
            link = root / "repo-link"
            link.symlink_to(repository, target_is_directory=True)
            with self.assertRaises(VALIDATOR.SafetyError) as caught:
                VALIDATOR.validate_repository(link)
            self.assertEqual(str(caught.exception), "REPOSITORY_UNAVAILABLE")

    def test_repository_replacement_does_not_redirect_open_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = self.create_repository(
                root,
                {"public.txt": "original-public\n"},
            )
            descriptor = VALIDATOR.open_repository(repository)
            moved = root / "original-repo"
            repository.rename(moved)
            replacement = self.create_repository(
                root,
                {"malicious.txt": "replacement\n"},
            )
            self.assertEqual(replacement, repository)
            try:
                entries = VALIDATOR.tracked_entries(descriptor)
                self.assertEqual(entries[0][1], "public.txt")
                payload = VALIDATOR.read_regular_file(
                    descriptor,
                    VALIDATOR.validate_relative_path("public.txt"),
                    VALIDATOR.MAX_TOTAL_BYTES,
                )
                self.assertEqual(payload, b"original-public\n")
            finally:
                os.close(descriptor)

    def test_unexpected_error_is_content_free(self) -> None:
        output = io.StringIO()
        with (
            mock.patch.object(
                VALIDATOR,
                "validate_repository",
                side_effect=OSError("private path detail"),
            ),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(VALIDATOR.main([]), 1)
        self.assertEqual(
            output.getvalue(),
            "PUBLIC_REPOSITORY_SAFETY=FAIL:INTERNAL_ERROR\n",
        )

    def test_invalid_arguments_are_content_free(self) -> None:
        output = io.StringIO()
        error = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            self.assertEqual(
                VALIDATOR.main(["--unknown", "/" + "Users" + "/private"]),
                1,
            )
        self.assertEqual(
            output.getvalue(),
            "PUBLIC_REPOSITORY_SAFETY=FAIL:INVALID_ARGUMENTS\n",
        )
        self.assertEqual(error.getvalue(), "")

    def test_workflow_uses_base_control_plane(self) -> None:
        workflow = (ROOT / ".github/workflows/factory-contracts.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("`required_workflows` rule", workflow)
        self.assertIn("--trusted-root trusted", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("repository: BeyondZeroLabs/apple-silicon-ai-lab", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("candidate-tests:", workflow)
        self.assertNotIn("run: python3 -I candidate/", workflow)


if __name__ == "__main__":
    unittest.main()
