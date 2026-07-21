#!/usr/bin/env python3
"""Offline policy gate for the M5 Software Factory cockpit.

The program evaluates public-safe human decision envelopes and optionally
creates non-overwriting, sanitized receipts inside the repository's ignored
`.factory-state` directory. It deliberately has no network, model, service,
credential, GitHub, or external-storage integration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = REPO_ROOT / "config/software-factory/m5-policy-cockpit.json"

POLICY_KEYS = {
    "schema_version",
    "id",
    "status",
    "policy_revision",
    "machine_role",
    "mode",
    "allowed_repositories",
    "allowed_data_classifications",
    "allowed_actions",
    "required_evidence",
    "prohibited_capabilities",
    "receipt_root",
    "receipt_mode",
}

REQUEST_KEYS = {
    "schema_version",
    "request_id",
    "action",
    "repository",
    "data_classification",
    "risk_class",
    "human_owner_role",
    "human_confirmation",
    "candidate_ref",
    "rollback_ref",
    "evidence",
}

RECEIPT_KEYS = {
    "schema_version",
    "receipt_type",
    "request_id",
    "request_sha256",
    "recorded_at",
    "machine_role",
    "policy_revision",
    "action",
    "repository",
    "data_classification",
    "risk_class",
    "candidate_ref",
    "rollback_ref",
    "decision",
    "executes_action",
}

EXPECTED_POLICY = {
    "schema_version": "1.0",
    "id": "bz-m5-policy-cockpit-public-pilot",
    "status": "ACTIVE_INTERACTIVE_PILOT",
    "policy_revision": "094f5a852c90be00c19e5915ae0fd8b45a22826c",
    "machine_role": "mbp_m5_max_policy_cockpit",
    "mode": "interactive_only",
    "allowed_repositories": ["BeyondZeroLabs/apple-silicon-ai-lab"],
    "allowed_data_classifications": ["PUBLIC"],
    "allowed_actions": [
        "approve_goal",
        "record_independent_review",
        "authorize_merge",
        "authorize_rollback",
    ],
    "required_evidence": [
        "contracts_accepted",
        "deterministic_tests_passed",
        "privacy_scan_passed",
        "independent_review_passed",
        "rollback_documented",
        "scope_is_public_safe",
    ],
    "prohibited_capabilities": [
        "automatic_merge",
        "coordinator_lease",
        "fleet_service_install",
        "model_download",
        "model_or_policy_promotion",
        "network_service_bind",
        "protected_storage_access",
        "external_drive_write",
        "credential_export",
    ],
    "receipt_root": ".factory-state/m5-policy-cockpit/receipts",
    "receipt_mode": "create_exclusive_non_authoritative",
}

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{7,79}$")
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{2,159}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
SENSITIVE_PATTERNS = (
    re.compile("/" + "Users" + "/", re.IGNORECASE),
    re.compile("file:" + "//", re.IGNORECASE),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:sk-|gh[pousr]_)[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


class CockpitError(ValueError):
    """A fail-closed policy or integrity error."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CockpitError("duplicate JSON field")
        value[key] = item
    return value


