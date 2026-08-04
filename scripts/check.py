#!/usr/bin/env python3
"""Small project validator used locally and in GitHub Actions."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required = [
    ROOT / "data/site.json",
    ROOT / "templates/base.html",
    ROOT / "src/assets/css/main.css",
    ROOT / "src/assets/js/main.js",
    ROOT / "src/assets/js/cosmic-web.js",
]
for path in required:
    if not path.exists(): errors.append(f"Missing required file: {path.relative_to(ROOT)}")

try:
    data = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
    for key in ["site", "profile", "navigation", "research", "projects", "publications"]:
        if key not in data: errors.append(f"Missing data key: {key}")
    email = data.get("profile", {}).get("email", "")
    if "@" not in email: errors.append("Profile email is invalid")
except Exception as exc:
    errors.append(f"Could not parse data/site.json: {exc}")

for post in (ROOT / "content/blog").glob("*.md"):
    text = post.read_text(encoding="utf-8")
    for field in ["title:", "date:", "category:", "excerpt:"]:
        if field not in text: errors.append(f"{post.name} is missing front-matter field {field}")

if errors:
    print("Project validation failed:")
    for error in errors: print(f"  - {error}")
    sys.exit(1)
print("Project validation passed.")
