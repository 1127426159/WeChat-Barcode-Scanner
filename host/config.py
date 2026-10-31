"""Configuration storage for WeChat-Barcode-Scanner."""

from __future__ import annotations

import json
import os
import socket
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_NAME = "WeChat-Barcode-Scanner"
LEGACY_APP_NAMES = ("WxMiniScanGun", "ScannerHost")


def _app_base_dir() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return Path.home() / "Library" / "Application Support"


def _config_override():
    return (
        os.environ.get("WECHAT_BARCODE_SCANNER_DIR")
        or os.environ.get("WX_MINI_SCANGUN_DIR")
        or os.environ.get("SCANNER_HOST_DIR")
    )


def config_dir() -> Path:
    override = _config_override()
    if override:
        return Path(override)
    return _app_base_dir() / APP_NAME


def legacy_config_paths() -> list:
    base = _app_base_dir()
    return [base / name / "config.json" for name in LEGACY_APP_NAMES]


def config_path() -> Path:
    return config_dir() / "config.json"


def default_device_name() -> str:
    try:
        return socket.gethostname() or "WeChat-Barcode-Scanner"
    except OSError:
        return "WeChat-Barcode-Scanner"


def enable_utf8_console() -> None:
    """Make Chinese messages readable in the console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


@dataclass
class Config:
    device_name: str = field(default_factory=default_device_name)
    http_port: int = 47653
    append_enter: bool = True
    key_delay_ms: int = 12
    autostart: bool = False

    @classmethod
    def load(cls) -> Config:
        path = config_path()
        if not path.exists() and not _config_override():
            for legacy_path in legacy_config_paths():
                if legacy_path.exists():
                    path = legacy_path
                    break
        cfg = cls()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = {}
            for key, value in data.items():
                if hasattr(cfg, key) and isinstance(value, type(getattr(cfg, key))):
                    setattr(cfg, key, value)
        cfg.key_delay_ms = max(0, min(cfg.key_delay_ms, 200))
        return cfg

    def save(self) -> None:
        path = config_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            print(f"[警告] 配置保存失败，本次仍可正常使用：{exc}", flush=True)
