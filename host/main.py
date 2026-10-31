"""Entry point for WeChat-Barcode-Scanner."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from .config import Config, enable_utf8_console
from .keyboard import InputError, KeyInjector
from .netinfo import local_ipv4_addresses
from .server import ScannerAPI, new_device_id, serve


def connection_payload(cfg: Config, ips: List[str]) -> str:
    return json.dumps(
        {"v": 1, "name": cfg.device_name, "port": cfg.http_port, "ips": ips},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def show_qr_code(qr, payload: str) -> None:
    if sys.platform == "win32":
        image_path = Path(tempfile.gettempdir()) / "WeChat-Barcode-Scanner-QR.png"
        try:
            qr.save(str(image_path), scale=10, border=4)
            print("\n正在打开清晰的二维码图片……", flush=True)
            print(f"  图片路径：{image_path}", flush=True)
            os.startfile(str(image_path))
            print("  如果图片没有自动打开，请双击上面的图片路径。", flush=True)
            return
        except (OSError, ValueError) as exc:
            print(f"  二维码图片打开失败：{exc}", flush=True)
            print("  请在小程序中手动输入下面的连接信息：", flush=True)
            print(f"  {payload}", flush=True)
            return

    print("\n用微信小程序扫描下面的二维码即可连接：", flush=True)
    qr.terminal(compact=True)


def print_connection(cfg: Config, ips: List[str]) -> None:
    payload = connection_payload(cfg, ips)
    print("扫码接收端已启动", flush=True)
    print(f"  设备名：{cfg.device_name}", flush=True)
    if ips:
        for ip in ips:
            print(f"  地址：{ip}:{cfg.http_port}", flush=True)
    else:
        print("  未检测到局域网地址，请检查网络连接", flush=True)

    try:
        import segno
    except ImportError:
        segno = None

    if segno is not None:
        qr = segno.make(payload, error="m")
        show_qr_code(qr, payload)
    else:
        print("\n连接信息（小程序里可手动输入）：", flush=True)
        print(f"  {payload}", flush=True)
        print("  提示：pip install segno 后可显示二维码", flush=True)

    print(
        f"\n自动回车：{'是' if cfg.append_enter else '否'}  "
        f"按键间隔：{cfg.key_delay_ms}ms  按 Ctrl+C 停止",
        flush=True,
    )


def main(argv: Optional[List[str]] = None) -> int:
    enable_utf8_console()
    parser = argparse.ArgumentParser(
        prog="WeChat-Barcode-Scanner-host",
        description="微信小程序扫码枪电脑接收端",
    )
    parser.add_argument("--port", type=int, help="HTTP 端口")
    parser.add_argument("--name", help="手机上显示的设备名")
    parser.add_argument("--no-enter", action="store_true", help="扫码后不追加回车")
    parser.add_argument("--delay", type=int, help="按键间隔（毫秒）")
    parser.add_argument("--test", metavar="TEXT", help="向当前窗口输入一段文本后退出")
    args = parser.parse_args(argv)

    cfg = Config.load()
    changed = False
    if args.port:
        cfg.http_port = args.port
        changed = True
    if args.name:
        cfg.device_name = args.name
        changed = True
    if args.no_enter:
        cfg.append_enter = False
        changed = True
    if args.delay is not None:
        cfg.key_delay_ms = args.delay
        changed = True

    try:
        injector = KeyInjector(cfg.key_delay_ms)
    except InputError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    if args.test:
        try:
            injector.type_text(args.test, cfg.append_enter)
        except InputError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 3
        print("测试文本已发送。")
        return 0

    if changed:
        cfg.save()

    hint = injector.permission_hint
    if hint:
        print(f"[提示] {hint}", flush=True)

    def on_scan(code: str) -> None:
        injector.type_text(code, cfg.append_enter)
        print(f"[scan] {code}", flush=True)

    api = ScannerAPI(cfg.device_name, on_scan)
    device_id = new_device_id()

    try:
        httpd, _ = serve(api, device_id, cfg.device_name, cfg.http_port)
    except OSError as exc:
        print(f"错误：无法监听端口 {cfg.http_port}：{exc}", file=sys.stderr)
        return 4

    print_connection(cfg, local_ipv4_addresses())

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
    print("已停止。", flush=True)
    return 0
