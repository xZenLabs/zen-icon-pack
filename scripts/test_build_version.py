"""Run with python3 -m unittest discover -s scripts -p 'test_*.py'."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build

spec = importlib.util.spec_from_file_location("update_icons", Path(__file__).with_name("update-icons.py"))
update_icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_icons)


class BuildVersionTest(unittest.TestCase):
    def test_zip_version_preserves_source_manifest_artwork_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "zen-test"
            pack.mkdir()
            metadata = {"id": pack.name, "name": "Test", "version": "1.0.0", "author": "ZenLabs", "color": False}
            manifest = (json.dumps(metadata, indent=2) + "\n").encode()
            (pack / "pack.json").write_bytes(manifest)
            artwork = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"/>'
            icons = pack / "koreader"
            icons.mkdir(parents=True)
            (icons / "test.svg").write_bytes(artwork)
            output = root / "pack.zip"
            for version in (None, "1.0.0", "1.3.0"):
                with self.subTest(version=version):
                    build.write_zip(pack, output, version)
                    with zipfile.ZipFile(output) as archive:
                        self.assertIsNone(archive.testzip())
                        self.assertEqual(archive.namelist(), ["zen-test/pack.json", "zen-test/test.svg"])
                        expected = dict(metadata, version=version or metadata["version"])
                        self.assertEqual(json.loads(archive.read("zen-test/pack.json")), expected)
                        self.assertEqual(archive.read("zen-test/test.svg"), artwork)
                    self.assertEqual((pack / "pack.json").read_bytes(), manifest)
                    first = output.read_bytes()
                    build.write_zip(pack, output, version)
                    self.assertEqual(output.read_bytes(), first)

    def test_refresh_keeps_grouped_source_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = "koreader/star.empty.svg"
            manifest = root / "icon-mappings.json"
            manifest.write_text(json.dumps({"packs": [{
                "id": "zen-test", "prefix": "test", "icons": {source: "star"},
            }]}))
            artwork = b'<svg viewBox="0 0 24 24"/>'
            def download(task):
                return task[3] / task[2], artwork
            with patch.object(update_icons, "ROOT", root), \
                    patch.object(update_icons, "MAPPINGS", manifest), \
                    patch.object(update_icons, "download", side_effect=download):
                update_icons.main()
            pack = root / "packs" / "zen-test"
            self.assertEqual((pack / source).read_bytes(), artwork)
            self.assertFalse((pack / "star.empty.svg").exists())

    def test_duplicate_lookup_in_another_category_is_rejected(self):
        mappings = json.loads(build.MAPPINGS.read_text())["packs"]
        pack = next(item for item in mappings if (build.ROOT / "packs" / item["id"]).is_dir())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "packs" / pack["id"]
            shutil.copytree(build.ROOT / "packs" / pack["id"], directory)
            source = next(directory.rglob("star.empty.svg"))
            shutil.copyfile(source, directory / source.name)
            with patch.object(build, "ROOT", root):
                with self.assertRaisesRegex(SystemExit, "duplicate lookup filenames"):
                    build.validate_pack(pack, {Path(name).name for name in pack["icons"]})

    def test_invalid_release_versions_fail_before_building(self):
        for version in ("", "1.0", "v1.0.0", "01.0.0", "1.0.0-rc.1", "-1.0.0"):
            with self.subTest(version=version):
                result = subprocess.run(
                    [sys.executable, str(Path(build.__file__)), "--version=" + version],
                    capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("version must be MAJOR.MINOR.PATCH", result.stderr)


if __name__ == "__main__":
    unittest.main()