def _strict_json_loads(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise CockpitError("invalid JSON") from exc
    if not isinstance(value, dict):
        raise CockpitError("JSON root must be an object")
    return value


def _inside_repo(path: Path) -> Path:
    """Return a resolved repository-local regular file and reject symlinks."""
    if path.is_symlink():
        raise CockpitError("symlink input is not allowed")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise CockpitError("input must remain inside the repository") from exc
    if not resolved.is_file():
        raise CockpitError("input must be a regular file")
    return resolved


def _read_public_json(path: Path) -> tuple[dict[str, Any], str]:
    resolved = _inside_repo(path)
    raw = resolved.read_text(encoding="utf-8")
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(raw):
            raise CockpitError("request contains content prohibited in the public lane")
    value = _strict_json_loads(raw)
    return value, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    policy, _ = _read_public_json(path)
    if set(policy) != POLICY_KEYS:
        raise CockpitError("policy fields do not match the pinned schema")
    for key, expected in EXPECTED_POLICY.items():
        if policy.get(key) != expected:
            raise CockpitError("policy does not match the pinned public pilot")
    return policy


def evaluate(request: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    unknown = set(request) - REQUEST_KEYS
    missing = REQUEST_KEYS - set(request)
    reasons: list[str] = []

    if unknown:
        reasons.append("unknown request fields")
    if missing:
        reasons.append("missing required request fields")
    if request.get("schema_version") != "1.0":
        reasons.append("unsupported request schema")
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not SAFE_ID.fullmatch(request_id):
        reasons.append("invalid request identifier")
    if request.get("action") not in policy.get("allowed_actions", []):
        reasons.append("action is outside the bounded cockpit")
    if request.get("repository") not in policy.get("allowed_repositories", []):
        reasons.append("repository is not allowlisted")
    if request.get("data_classification") not in policy.get(
        "allowed_data_classifications", []
    ):
        reasons.append("data classification is not allowed")
    if request.get("risk_class") not in {"LOW", "MEDIUM", "HIGH"}:
        reasons.append("invalid risk class")
    if request.get("human_owner_role") != "m5_policy_owner":
        reasons.append("human owner role is not the M5 policy owner")
    if request.get("human_confirmation") is not True:
        reasons.append("explicit human confirmation is required")

    for field in ("candidate_ref", "rollback_ref"):
        value = request.get(field)
        if not isinstance(value, str) or not SAFE_REF.fullmatch(value):
            reasons.append(f"invalid {field}")

    evidence = request.get("evidence")
    required_evidence = set(policy.get("required_evidence", []))
    if not isinstance(evidence, dict):
        reasons.append("evidence must be an object")
    else:
        if set(evidence) != required_evidence:
            reasons.append("evidence fields do not match the policy")
        if any(evidence.get(name) is not True for name in required_evidence):
            reasons.append("all required evidence must pass")

    return {
        "schema_version": "1.0",
        "policy_id": policy.get("id"),
        "policy_revision": policy.get("policy_revision"),
        "request_id": request_id if isinstance(request_id, str) else "invalid-request",
        "decision": "APPROVED_FOR_HUMAN_ACTION" if not reasons else "DENIED",
        "reason_codes": sorted(set(reasons)),
        "executes_action": False,
        "network_used": False,
        "protected_storage_accessed": False,
    }


def _receipt_root(policy: dict[str, Any]) -> Path:
    relative = Path(str(policy.get("receipt_root", "")))
    if relative.is_absolute() or ".." in relative.parts:
        raise CockpitError("receipt root must be a repository-relative path")
    state_root = REPO_ROOT / ".factory-state"
    if state_root.is_symlink():
        raise CockpitError(".factory-state must not be a symlink")
    root = (REPO_ROOT / relative).resolve()
    try:
        root.relative_to(state_root)
    except ValueError as exc:
        raise CockpitError("receipts must remain under .factory-state") from exc
    return root


def _receipt_parts(policy: dict[str, Any]) -> tuple[str, ...]:
    relative = Path(str(policy.get("receipt_root", "")))
    if (
        relative.is_absolute()
        or not relative.parts
        or relative.parts[0] != ".factory-state"
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise CockpitError("receipt root must remain under .factory-state")
    return relative.parts


def _secure_directory_fd(policy: dict[str, Any], *, create: bool) -> int | None:
    """Open the receipt directory without following path-component symlinks."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    current = os.open(REPO_ROOT, flags)
    try:
        for part in _receipt_parts(policy):
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=current)
                except FileExistsError:
                    pass
            try:
                child = os.open(part, flags, dir_fd=current)
            except FileNotFoundError:
                if create:
                    raise
                os.close(current)
                return None
            info = os.fstat(child)
            if (
                not stat.S_ISDIR(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077
            ):
                os.close(child)
                raise CockpitError("receipt directory ownership or permissions are unsafe")
            os.close(current)
            current = child
        return current
    except Exception:
        try:
            os.close(current)
        except OSError:
            pass
        raise


def _read_receipt_at(directory_fd: int, filename: str) -> dict[str, Any]:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open(filename, flags, dir_fd=directory_fd)
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_nlink != 1
            or stat.S_IMODE(info.st_mode) & 0o077
        ):
            raise CockpitError("receipt ownership, type, links, or permissions are unsafe")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = handle.read(65537)
        if len(payload) > 65536:
            raise CockpitError("receipt exceeds the size limit")
        raw = payload.decode("utf-8")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(raw):
                raise CockpitError("receipt contains prohibited content")
        return _strict_json_loads(raw)
    finally:
        os.close(descriptor)


def _validate_receipt(
    value: dict[str, Any], filename: str, policy: dict[str, Any]
) -> None:
    if set(value) != RECEIPT_KEYS:
        raise CockpitError("receipt fields do not match the pinned schema")
    request_id = value.get("request_id")
    checks = (
        value.get("schema_version") == "1.0",
        value.get("receipt_type") == "m5_policy_cockpit_decision",
        isinstance(request_id, str) and SAFE_ID.fullmatch(request_id) is not None,
        filename == f"{request_id}.json",
        isinstance(value.get("request_sha256"), str)
        and SHA256.fullmatch(value["request_sha256"]) is not None,
        value.get("machine_role") == policy.get("machine_role"),
        value.get("policy_revision") == policy.get("policy_revision"),
        value.get("action") in policy.get("allowed_actions", []),
        value.get("repository") in policy.get("allowed_repositories", []),
        value.get("data_classification")
        in policy.get("allowed_data_classifications", []),
        value.get("risk_class") in {"LOW", "MEDIUM", "HIGH"},
        isinstance(value.get("candidate_ref"), str)
        and SAFE_REF.fullmatch(value["candidate_ref"]) is not None,
        isinstance(value.get("rollback_ref"), str)
        and SAFE_REF.fullmatch(value["rollback_ref"]) is not None,
        value.get("decision") == "APPROVED_FOR_HUMAN_ACTION",
        value.get("executes_action") is False,
    )
    if not all(checks):
        raise CockpitError("receipt does not match the pinned security contract")
    recorded_at = value.get("recorded_at")
    if not isinstance(recorded_at, str) or not recorded_at.endswith("Z"):
        raise CockpitError("receipt timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CockpitError("receipt timestamp is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise CockpitError("receipt timestamp is invalid")


def record_receipt(
    request: dict[str, Any],
    request_sha256: str,
    decision: dict[str, Any],
    policy: dict[str, Any],
    *,
    human_confirmed: bool,
) -> tuple[Path, str]:
    if not human_confirmed:
        raise CockpitError("live human confirmation flag is required to record")
    if decision["decision"] != "APPROVED_FOR_HUMAN_ACTION":
        raise CockpitError("denied requests cannot be recorded as approvals")
    if not SHA256.fullmatch(request_sha256):
        raise CockpitError("request digest is invalid")

    root = _receipt_root(policy)
    request_id = decision["request_id"]
    destination = root / f"{request_id}.json"
    receipt = {
        "schema_version": "1.0",
        "receipt_type": "m5_policy_cockpit_decision",
        "request_id": request_id,
        "request_sha256": request_sha256,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "machine_role": policy["machine_role"],
        "policy_revision": policy["policy_revision"],
        "action": request["action"],
        "repository": request["repository"],
        "data_classification": request["data_classification"],
        "risk_class": request["risk_class"],
        "candidate_ref": request["candidate_ref"],
        "rollback_ref": request["rollback_ref"],
        "decision": decision["decision"],
        "executes_action": False,
    }
    payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    directory_fd = _secure_directory_fd(policy, create=True)
    assert directory_fd is not None
    try:
        try:
            descriptor = os.open(
                destination.name, flags, 0o600, dir_fd=directory_fd
            )
        except FileExistsError as exc:
            raise CockpitError("create-exclusive receipt already exists") from exc
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return destination, hashlib.sha256(payload).hexdigest()


def verify_receipts(policy: dict[str, Any]) -> dict[str, Any]:
    _receipt_root(policy)
    directory_fd = _secure_directory_fd(policy, create=False)
    if directory_fd is None:
        return {"receipt_count": 0, "status": "PASS"}
    try:
        count = 0
        for filename in sorted(os.listdir(directory_fd)):
            if not filename.endswith(".json") or "/" in filename:
                raise CockpitError("unexpected receipt entry")
            value = _read_receipt_at(directory_fd, filename)
            _validate_receipt(value, filename, policy)
            count += 1
        return {"receipt_count": count, "status": "PASS"}
    finally:
        os.close(directory_fd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("request", type=Path)
    record = commands.add_parser("record")
    record.add_argument("request", type=Path)
    record.add_argument(
        "--human-confirm",
        action="store_true",
        help="record that a human is deliberately authorizing this receipt",
    )
    commands.add_parser("verify-receipts")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = load_policy()
        if args.command == "verify-receipts":
            print(json.dumps(verify_receipts(policy), sort_keys=True))
            return 0

        request, request_sha256 = _read_public_json(args.request)
        decision = evaluate(request, policy)
        if args.command == "check":
            print(json.dumps(decision, indent=2, sort_keys=True))
            return 0 if decision["decision"] == "APPROVED_FOR_HUMAN_ACTION" else 2

        destination, receipt_sha256 = record_receipt(
            request,
            request_sha256,
            decision,
            policy,
            human_confirmed=args.human_confirm,
        )
        print(
            json.dumps(
                {
                    "decision": decision["decision"],
                    "receipt_path": str(destination.relative_to(REPO_ROOT)),
                    "receipt_sha256": receipt_sha256,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except CockpitError as exc:
        print(f"M5_POLICY_COCKPIT_FAIL: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print(
            "M5_POLICY_COCKPIT_FAIL: filesystem or encoding operation failed",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
