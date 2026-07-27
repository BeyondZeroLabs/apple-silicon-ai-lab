#!/usr/bin/env python3
"""Fail-closed, content-free safety checks for tracked public-repository files."""

from __future__ import annotations

import argparse
import os
import re
import selectors
import stat
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath


class SafetyError(RuntimeError):
    pass


MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 33_554_432
MAX_TRACKED_FILES = 5_000
MAX_GIT_OUTPUT_BYTES = 2_097_152
GIT_TIMEOUT_SECONDS = 10.0
READ_CHUNK_BYTES = 65_536
ALLOWED_GIT_MODES = {"100644", "100755"}
PROTECTED_CONTROL_PATHS = (
    ".github/workflows/factory-contracts.yml",
    "docs/software-factory/validate_package.sh",
    "scripts/m5_policy_cockpit.py",
    "scripts/validate_m5_policy_cockpit.sh",
    "scripts/validate_public_repository_safety.py",
    "scripts/validate_skill_registry.py",
    "scripts/validate_skill_supply_chain.sh",
    "tests/test_m5_policy_cockpit.py",
    "tests/test_skill_registry.py",
    "tests/test_validate_public_repository_safety.py",
)
PROHIBITED_COMPONENTS = {
    ".aws",
    ".factory-state",
    ".gnupg",
    ".obsidian",
    ".ssh",
    "agent_bridge",
    "case-brain",
    "case_brain",
    "casebrain",
    "outputs",
    "private",
    "receipts",
    "secrets",
}
PROHIBITED_FILENAMES = {
    ".dockerconfigjson",
    ".env",
    ".envrc",
    ".git-credentials",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "application_default_credentials.json",
    "auth.json",
    "authorized_keys",
    "cookies.json",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "login data",
    "oauth.json",
    "service-account.json",
    "service_account.json",
    "token.json",
}
PROHIBITED_FILENAME_TOKENS = re.compile(
    r"(?:^|[._-])(?:credential|credentials|private[_-]?key|"
    r"secret|secrets|token|tokens)(?:[._-]|$)",
    re.IGNORECASE,
)
PROHIBITED_SUFFIXES = {
    ".7z",
    ".accdb",
    ".bak",
    ".backup",
    ".db",
    ".db3",
    ".dmg",
    ".dump",
    ".gz",
    ".kdbx",
    ".key",
    ".keychain-db",
    ".mdb",
    ".mobileprovision",
    ".ovpn",
    ".p12",
    ".pem",
    ".pfx",
    ".pkg",
    ".ppk",
    ".rar",
    ".realm",
    ".rdb",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".zip",
}
CONTENT_PATTERNS = (
    (
        "CREDENTIAL_SHAPE",
        re.compile(
            r"(?i)(?:"
            r"github_pat_[A-Za-z0-9_]{20,}|"
            r"gh[pousr]_[A-Za-z0-9]{20,}|"
            r"glpat-[A-Za-z0-9_-]{20,}|"
            r"npm_[A-Za-z0-9]{20,}|"
            r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}|"
            r"xox[baprs]-[A-Za-z0-9-]{20,}|"
            r"AIza[0-9A-Za-z_-]{35}|"
            r"(?:AKIA|ASIA)[0-9A-Z]{16}|"
            r"eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}"
            r")"
        ),
    ),
    (
        "SECRET_ASSIGNMENT",
        re.compile(
            r"(?i)(?:authorization|api[_ -]?key|access[_ -]?token|"
            r"client[_ -]?secret|password|private[_ -]?token)"
            r"\s*[:=]\s*[\"']?(?!\$\{|<|\{\{)[A-Za-z0-9/+_.=-]{12,}"
        ),
    ),
    (
        "PRIVATE_KEY_MATERIAL",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "PRIVATE_HOME_PATH",
        re.compile(
            r"(?i)(?:/Users/|/home/|[A-Z]:\\\\Users\\\\)[A-Za-z0-9._-]+"
        ),
    ),
    (
        "PRIVATE_CHAT_LINK",
        re.compile(
            r"https://(?:chatgpt\.com/(?:c|share|g/[^/]+/c)/|"
            r"claude\.ai/(?:chat|share|epitaxy)/)[A-Za-z0-9_/?=&.-]+",
            re.IGNORECASE,
        ),
    ),
    (
        "PERSONAL_IDENTIFIER_SHAPE",
        re.compile(
            r"(?i)(?:"
            r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)|"
            r"(?<![A-Z0-9._%+/:~-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|"
            r"(?<!\d)(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?"
            r"[-.\s]\d{3}[-.\s]\d{4}(?!\d)|"
            r"(?<![0-9A-F])(?:[0-9A-F]{2}:){5}[0-9A-F]{2}(?![0-9A-F])|"
            r"(?<![0-9A-F])[0-9A-F]{8}-[0-9A-F]{4}-[1-5][0-9A-F]{3}-"
            r"[89AB][0-9A-F]{3}-[0-9A-F]{12}(?![0-9A-F])"
            r")"
        ),
    ),
    (
        "PRIVATE_NETWORK_ADDRESS",
        re.compile(
            r"(?<!\d)(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
            r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?!\d)|"
            r"(?i:(?<![0-9a-f:])(?:f[cd][0-9a-f]{0,2}|"
            r"fe[89ab][0-9a-f]):[0-9a-f:]+(?![0-9a-f:]))"
        ),
    ),
)


class ContentFreeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise SafetyError("INVALID_ARGUMENTS")


def fail(condition: bool, code: str) -> None:
    if not condition:
        raise SafetyError(code)


def validate_relative_path(raw_path: str) -> PurePosixPath:
    fail(bool(raw_path), "EMPTY_PATH")
    fail(
        all(ord(character) >= 32 and ord(character) != 127 for character in raw_path),
        "PATH_CONTROL_CHARACTER",
    )
    path = PurePosixPath(raw_path)
    fail(not path.is_absolute(), "ABSOLUTE_PATH")
    fail(".." not in path.parts, "PATH_TRAVERSAL")
    lowered_parts = tuple(part.casefold() for part in path.parts)
    fail(
        not set(lowered_parts).intersection(PROHIBITED_COMPONENTS),
        "PROHIBITED_PATH",
    )
    filename = lowered_parts[-1]
    fail(
        filename not in PROHIBITED_FILENAMES
        and not filename.startswith(".env.")
        and PROHIBITED_FILENAME_TOKENS.search(filename) is None,
        "PROHIBITED_FILENAME",
    )
    fail(path.suffix.casefold() not in PROHIBITED_SUFFIXES, "PROHIBITED_FILE_TYPE")
    return path


def validate_text(text: str) -> None:
    for code, pattern in CONTENT_PATTERNS:
        fail(pattern.search(text) is None, code)


def validate_bytes(payload: bytes) -> None:
    fail(len(payload) <= MAX_FILE_BYTES, "FILE_TOO_LARGE")
    fail(b"\x00" not in payload, "BINARY_FILE")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SafetyError("NON_UTF8_FILE") from exc
    validate_text(text)


