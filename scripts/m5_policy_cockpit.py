#!/usr/bin/env python3
"""Offline policy gate for the M5 Software Factory cockpit.

The program evaluates public-safe human decision envelopes and optionally
creates append-only, sanitized receipts inside the repository's ignored
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

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{7,79}$")
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{2,159}$")
SENSITIVE_PATTERNS = (
    re.compile("/" + "Users" + "/", re.IGNORECASE),
    re.compile("file:" + "//", re.IGNORECASE),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:sk-|gh[pousr]_)[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


class CockpitError(ValueError):
    """A fail-closed policy or integrity error."""


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
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CockpitError("invalid JSON") from exc
    if not isinstance(value, dict):
        raise CockpitError("JSON root must be an object")
    return value, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    policy, _ = _read_public_json(path)
    if policy.get("schema_version") != "1.0":
        raise CockpitError("unsupported policy schema")
    if policy.get("mode") != "interactive_only":
        raise CockpitError("policy must remain interactive-only")
    if policy.get("status") != "ACTIVE_INTERACTIVE_PILOT":
        raise CockpitError("policy is not active for the bounded pilot")
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

    root = _receipt_root(policy)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
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
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(destination, flags, 0o600)
    except FileExistsError as exc:
        raise CockpitError("append-only receipt already exists") from exc
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return destination, hashlib.sha256(payload).hexdigest()


def verify_receipts(policy: dict[str, Any]) -> dict[str, Any]:
    root = _receipt_root(policy)
    if not root.exists():
        return {"receipt_count": 0, "status": "PASS"}
    if root.is_symlink() or not root.is_dir():
        raise CockpitError("receipt root integrity failure")
    count = 0
    for path in sorted(root.iterdir()):
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            raise CockpitError("unexpected receipt entry")
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise CockpitError("receipt permissions are too broad")
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("receipt_type") != "m5_policy_cockpit_decision":
            raise CockpitError("unexpected receipt type")
        if value.get("policy_revision") != policy.get("policy_revision"):
            raise CockpitError("receipt policy revision mismatch")
        if value.get("executes_action") is not False:
            raise CockpitError("receipt claims execution authority")
        count += 1
    return {"receipt_count": count, "status": "PASS"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
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
        policy = load_policy(args.policy)
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
    except (CockpitError, OSError, json.JSONDecodeError) as exc:
        print(f"M5_POLICY_COCKPIT_FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
