#!/usr/bin/env python3
"""Honor a pushed version increase, otherwise select the next patch release."""

import json
import os
from pathlib import Path
import re
import subprocess


VERSION_PATTERN = r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}"


def next_version(version, tags, previous_version=None):
    if not isinstance(version, str) or not re.fullmatch(VERSION_PATTERN, version):
        raise ValueError("pack.json version must be MAJOR.MINOR.PATCH")
    current = tuple(map(int, version.split(".")))
    if previous_version is not None:
        if not isinstance(previous_version, str) or not re.fullmatch(VERSION_PATTERN, previous_version):
            raise ValueError("Previous pack.json version must be MAJOR.MINOR.PATCH")
        if current > tuple(map(int, previous_version.split("."))):
            return version
    versions = [current]
    versions.extend(tuple(map(int, tag[1:].split("."))) for tag in tags
                    if re.fullmatch("v" + VERSION_PATTERN, tag))
    major, minor, patch = max(versions)
    return f"{major}.{minor}.{patch + 1}"


def version_before_push(root, revision):
    if not revision or set(revision) == {"0"}:
        return None
    files = subprocess.check_output(
        ["git", "ls-tree", "--name-only", revision, "--",
         "pack.json", "zen-icon-pack/pack.json"], cwd=root, text=True)
    if not files.strip():
        return None
    manifest_path = "pack.json" if "pack.json" in files.splitlines() else "zen-icon-pack/pack.json"
    manifest = subprocess.check_output(["git", "show", f"{revision}:{manifest_path}"], cwd=root, text=True)
    return json.loads(manifest)["version"]


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    version = json.loads((root / "pack.json").read_text())["version"]
    tags = subprocess.check_output(["git", "tag", "--list", "v*"], cwd=root, text=True)
    previous = version_before_push(root, os.environ.get("PREVIOUS_SHA"))
    print(next_version(version, tags.splitlines(), previous))
