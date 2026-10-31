"""Minimal HTTP API used by the mini program."""

from __future__ import annotations

import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict, Optional, Tuple

MAX_BODY = 4096
DEDUPE_WINDOW = 1.5
SERVICE_ID = "WeChat-Barcode-Scanner"


class ScannerAPI:
    def __init__(self, device_name: str, on_scan: Callable[[str], None]) -> None:
        self.device_name = device_name
        self._on_scan = on_scan
        self._lock = threading.Lock()
        self._seen: Dict[str, float] = {}
        self.last_code = ""
        self.last_error = ""
        self.count = 0

    def handle_scan(self, code: str, seq: Optional[str]) -> Tuple[int, dict]:
        code = code.strip()
        if not code:
            return 400, {"ok": False, "error": "empty code"}
        now = time.monotonic()
        key = seq or code
        with self._lock:
            for old in [k for k, t in self._seen.items() if now - t > DEDUPE_WINDOW]:
                self._seen.pop(old, None)
            if key in self._seen:
                return 200, {"ok": True, "duplicate": True}
            self._seen[key] = now
        try:
            self._on_scan(code)
        except Exception as exc:  # noqa: BLE001 - surface to the phone
            self.last_error = str(exc)
            needs_admin = bool(getattr(exc, "needs_admin", False))
            return 409, {"ok": False, "error": str(exc), "needs_admin": needs_admin}
        with self._lock:
            self.last_code = code
            self.count += 1
        return 200, {"ok": True, "duplicate": False}

    def status(self) -> dict:
        with self._lock:
            return {
                "ok": True,
                "device": self.device_name,
                "last_code": self.last_code,
                "count": self.count,
                "last_error": self.last_error,
            }


def make_handler(api: ScannerAPI, device_id: str, device_name: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "WeChat-Barcode-Scanner/0.1"

        def log_message(self, fmt: str, *args) -> None:  # keep console quiet
            return

        def _send(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "content-type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self._send(204, {})

        def do_GET(self) -> None:
            if self.path.startswith("/ping"):
                self._send(
                    200,
                    {
                        "ok": True,
                        "service": SERVICE_ID,
                        "id": device_id,
                        "device": device_name,
                        "ver": 1,
                    },
                )
            elif self.path.startswith("/status"):
                self._send(200, api.status())
            else:
                self._send(404, {"ok": False, "error": "not found"})

        def do_POST(self) -> None:
            if not self.path.startswith("/scan"):
                self._send(404, {"ok": False, "error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0 or length > MAX_BODY:
                self._send(400, {"ok": False, "error": "bad body"})
                return
            try:
                data = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                self._send(400, {"ok": False, "error": "invalid json"})
                return
            code = data.get("code")
            if not isinstance(code, str):
                self._send(400, {"ok": False, "error": "code required"})
                return
            status, payload = api.handle_scan(code, data.get("seq"))
            self._send(status, payload)

    return Handler


def serve(
    api: ScannerAPI, device_id: str, device_name: str, port: int
) -> Tuple[ThreadingHTTPServer, threading.Thread]:
    httpd = ThreadingHTTPServer(("0.0.0.0", port), make_handler(api, device_id, device_name))
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, name="http", daemon=True)
    thread.start()
    return httpd, thread


def new_device_id() -> str:
    return uuid.uuid4().hex[:12]
