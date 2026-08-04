#!/usr/bin/env python3
"""Validate generated routes and local links in dist/."""
from __future__ import annotations
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
errors: list[str] = []
if not DIST.exists():
    print("dist/ does not exist; run scripts/build.py first")
    sys.exit(1)

for page in DIST.rglob("*.html"):
    text = page.read_text(encoding="utf-8")
    if "{{" in text or "}}" in text:
        errors.append(f"Unresolved template token in {page.relative_to(DIST)}")
    for href in re.findall(r'href="([^"]+)"', text):
        if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        clean = urlsplit(href).path
        if not clean:
            continue
        if clean.startswith("/"):
            target = DIST / clean.lstrip("/")
        else:
            target = page.parent / clean
        if clean.endswith("/"):
            target = target / "index.html"
        elif target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"Broken link in {page.relative_to(DIST)}: {href}")

if errors:
    print("Generated-site validation failed:")
    for error in sorted(set(errors)): print(f"  - {error}")
    sys.exit(1)
print("Generated-site validation passed.")
