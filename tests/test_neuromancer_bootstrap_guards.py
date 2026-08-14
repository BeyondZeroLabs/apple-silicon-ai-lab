from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "examples" / "neuromancer-bootstrap"


def write_identity(path: Path, **values: str) -> Path:
    lines = [f"{key}={value}\n" for key, value in values.items()]
    path.write_text("".join(lines), encoding="utf-8")
    return path


class NeuromancerBootstrapGuardTests(unittest.TestCase):
    def run_guard(self, identity: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if identity is not None:
            env["NEUROMANCER_IDENTITY_FILE"] = str(identity)
        return subprocess.run(
            [
                "bash",
                "-c",
                "source ./lib/host-guard.sh && neuromancer_host_guard",
            ],
            cwd=BOOTSTRAP,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_live_environment_is_rejected_without_fixture(self) -> None:
        result = self.run_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HOST_GUARD=FAIL", result.stdout)

    def test_matching_identity_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            identity = write_identity(
                Path(raw) / "identity.sh",
                NM_HOSTNAME="neuromancer",
                NM_PRODUCT="MacBookPro16,1",
                NM_ARCH="x86_64",
                NM_VIRT="none",
                NM_OS_ID="ubuntu",
                NM_OS_VERSION="26.04",
            )
            result = self.run_guard(identity)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), "HOST_GUARD=PASS")

    def test_hypervisor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            identity = write_identity(
                Path(raw) / "identity.sh",
                NM_HOSTNAME="neuromancer",
                NM_PRODUCT="MacBookPro16,1",
                NM_ARCH="x86_64",
                NM_VIRT="kvm",
                NM_OS_ID="ubuntu",
                NM_OS_VERSION="26.04",
            )
            result = self.run_guard(identity)
            self.assertEqual(result.returncode, 1)
            self.assertIn("HOST_GUARD=FAIL:HYPERVISOR:kvm", result.stdout)

    def test_mutating_scripts_refuse_without_host_match(self) -> None:
        for script in ("install-core.sh", "install-ai-tools.sh"):
            result = subprocess.run(
                ["bash", str(BOOTSTRAP / script)],
                cwd=BOOTSTRAP,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("REFUSE:", result.stderr)

    def test_inventory_writes_under_overridden_local_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            local_root = Path(raw) / "local"
            env = os.environ.copy()
            env["NEUROMANCER_LOCAL_ROOT"] = str(local_root)
            result = subprocess.run(
                ["bash", str(BOOTSTRAP / "inventory.sh")],
                cwd=BOOTSTRAP,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            baseline = local_root / "evidence" / "BASELINE.md"
            self.assertTrue(baseline.is_file())
            text = baseline.read_text(encoding="utf-8")
            self.assertIn("HOST_GUARD=FAIL", text)
            self.assertIn("This inventory is read-only.", text)

    def test_scripts_are_executable(self) -> None:
        for name in (
            "inventory.sh",
            "network-health.sh",
            "install-core.sh",
            "install-ai-tools.sh",
            "verify.sh",
        ):
            mode = (BOOTSTRAP / name).stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
