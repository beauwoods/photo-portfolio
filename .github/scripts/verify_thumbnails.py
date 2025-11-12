#!/usr/bin/env python3
"""
Ensure every image in images.json has matching 320/1600 thumbnails.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PHOTO_SIZES = ("320", "1600")
THUMBS_DIR = Path("thumbs")
IMAGES_JSON = Path("images.json")


def main() -> int:
    if not IMAGES_JSON.exists():
        print(f"{IMAGES_JSON} not found; did the indexer run?", file=sys.stderr)
        return 1

    with IMAGES_JSON.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    images = data["images"] if isinstance(data, dict) else data
    missing: list[Path] = []

    for img in images:
        base = Path(img["path"]).stem
        for size in PHOTO_SIZES:
            thumb = THUMBS_DIR / f"{base}_{size}.webp"
            if not thumb.exists():
                missing.append(thumb)

    if missing:
        print("Missing thumbnails detected:")
        for path in missing:
            print(f" - {path}")
        return 1

    print("All referenced thumbnails are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
