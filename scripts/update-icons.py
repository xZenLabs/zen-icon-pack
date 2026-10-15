#!/usr/bin/env python3
"""Download the mapped Iconify SVGs into the committed pack folders."""

from __future__ import annotations

import json
import shutil
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / "icon-mappings.json"
API_ROOT = "https://api.iconify.design"


def download(task: tuple[str, str, str, Path]) -> tuple[Path, bytes]:
    prefix, source_name, filename, destination = task
    icon = urllib.parse.quote(source_name, safe="-")
    url = f"{API_ROOT}/{prefix}/{icon}.svg?color=%23000000&width=24&height=24"
    request = urllib.request.Request(url, headers={"User-Agent": "zen-icon-pack updater"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    if not data.startswith(b"<svg ") or b"viewBox=" not in data:
        raise ValueError(f"Iconify returned invalid SVG for {prefix}:{source_name}")
    if b"currentColor" in data:
        raise ValueError(f"Iconify returned a theme-dependent color for {prefix}:{source_name}")
    return destination / filename, data.rstrip() + b"\n"


def main() -> None:
    manifest = json.loads(MAPPINGS.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="zen-icon-packs-") as temporary:
        temporary_root = Path(temporary)
        tasks = []
        for pack in manifest["packs"]:
            destination = temporary_root / pack["id"]
            destination.mkdir()
            for filename, source in pack["icons"].items():
                if ":" in source:
                    prefix, source_name = source.split(":", 1)
                else:
                    prefix, source_name = pack["prefix"], source
                tasks.append((prefix, source_name, filename, destination))

        with ThreadPoolExecutor(max_workers=12) as executor:
            downloads = list(executor.map(download, tasks))

        for path, data in downloads:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        for pack in manifest["packs"]:
            destination = ROOT / "packs" / pack["id"]
            for source in sorted((temporary_root / pack["id"]).rglob("*.svg")):
                target = destination / source.relative_to(temporary_root / pack["id"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

    print(f"Updated {len(tasks)} SVG files across {len(manifest['packs'])} packs.")


if __name__ == "__main__":
    main()
