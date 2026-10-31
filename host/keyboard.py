"""Text injection built on the open-source pyautogui library.

pyautogui covers Windows and macOS. On Windows we prefer pyautogui's native
backend and fall back to a raw SendInput path when a character cannot be typed.
"""

from __future__ import annotations

import platform
import threading
import time
from typing import List, Optional

PLATFORM = platform.system()

try:
    import pyautogui
except Exception:  # pragma: no cover - pyautogui needs a display
    pyautogui = None


class InputError(RuntimeError):
    """Raised when the OS refuses or fails to inject input."""

    def __init__(self, message: str, needs_admin: bool = False) -> None:
        super().__init__(message)
        self.needs_admin = needs_admin


class KeyInjector:
    """Types text into whichever window currently has focus."""

    def __init__(self, delay_ms: int = 12) -> None:
        if PLATFORM not in ("Windows", "Darwin"):
            raise InputError(f"不支持的平台：{PLATFORM}（当前仅支持 Windows 与 macOS）")
        self.delay = max(0, delay_ms) / 1000.0
        self._lock = threading.Lock()
        self._sendinput = _WinSendInput() if PLATFORM == "Windows" else None
        if pyautogui is not None:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0

    @property
    def permission_hint(self) -> Optional[str]:
        if PLATFORM != "Darwin":
            return None
        try:
            import ApplicationServices
        except ImportError:
            return "macOS 需要授予本程序「辅助功能」权限，否则按键会被静默丢弃。"
        if ApplicationServices.AXIsProcessTrusted():
            return None
        return "macOS 需要授予本程序「辅助功能」权限，否则按键会被静默丢弃。"

    def _type_ascii(self, text: str) -> bool:
        """Type simple text through pyautogui when possible."""
        if pyautogui is None:
            return False
        try:
            pyautogui.write(text, interval=self.delay)
            return True
        except Exception:  # noqa: BLE001 - fall through to platform backend
            return False

    def _type_unicode(self, text: str) -> None:
        if self._sendinput is not None:
            self._sendinput.type_text(text, self.delay)
            return
        if pyautogui is None:
            raise InputError("无法输入文本：缺少可用的键盘后端")
        # macOS: CGEvent unicode typing via Quartz
        import Quartz

        for ch in text:
            for down in (True, False):
                event = Quartz.CGEventCreateKeyboardEvent(None, 0, down)
                Quartz.CGEventKeyboardSetUnicodeString(event, len(ch), ch)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
            if self.delay:
                time.sleep(self.delay)

    def type_text(self, text: str, append_enter: bool = True) -> None:
        if not text:
            raise InputError("空内容")
        with self._lock:
            if not text.isascii():
                self._type_unicode(text)
            elif not self._type_ascii(text):
                self._type_unicode(text)
            if append_enter:
                if pyautogui is not None and self._type_ascii_enter():
                    pass
                elif self._sendinput is not None:
                    self._sendinput.press_enter(self.delay)
                else:
                    import Quartz

                    for down in (True, False):
                        Quartz.CGEventPost(
                            Quartz.kCGHIDEventTap,
                            Quartz.CGEventCreateKeyboardEvent(None, 0x24, down),
                        )

    def _type_ascii_enter(self) -> bool:
        try:
            pyautogui.press("enter")
            return True
        except Exception:  # noqa: BLE001
            return False


class _WinSendInput:
    """Raw SendInput with Unicode support, used for CJK and as a fallback."""

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    INPUT_KEYBOARD = 1
    VK_RETURN = 0x0D
    ULONG_PTR = None

    def __init__(self) -> None:
        import ctypes

        self.ctypes = ctypes
        self.ULONG_PTR = ctypes.c_size_t
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.SendInput.argtypes = (
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_int,
        )
        self.user32.SendInput.restype = ctypes.c_uint
        self._structs = self._build_structs()
        self._input_size = ctypes.sizeof(self._structs["INPUT"])

    def _build_structs(self) -> dict:
        ctypes = self.ctypes
        ULONG_PTR = self.ULONG_PTR

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ULONG_PTR),
            ]

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ULONG_PTR),
            ]

        class HARDWAREINPUT(ctypes.Structure):
            _fields_ = [
                ("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_ushort),
                ("wParamH", ctypes.c_ushort),
            ]

        class UNION(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

        class INPUT(ctypes.Structure):
            _anonymous_ = ("u",)
            _fields_ = [("type", ctypes.c_ulong), ("u", UNION)]

        return {"KEYBDINPUT": KEYBDINPUT, "INPUT": INPUT}

    def _send(self, vk: int, scan: int, flags: int) -> None:
        structs = self._structs
        item = structs["INPUT"](type=self.INPUT_KEYBOARD)
        item.u.ki = structs["KEYBDINPUT"](wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)
        sent = self.user32.SendInput(1, self.ctypes.byref(item), self._input_size)
        if sent != 1:
            code = self.ctypes.get_last_error()
            if code == 5:
                raise InputError(
                    "目标窗口以管理员权限运行，按键被系统拦截（错误码 5）。"
                    "请以管理员身份重启本程序后重试。",
                    needs_admin=True,
                )
            raise InputError(f"SendInput 失败（错误码 {code}）")

    @staticmethod
    def _units(ch: str) -> List[int]:
        encoded = ch.encode("utf-16-le")
        return [int.from_bytes(encoded[i : i + 2], "little") for i in range(0, len(encoded), 2)]

    def type_text(self, text: str, delay: float) -> None:
        for ch in text:
            for unit in self._units(ch):
                self._send(0, unit, self.KEYEVENTF_UNICODE)
                self._send(0, unit, self.KEYEVENTF_UNICODE | self.KEYEVENTF_KEYUP)
            if delay:
                time.sleep(delay)

    def press_enter(self, delay: float) -> None:
        self._send(self.VK_RETURN, 0, 0)
        self._send(self.VK_RETURN, 0, self.KEYEVENTF_KEYUP)
        if delay:
            time.sleep(delay)
