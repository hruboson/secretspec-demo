#!/usr/bin/env python3
"""Bare-bones demo server for NASA's InSight: Mars Weather Service API.

Standard library only. The NASA key stays on the server (read from the
NASA_API_KEY env var, which secretspec injects) and the browser only ever
talks to /api/weather.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
NASA_URL = "https://api.nasa.gov/insight_weather/"
CACHE_SECONDS = 600  # DEMO_KEY is heavily rate limited; be gentle

_cache = {"at": 0.0, "body": None}


def fetch_weather():
    """Return the NASA JSON (as bytes), cached for CACHE_SECONDS."""
    now = time.time()
    if _cache["body"] and now - _cache["at"] < CACHE_SECONDS:
        return _cache["body"]
    query = urllib.parse.urlencode(
        {"api_key": API_KEY, "feedtype": "json", "ver": "1.0"}
    )
    req = urllib.request.Request(
        f"{NASA_URL}?{query}", headers={"User-Agent": "mars-weather-demo/0.1"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read()
    json.loads(body)  # validate before caching
    _cache.update(at=now, body=body)
    return body

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self._send(200, (Path(__file__).parent / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            static_dir = (Path(__file__).parent / "static").resolve()
            file_path = (static_dir / path[len("/static/"):]).resolve()

            # prevent access to files outside the static directory.
            if not file_path.is_relative_to(static_dir):
                self._send(403, b"Forbidden", "text/plain")
            elif file_path.is_file():
                content_types = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".svg": "image/svg+xml",
                    ".ico": "image/x-icon",
                }
                ctype = content_types.get(
                    file_path.suffix.lower(), "application/octet-stream"
                )
                self._send(200, file_path.read_bytes(), ctype)
            else:
                self._send(404, b"Not found", "text/plain")
        elif path == "/api/weather":
            try:
                self._send(200, fetch_weather(), "application/json")
            except urllib.error.HTTPError as e:
                msg = f"NASA API returned {e.code}" + (
                    " (rate limited; try a real key)" if e.code == 429 else ""
                )
                self._send(502, json.dumps({"error": msg}).encode(), "application/json")
            except Exception as e:  # network, bad JSON, etc.
                self._send(502, json.dumps({"error": str(e)}).encode(), "application/json")
        else:
            self._send(404, b"Not found", "text/plain")


if __name__ == "__main__":
    using = "DEMO_KEY (limited)" if API_KEY == "DEMO_KEY" else "custom key"
    print(f"Serving on http://{HOST}:{PORT}  ·  NASA key: {using}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