def bounded_git_index(repository_descriptor: int) -> bytes:
    try:
        git_descriptor = os.open(
            ".git",
            directory_open_flags(),
            dir_fd=repository_descriptor,
        )
    except OSError as exc:
        raise SafetyError("GIT_DIRECTORY_UNAVAILABLE") from exc
    os.close(git_descriptor)
    try:
        process = subprocess.Popen(
            ["git", "ls-files", "-s", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            pass_fds=(repository_descriptor,),
            preexec_fn=lambda: os.fchdir(repository_descriptor),
        )
    except OSError as exc:
        raise SafetyError("GIT_INDEX_UNAVAILABLE") from exc
    fail(process.stdout is not None, "GIT_INDEX_UNAVAILABLE")
    selector = selectors.DefaultSelector()
    chunks: list[bytes] = []
    total = 0
    deadline = time.monotonic() + GIT_TIMEOUT_SECONDS
    try:
        selector.register(process.stdout, selectors.EVENT_READ)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SafetyError("GIT_INDEX_TIMEOUT")
            events = selector.select(remaining)
            if not events:
                raise SafetyError("GIT_INDEX_TIMEOUT")
            chunk = os.read(process.stdout.fileno(), READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            fail(total <= MAX_GIT_OUTPUT_BYTES, "GIT_INDEX_TOO_LARGE")
            chunks.append(chunk)
        try:
            returncode = process.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise SafetyError("GIT_INDEX_TIMEOUT") from exc
        fail(returncode == 0, "GIT_INDEX_ERROR")
        return b"".join(chunks)
    except SafetyError:
        process.kill()
        process.wait()
        raise
    except (OSError, ValueError) as exc:
        process.kill()
        process.wait()
        raise SafetyError("GIT_INDEX_UNAVAILABLE") from exc
    finally:
        selector.close()
        process.stdout.close()


def tracked_entries(repository_descriptor: int) -> list[tuple[str, str]]:
    output = bounded_git_index(repository_descriptor)
    entries: list[tuple[str, str]] = []
    for record in output.split(b"\0"):
        if not record:
            continue
        fail(len(entries) < MAX_TRACKED_FILES, "TRACKED_FILE_COUNT_EXCEEDED")
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, object_id, stage = metadata.decode("ascii").split(" ")
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise SafetyError("GIT_INDEX_FORMAT") from exc
        fail(stage == "0", "GIT_INDEX_STAGE")
        fail(
            len(object_id) in {40, 64}
            and all(character in "0123456789abcdef" for character in object_id),
            "GIT_OBJECT_ID_FORMAT",
        )
        entries.append((mode, path))
    fail(bool(entries), "TRACKED_SET_EMPTY")
    return entries


def directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def file_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def open_repository(repo: Path) -> int:
    fail(repo.is_absolute(), "REPOSITORY_NOT_ABSOLUTE")
    descriptor = -1
    try:
        descriptor = os.open(repo, directory_open_flags())
        info = os.fstat(descriptor)
    except OSError as exc:
        if descriptor >= 0:
            os.close(descriptor)
        raise SafetyError("REPOSITORY_UNAVAILABLE") from exc
    if not stat.S_ISDIR(info.st_mode):
        os.close(descriptor)
        raise SafetyError("REPOSITORY_NOT_DIRECTORY")
    return descriptor


def read_regular_file(
    repository_descriptor: int,
    relative: PurePosixPath,
    remaining_total_bytes: int,
) -> bytes:
    parent_descriptor = os.dup(repository_descriptor)
    file_descriptor = -1
    try:
        for component in relative.parts[:-1]:
            try:
                child_descriptor = os.open(
                    component,
                    directory_open_flags(),
                    dir_fd=parent_descriptor,
                )
            except OSError as exc:
                raise SafetyError("PARENT_UNAVAILABLE") from exc
            os.close(parent_descriptor)
            parent_descriptor = child_descriptor
            fail(
                stat.S_ISDIR(os.fstat(parent_descriptor).st_mode),
                "PARENT_NOT_DIRECTORY",
            )
        try:
            file_descriptor = os.open(
                relative.parts[-1],
                file_open_flags(),
                dir_fd=parent_descriptor,
            )
        except OSError as exc:
            raise SafetyError("TRACKED_FILE_UNAVAILABLE") from exc
        before = os.fstat(file_descriptor)
        fail(stat.S_ISREG(before.st_mode), "TRACKED_NOT_REGULAR")
        fail(before.st_size <= MAX_FILE_BYTES, "FILE_TOO_LARGE")
        fail(before.st_size <= remaining_total_bytes, "TOTAL_BYTES_EXCEEDED")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(file_descriptor, READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            fail(total <= before.st_size, "TRACKED_FILE_CHANGED")
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        fail(
            (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            and total == before.st_size,
            "TRACKED_FILE_CHANGED",
        )
        return b"".join(chunks)
    finally:
        if file_descriptor >= 0:
            os.close(file_descriptor)
        os.close(parent_descriptor)


def validate_repository(repo: Path) -> int:
    repository_descriptor = open_repository(repo)
    total_bytes = 0
    seen: set[str] = set()
    try:
        entries = tracked_entries(repository_descriptor)
        for mode, raw_path in entries:
            fail(mode in ALLOWED_GIT_MODES, "UNSAFE_GIT_MODE")
            fail(raw_path not in seen, "DUPLICATE_TRACKED_PATH")
            seen.add(raw_path)
            relative = validate_relative_path(raw_path)
            payload = read_regular_file(
                repository_descriptor,
                relative,
                MAX_TOTAL_BYTES - total_bytes,
            )
            total_bytes += len(payload)
            validate_bytes(payload)
    finally:
        os.close(repository_descriptor)
    return len(entries)


def validate_control_files(candidate_repo: Path, trusted_root: Path) -> None:
    candidate_descriptor = open_repository(candidate_repo)
    trusted_descriptor = open_repository(trusted_root)
    try:
        candidate_workflows = {
            path
            for _mode, path in tracked_entries(candidate_descriptor)
            if path.startswith(".github/workflows/")
        }
        trusted_workflows = {
            path
            for _mode, path in tracked_entries(trusted_descriptor)
            if path.startswith(".github/workflows/")
        }
        fail(candidate_workflows == trusted_workflows, "WORKFLOW_SET_CHANGED")
        control_paths = set(PROTECTED_CONTROL_PATHS) | trusted_workflows
        for raw_path in sorted(control_paths):
            relative = validate_relative_path(raw_path)
            try:
                candidate_payload = read_regular_file(
                    candidate_descriptor,
                    relative,
                    MAX_FILE_BYTES,
                )
                trusted_payload = read_regular_file(
                    trusted_descriptor,
                    relative,
                    MAX_FILE_BYTES,
                )
            except SafetyError as exc:
                raise SafetyError("CONTROL_FILE_UNAVAILABLE") from exc
            fail(candidate_payload == trusted_payload, "CONTROL_FILE_CHANGED")
    finally:
        os.close(candidate_descriptor)
        os.close(trusted_descriptor)


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = ContentFreeArgumentParser(add_help=False)
    parser.add_argument("--repo", default=os.getcwd())
    parser.add_argument("--trusted-root")
    return parser.parse_args(argv)


def absolute_without_resolution(raw_path: str) -> Path:
    return Path(os.path.abspath(raw_path))


def main(argv: list[str] | None = None) -> int:
    try:
        arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
        repository = absolute_without_resolution(arguments.repo)
        count = validate_repository(repository)
        if arguments.trusted_root:
            validate_control_files(
                repository,
                absolute_without_resolution(arguments.trusted_root),
            )
    except SafetyError as exc:
        print(f"PUBLIC_REPOSITORY_SAFETY=FAIL:{exc}")
        return 1
    except Exception:
        print("PUBLIC_REPOSITORY_SAFETY=FAIL:INTERNAL_ERROR")
        return 1
    print("PUBLIC_REPOSITORY_SAFETY=PASS")
    print(f"TRACKED_FILE_COUNT={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
