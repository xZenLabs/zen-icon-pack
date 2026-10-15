"""Run with python3 -m unittest discover -s scripts -p 'test_*.py'."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "release_version", Path(__file__).with_name("next-release-version.py"))
release_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_version)


class ReleaseVersionTest(unittest.TestCase):
    def test_manual_increase_uses_the_pushed_version_without_an_extra_bump(self):
        for previous, version, tags in (
                ("1.0.0", "1.0.1", ["v1.0.0"]),
                ("1.0.9", "1.0.10", ["v1.0.9"]),
                ("1.9.0", "1.10.0", ["v1.9.99"]),
                ("1.9.99", "2.0.0", ["v1.9.99"])):
            with self.subTest(previous=previous, version=version):
                self.assertEqual(release_version.next_version(version, tags, previous), version)

    def test_unchanged_or_lower_manifest_version_still_bumps_above_release_tags(self):
        for previous, version, expected in (
                ("1.0.0", "1.0.0", "1.0.11"),
                ("1.1.0", "1.0.0", "1.0.11")):
            with self.subTest(previous=previous, version=version):
                self.assertEqual(release_version.next_version(
                    version, ["v1.0.9", "v1.0.10"], previous), expected)

    def test_reads_the_manifest_before_the_whole_push_and_handles_initial_pushes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

            git("init", "-q")
            git("config", "user.name", "Release test")
            git("config", "user.email", "release-test@example.invalid")
            git("config", "commit.gpgsign", "false")
            (root / "README.md").write_text("Initial repository\n")
            git("add", "README.md")
            git("commit", "-qm", "Initial repository")
            initial = git("rev-parse", "HEAD")
            legacy = root / "zen-icon-pack" / "pack.json"
            legacy.parent.mkdir()
            legacy.write_text(json.dumps({"version": "0.9.0"}))
            git("add", "zen-icon-pack/pack.json")
            git("commit", "-qm", "Legacy nested manifest")
            legacy_revision = git("rev-parse", "HEAD")
            manifest = root / "pack.json"
            for version in ("1.0.0", "1.1.0", "1.1.0"):
                manifest.write_text(json.dumps({"version": version}))
                git("add", "pack.json")
                git("commit", "--allow-empty", "-qm", version)
                if version == "1.0.0": before_push = git("rev-parse", "HEAD")
            self.assertEqual(release_version.version_before_push(root, before_push), "1.0.0")
            self.assertEqual(release_version.version_before_push(root, "HEAD~1"), "1.1.0")
            self.assertEqual(release_version.version_before_push(root, legacy_revision), "0.9.0")
            self.assertIsNone(release_version.version_before_push(root, initial))
            self.assertIsNone(release_version.version_before_push(root, "0" * 40))
            self.assertIsNone(release_version.version_before_push(root, ""))
            script = root / "scripts" / "next-release-version.py"
            script.parent.mkdir()
            shutil.copyfile(Path(__file__).with_name(script.name), script)
            for revision, expected in ((before_push, "1.1.0"), ("", "1.1.1")):
                output = subprocess.check_output([sys.executable, str(script)], cwd=root,
                    env=dict(os.environ, PREVIOUS_SHA=revision), text=True)
                self.assertEqual(output.strip(), expected)

    def test_next_patch_uses_highest_numeric_version_and_rejects_invalid_baselines(self):
        for version, tags, expected in (
                ("1.0.0", [], "1.0.1"),
                ("1.0.0", ["v1.0.0", "v1.0.9", "v1.0.10"], "1.0.11"),
                ("2.0.0", ["v1.9.99"], "2.0.1"),
                ("1.0.0", ["v2.3.4"], "2.3.5"),
                ("1.0.0", ["v9.0.0-rc.1", "vnext", "v1.0", "1.0.99"], "1.0.1")):
            with self.subTest(version=version, tags=tags):
                self.assertEqual(release_version.next_version(version, tags), expected)
        for version in (None, 1, "1.0", "v1.0.0", "01.0.0", "1.0.0-rc.1"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release_version.next_version(version, [])


if __name__ == "__main__":
    unittest.main()
