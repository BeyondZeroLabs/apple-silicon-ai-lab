#!/usr/bin/env python3
"""Fail-closed, content-free safety checks for tracked public-repository files."""

from __future__ import annotations

import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


class SafetyError(RuntimeError):
    pass


MAX_FILE_BYTES = 1_048_576
ALLOWED_GIT_MODES = {"100644", "100755"}
PROHIBITED_COMPONENTS = {
    ".env",
    ".factory-state",
    ".obsidian",
    "agent_bridge",
    "case_brain",
    "outputs",
    "private",
    "receipts",
    "secrets",
}
PROHIBITED_SUFFIXES = {
    ".7z",
    ".dmg",
    ".gz",
    ".key",
    ".mobileprovision",
    ".p12",
    ".pem",
    ".pfx",
    ".pkg",
    ".rar",
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
            r"sk-[A-Za-z0-9]{20,}|"
            r"xox[baprs]-[A-Za-z0-9-]{20,}|"
            r"AKIA[0-9A-Z]{16}"
            r")"
        ),
    ),
    (
        "PRIVATE_KEY_MATERIAL",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "PRIVATE_HOME_PATH",
        re.compile(r"(?i)(?:/Users/|[A-Z]:\\\\Users\\\\)[A-Za-z0-9._-]+"),
    ),
    (
        "PRIVATE_CHAT_LINK",
        re.compile(
            r"https://(?:chatgpt\.com/(?:c|share)/|"
            r"claude\.ai/(?:chat|share)/)[A-Za-z0-9_-]+",
            re.IGNORECASE,
        ),
    ),
)


def fail(condition: bool, code: str) -> None:
    if not condition:
        raise SafetyError(code)


def validate_relative_path(raw_path: str) -> PurePosixPath:
    fail(bool(raw_path), "EMPTY_PATH")
    path = PurePosixPath(raw_path)
    fail(not path.is_absolute(), "ABSOLUTE_PATH")
    fail(".." not in path.parts, "PATH_TRAVERSAL")
    lowered = {part.casefold() for part in path.parts}
    fail(not lowered.intersection(PROHIBITED_COMPONENTS), "PROHIBITED_PATH")
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


def tracked_entries(repo: Path) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-s", "-z"],
        check=False,
        capture_output=True,
    )
    fail(result.returncode == 0, "GIT_INDEX_UNAVAILABLE")
    fail(result.stderr == b"", "GIT_INDEX_ERROR")
    entries: list[tuple[str, str]] = []
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, _object_id, stage = metadata.decode("ascii").split(" ")
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise SafetyError("GIT_INDEX_FORMAT") from exc
        fail(stage == "0", "GIT_INDEX_STAGE")
        entries.append((mode, path))
    fail(bool(entries), "TRACKED_SET_EMPTY")
    return entries


def validate_parent_chain(repo: Path, relative: PurePosixPath) -> None:
    current = repo
    for component in relative.parts[:-1]:
        current = current / component
        try:
            info = current.lstat()
        except OSError as exc:
            raise SafetyError("PARENT_UNAVAILABLE") from exc
        fail(not stat.S_ISLNK(info.st_mode), "PARENT_SYMLINK")
        fail(stat.S_ISDIR(info.st_mode), "PARENT_NOT_DIRECTORY")


def validate_repository(repo: Path) -> int:
    try:
        repo_info = repo.lstat()
    except OSError as exc:
        raise SafetyError("REPOSITORY_UNAVAILABLE") from exc
    fail(repo.is_absolute(), "REPOSITORY_NOT_ABSOLUTE")
    fail(not stat.S_ISLNK(repo_info.st_mode), "REPOSITORY_SYMLINK")
    fail(stat.S_ISDIR(repo_info.st_mode), "REPOSITORY_NOT_DIRECTORY")

    entries = tracked_entries(repo)
    seen: set[str] = set()
    for mode, raw_path in entries:
        fail(mode in ALLOWED_GIT_MODES, "UNSAFE_GIT_MODE")
        fail(raw_path not in seen, "DUPLICATE_TRACKED_PATH")
        seen.add(raw_path)
        relative = validate_relative_path(raw_path)
        validate_parent_chain(repo, relative)
        candidate = repo.joinpath(*relative.parts)
        try:
            info = candidate.lstat()
            payload = candidate.read_bytes()
            after = candidate.lstat()
        except OSError as exc:
            raise SafetyError("TRACKED_FILE_UNAVAILABLE") from exc
        fail(not stat.S_ISLNK(info.st_mode), "TRACKED_SYMLINK")
        fail(stat.S_ISREG(info.st_mode), "TRACKED_NOT_REGULAR")
        fail(
            (info.st_dev, info.st_ino, info.st_size)
            == (after.st_dev, after.st_ino, after.st_size),
            "TRACKED_FILE_CHANGED",
        )
        validate_bytes(payload)
    return len(entries)


def main() -> int:
    try:
        count = validate_repository(Path(os.getcwd()))
    except SafetyError as exc:
        print(f"PUBLIC_REPOSITORY_SAFETY=FAIL:{exc}")
        return 1
    print("PUBLIC_REPOSITORY_SAFETY=PASS")
    print(f"TRACKED_FILE_COUNT={count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
