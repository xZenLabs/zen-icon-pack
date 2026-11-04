#!/usr/bin/env python3
"""Download the mapped Iconify SVGs into the committed pack folders."""

from __future__ import annotations

import json
import re
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


def strike(data: bytes) -> bytes:
    """Draw a diagonal line through an icon, at its own line weight where declared."""
    svg = data.decode("utf-8").rstrip()
    x, y, w, h = (float(value) for value in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    widths = [float(value) for value in re.findall(r'stroke-width="([0-9.]+)"', svg)]
    n = lambda value: f"{value:.4g}"
    line = (f'<path stroke="#000000" stroke-linecap="round" stroke-width="{n(max(widths, default=w / 16))}" '
            f'd="M{n(x + w / 8)} {n(y + h / 8)}L{n(x + w * 7 / 8)} {n(y + h * 7 / 8)}"/>')
    return (svg.removesuffix("</svg>") + line + "</svg>\n").encode("utf-8")


def main() -> None:
    manifest = json.loads(MAPPINGS.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="zen-icon-packs-") as temporary:
        temporary_root = Path(temporary)
        tasks = []
        strikes = []
        for pack in manifest["packs"]:
            destination = temporary_root / pack["id"]
            destination.mkdir()
            for filename, source in pack["icons"].items():
                if source.startswith("strike:"):
                    strikes.append((destination / filename, destination / source.removeprefix("strike:")))
                    continue
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
        for path, base in strikes:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(strike(base.read_bytes()))

        for pack in manifest["packs"]:
            destination = ROOT / "packs" / pack["id"]
            for source in sorted((temporary_root / pack["id"]).rglob("*.svg")):
                target = destination / source.relative_to(temporary_root / pack["id"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

    print(f"Updated {len(tasks) + len(strikes)} SVG files across {len(manifest['packs'])} packs.")


if __name__ == "__main__":
    main()
