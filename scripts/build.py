#!/usr/bin/env python3
"""Validate all icon packs and create deterministic release ZIP files."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "icon-mappings.json"
REQUIRED_PACK_FILES = {"LICENSE-ICONS.txt", "README.md", "pack.json"}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
VISIBLE_GROUPS = {
    "Navbar": {
        "appbar.menu.svg",
        "appbar.search.svg",
        "book.opened.svg",
        "home.svg",
        "library.svg",
        "star.empty.svg",
        "tab_authors.svg",
        "tab_collections.svg",
        "tab_exit.svg",
        "tab_history.svg",
        "tab_left.svg",
        "tab_manga.svg",
        "tab_news.svg",
        "tab_right.svg",
        "tab_series.svg",
        "tab_stats.svg",
        "tab_tags.svg",
        "tab_to_be_read.svg",
    },
    "top menu": {
        "appbar.filebrowser.svg",
        "appbar.menu.svg",
        "appbar.navigation.svg",
        "appbar.search.svg",
        "appbar.settings.svg",
        "appbar.tools.svg",
        "appbar.typeset.svg",
    },
    "reader quick settings": {
        "appbar.contrast.svg",
        "appbar.crop.svg",
        "appbar.pagefit.svg",
        "appbar.pageview.svg",
        "appbar.rotation.svg",
        "appbar.settings.svg",
        "appbar.textsize.svg",
    },
    "lookup actions": {
        "lookup.ai.svg",
        "lookup.dictionary.svg",
        "lookup.highlight.svg",
        "lookup.search.svg",
        "lookup.translate.svg",
        "lookup.vocab.svg",
        "lookup.vocab_remove.svg",
        "lookup.wikipedia.svg",
    },
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def validate_svg(path: Path) -> None:
    data = path.read_bytes()
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        fail(f"{path.relative_to(ROOT)} is not valid XML: {error}")
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        fail(f"{path.relative_to(ROOT)} does not have an SVG root element")
    if "viewBox" not in root.attrib:
        fail(f"{path.relative_to(ROOT)} has no viewBox")
    if root.attrib.get("width") != "24" or root.attrib.get("height") != "24":
        fail(f"{path.relative_to(ROOT)} must use a numeric 24x24 canvas")
    if b"currentColor" in data:
        fail(f"{path.relative_to(ROOT)} must use an explicit e-ink-safe color")


def validate_pack(pack: dict[str, object], expected_icons: set[str]) -> Path:
    pack_id = str(pack["id"])
    pack_dir = ROOT / "packs" / pack_id
    if not pack_dir.is_dir():
        fail(f"missing pack directory: {pack_dir.relative_to(ROOT)}")

    mappings = {Path(name).name: source for name, source in pack["icons"].items()}
    mapped_icons = set(mappings)
    if len(mapped_icons) != len(pack["icons"]):
        fail(f"{pack_id} maps duplicate lookup filenames")
    if mapped_icons != expected_icons:
        missing = sorted(expected_icons - mapped_icons)
        extra = sorted(mapped_icons - expected_icons)
        fail(f"{pack_id} mappings differ from the canonical set (missing={missing}, extra={extra})")

    for group, filenames in VISIBLE_GROUPS.items():
        if not filenames <= expected_icons:
            fail(f"{group} contains filenames missing from the template")
        source_icons = [mappings[filename] for filename in filenames]
        duplicate_sources = sorted(
            source for source, count in Counter(source_icons).items() if count > 1
        )
        if duplicate_sources:
            fail(f"{pack_id} reuses icons within {group}: {duplicate_sources}")

    paths = list(pack_dir.rglob("*.svg"))
    actual_icons = {path.name: path for path in paths}
    if len(actual_icons) != len(paths):
        fail(f"{pack_id} contains duplicate lookup filenames")
    if set(actual_icons) != expected_icons:
        missing = sorted(expected_icons - actual_icons.keys())
        extra = sorted(actual_icons.keys() - expected_icons)
        fail(f"{pack_id} files differ from the template (missing={missing}, extra={extra})")
    if {path.relative_to(pack_dir).as_posix() for path in paths} != set(pack["icons"]):
        fail(f"{pack_id} source paths differ from icon-mappings.json")

    for group, filenames in VISIBLE_GROUPS.items():
        content_groups: dict[str, list[str]] = {}
        for filename in sorted(filenames):
            icon = actual_icons[filename]
            digest = sha256(icon.read_bytes()).hexdigest()
            content_groups.setdefault(digest, []).append(filename)
        duplicate_files = [files for files in content_groups.values() if len(files) > 1]
        if duplicate_files:
            fail(f"{pack_id} contains identical icons within {group}: {duplicate_files}")

    actual_files = {path.name for path in pack_dir.iterdir() if path.is_file()}
    missing_pack_files = REQUIRED_PACK_FILES - actual_files
    if missing_pack_files:
        fail(f"{pack_id} is missing {sorted(missing_pack_files)}")

    metadata = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    if metadata.get("id") != pack_id:
        fail(f"{pack_id}/pack.json id must match its folder name")
    if metadata.get("name") != pack["name"]:
        fail(f"{pack_id}/pack.json name differs from icon-mappings.json")

    for icon in sorted(paths):
        validate_svg(icon)
    return pack_dir


def write_zip(pack_dir: Path, output: Path, version: str | None = None) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((item for item in pack_dir.rglob("*") if item.is_file()),
                           key=lambda item: item.name if item.suffix == ".svg"
                           else item.relative_to(pack_dir).as_posix()):
            relative = (f"{pack_dir.name}/{path.name}" if path.suffix == ".svg"
                        else path.relative_to(pack_dir.parent).as_posix())
            info = zipfile.ZipInfo(relative, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            data = path.read_bytes()
            if path == pack_dir / "pack.json" and version is not None:
                metadata = json.loads(data)
                metadata["version"] = version
                data = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
            archive.writestr(info, data, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Override the shared release version in root pack.json")
    args = parser.parse_args()
    version = args.version if args.version is not None else json.loads(
        (ROOT / "pack.json").read_text(encoding="utf-8"))["version"]
    if not isinstance(version, str) or not re.fullmatch(
            r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}", version):
        fail("version must be MAJOR.MINOR.PATCH")

    manifest = json.loads(MAPPINGS.read_text(encoding="utf-8"))
    packs = manifest.get("packs", [])
    pack_ids = [pack["id"] for pack in packs]
    if not packs or len(pack_ids) != len(set(pack_ids)):
        fail("icon-mappings.json must define uniquely named packs")

    expected_icons = {Path(name).name for name in packs[0]["icons"]}
    if len(expected_icons) != 62:
        fail(f"expected 62 canonical icon mappings, found {len(expected_icons)}")

    pack_dirs = [validate_pack(pack, expected_icons) for pack in packs]
    output = ROOT / "dist"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for pack_dir in pack_dirs:
        destination = output / f"{pack_dir.name}.zip"
        write_zip(pack_dir, destination, version)
        print(f"Built {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
