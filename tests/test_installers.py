import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InstallerRepositoryTests(unittest.TestCase):
    def test_expected_entrypoints_exist(self):
        expected = [
            "install.ps1",
            "install.cmd",
            "install.sh",
            "install.command",
            "config/srd-2024.json",
        ]
        missing = [name for name in expected if not (ROOT / name).is_file()]
        self.assertEqual([], missing, f"Missing installer files: {missing}")

    def test_srd_config_selects_only_2024_open_rules(self):
        config = json.loads((ROOT / "config/srd-2024.json").read_text(encoding="utf-8"))
        self.assertEqual(
            ["srd52", "basicRules2024"],
            config["sources"]["reference"],
        )
        self.assertFalse(config["images"]["copyInternal"])
        self.assertFalse(config["images"]["copyExternal"])

    def test_windows_installer_uses_release_checksums_and_user_path(self):
        text = (ROOT / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("https://api.github.com/repos/$Repository/releases", text)
        self.assertIn("Get-FileHash", text)
        self.assertIn('"$archiveName.sha256"', text)
        self.assertIn("SetEnvironmentVariable", text)
        self.assertIn("srd-2024.json", text)

    def test_unix_installer_uses_release_checksums_and_user_path(self):
        text = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("https://github.com/$CLI_REPOSITORY/releases", text)
        self.assertIn("sha256sum", text)
        self.assertIn("shasum -a 256", text)
        self.assertIn("$HOME/.local/bin", text)
        self.assertIn("srd-2024.json", text)

    @unittest.skipUnless(os.name == "nt", "Windows installer dry run runs on Windows")
    def test_windows_dry_run_reports_plan(self):
        shell = shutil.which("pwsh") or shutil.which("powershell.exe")
        if not shell:
            self.skipTest("PowerShell is unavailable")
        result = subprocess.run(
            [
                shell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "install.ps1"),
                "-DryRun",
                "-SetupSrd",
            ],
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY_RUN=true", result.stdout)
        self.assertIn("ASSET=windows-x86_64", result.stdout)
        self.assertIn("SETUP_SRD=true", result.stdout)

    @unittest.skipIf(os.name == "nt", "Unix installer test runs on macOS/Linux")
    def test_unix_dry_run_reports_platform_plan(self):
        result = subprocess.run(
            ["bash", str(ROOT / "install.sh"), "--dry-run", "--with-srd"],
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY_RUN=true", result.stdout)
        self.assertIn("SETUP_SRD=true", result.stdout)
        if sys.platform == "darwin":
            self.assertIn("ASSET=osx-", result.stdout)
        elif sys.platform.startswith("linux"):
            self.assertIn("ASSET=linux-x86_64", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
