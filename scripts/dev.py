#!/usr/bin/env python3
"""Build, serve, and rebuild the site when source files change."""
from __future__ import annotations

import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = [ROOT / "data", ROOT / "content", ROOT / "templates", ROOT / "src"]


def build() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], cwd=ROOT)
    if result.returncode:
        print("Build failed; keeping the previous dist folder.")


def snapshot() -> dict[str, int]:
    values = {}
    for folder in WATCH:
        for path in folder.rglob("*"):
            if path.is_file():
                try: values[str(path)] = path.stat().st_mtime_ns
                except FileNotFoundError: pass
    return values


def watch() -> None:
    before = snapshot()
    while True:
        time.sleep(.8)
        after = snapshot()
        if after != before:
            print("\nChange detected — rebuilding…")
            build()
            before = after


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "dist"), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    build()
    threading.Thread(target=watch, daemon=True).start()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving http://localhost:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
