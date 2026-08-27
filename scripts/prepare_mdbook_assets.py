#!/usr/bin/env python3
"""Populate each mdBook theme directory from the shared source assets."""

from __future__ import annotations

import shutil
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
EDITIONS = ("en", "zh-TW")
SHARED_ASSETS = {
    REPOSITORY_ROOT / "favicon.svg": "favicon.svg",
    REPOSITORY_ROOT / "assets" / "mdbook" / "code-fix.css": "code-fix.css",
    REPOSITORY_ROOT / "assets" / "mdbook" / "share.css": "share.css",
    REPOSITORY_ROOT / "assets" / "mdbook" / "share.js": "share.js",
}


def copy_if_changed(source: Path, destination: Path) -> bool:
    data = source.read_bytes()
    if destination.exists() and destination.read_bytes() == data:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    shutil.copymode(source, destination)
    return True


def main() -> None:
    missing = [str(path) for path in SHARED_ASSETS if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing shared mdBook assets: " + ", ".join(missing))

    updated = 0
    for edition in EDITIONS:
        theme_dir = REPOSITORY_ROOT / edition / "theme"
        for source, filename in SHARED_ASSETS.items():
            if copy_if_changed(source, theme_dir / filename):
                updated += 1

    print(
        f"Prepared {len(SHARED_ASSETS)} shared mdBook assets for "
        f"{len(EDITIONS)} editions ({updated} files updated)."
    )


if __name__ == "__main__":
    main()
