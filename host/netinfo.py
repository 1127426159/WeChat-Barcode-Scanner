"""Report every local IPv4 address the phone might reach."""

from __future__ import annotations

import socket
import subprocess
import sys
from typing import List, Set


def _from_hostname() -> Set[str]:
    found: Set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            found.add(info[4][0])
    except OSError:
        pass
    return found


def _from_route_probe() -> Set[str]:
    found: Set[str] = set()
    for target in ("8.8.8.8", "1.1.1.1"):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((target, 80))
            found.add(sock.getsockname()[0])
        except OSError:
            pass
        finally:
            sock.close()
    return found


def _from_ipconfig() -> Set[str]:
    """Scrape `ipconfig` for IPv4 addresses, skipping masks and gateways."""
    found: Set[str] = set()
    if sys.platform != "win32":
        return found
    try:
        out = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="gbk",
            errors="replace",
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return found

    for line in out.splitlines():
        if ":" not in line:
            continue
        label, _, value = line.partition(":")
        label = label.strip().lower()
        if not any(key in label for key in ("ipv4", "ip address", "自动配置")):
            continue
        if any(key in label for key in ("mask", "gateway", "掩码", "网关")):
            continue
        candidate = value.strip()
        if candidate.lower().startswith(("fe80", "::")):
            continue
        parts = candidate.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            continue
        found.add(candidate)
    return found


def _usable(ip: str) -> bool:
    if ip.startswith(("127.", "169.254.", "0.", "255.")):
        return False
    octets = [int(p) for p in ip.split(".")]
    # Skip subnet masks, which look like 255.255.255.0 etc.
    if octets[0] == 255 or octets[1] == 255:
        return False
    return True


def local_ipv4_addresses() -> List[str]:
    """Return de-duplicated LAN addresses, the default-route one first."""
    ordered: List[str] = []
    for ip in sorted(_from_route_probe()):
        if _usable(ip):
            ordered.append(ip)
    for ip in sorted(_from_hostname() | _from_ipconfig()):
        if _usable(ip) and ip not in ordered:
            ordered.append(ip)
    return ordered
