#!/usr/bin/env python3
"""Static validation for Gazebo world asset references.

This intentionally does not replace opening the world in Gazebo and manually
checking visual realism, collision geometry, or robot navigation. It catches
cheap-to-find packaging errors before that runtime pass.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

REMOTE_SCHEMES = {"http", "https", "file"}


def _resolve_model_uri(uri: str, models_dir: Path) -> Path | None:
    if not uri.startswith("model://"):
        return None
    relative = uri.removeprefix("model://")
    return models_dir / relative


def validate_world(world_path: Path, models_dir: Path) -> list[str]:
    errors: list[str] = []

    try:
        root = ET.parse(world_path).getroot()
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]

    if root.tag != "sdf":
        errors.append(f"expected <sdf> root, found <{root.tag}>")

    worlds = root.findall("world")
    if len(worlds) != 1:
        errors.append(f"expected exactly one <world>, found {len(worlds)}")

    for uri_node in root.findall(".//uri"):
        uri = (uri_node.text or "").strip()
        if not uri:
            errors.append("found empty <uri> element")
            continue

        parsed = urlparse(uri)
        if parsed.scheme in REMOTE_SCHEMES:
            # Remote/file URIs are outside this packaging check.
            continue

        if uri.startswith("model://"):
            target = _resolve_model_uri(uri, models_dir)
            assert target is not None
            if not target.exists():
                errors.append(f"missing model asset: {uri} -> {target}")
            continue

        # Plain relative paths are resolved relative to the world file.
        if not parsed.scheme:
            target = world_path.parent / uri
            if not target.exists():
                errors.append(f"missing relative asset: {uri} -> {target}")

    # Every collision and visual should have geometry. This catches accidental
    # empty elements that Gazebo may silently ignore.
    for tag in ("collision", "visual"):
        for node in root.findall(f".//{tag}"):
            if node.find("geometry") is None:
                name = node.attrib.get("name", "<unnamed>")
                errors.append(f"{tag} {name!r} has no <geometry>")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "world",
        nargs="?",
        default="worlds/kitchen.world",
        help="world file to validate (default: worlds/kitchen.world)",
    )
    parser.add_argument(
        "--models-dir",
        default="models",
        help="directory used to resolve model:// URIs (default: models)",
    )
    args = parser.parse_args()

    world_path = Path(args.world).resolve()
    models_dir = Path(args.models_dir).resolve()

    if not world_path.is_file():
        print(f"ERROR: world file does not exist: {world_path}", file=sys.stderr)
        return 2
    if not models_dir.is_dir():
        print(f"ERROR: models directory does not exist: {models_dir}", file=sys.stderr)
        return 2

    errors = validate_world(world_path, models_dir)
    if errors:
        print(f"FAIL: {len(errors)} static validation error(s)")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"PASS: {world_path} parses and all checked local assets resolve")
    print("NOTE: still run Gazebo and manually inspect visuals/collisions/navigation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
