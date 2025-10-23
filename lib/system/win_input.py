"""
Low-level keyboard input using Windows SendInput via ctypes.
Supports common keys by name (digits, letters, F1-F24, SPACE, ENTER, ESC, TAB, SHIFT, CTRL, ALT, ARROWS).
Note: Some games may still block simulated input due to anti-cheat.
"""
from __future__ import annotations
import time
import ctypes
import sys
import platform
from typing import Any
from ctypes import wintypes

# Platform detection
IS_WINDOWS = sys.platform == 'win32' or platform.system() == 'Windows'

# Only load Windows DLL on Windows platform
if IS_WINDOWS:
    user32 = ctypes.WinDLL('user32', use_last_error=True)
else:
    # Mock user32 for non-Windows platforms (for testing/CI)
    class MockCallable:
        """Mock callable with mutable argtypes/restype."""
        def __init__(self, return_value: Any = 1):
            self.argtypes: Any = None
            self.restype: Any = None
            self._return_value = return_value
        
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self._return_value
    
    class MockWinDLL:
        """Mock Windows DLL for non-Windows platforms."""
        def __init__(self):
            self.SendInput = MockCallable(1)  # Simulate successful input
            self.MapVirtualKeyW = MockCallable(0)  # Return scancode
    
    user32 = MockWinDLL()  # type: ignore[assignment]

# Constants
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
MAPVK_VK_TO_VSC = 0

# Virtual-key codes for special keys
VK = {
    'BACK': 0x08,
    'TAB': 0x09,
    'ENTER': 0x0D,
    'SHIFT': 0x10,
    'CTRL': 0x11,
    'ALT': 0x12,
    'PAUSE': 0x13,
    'CAPSLOCK': 0x14,
    'ESC': 0x1B,
    'SPACE': 0x20,
    'PAGEUP': 0x21,
    'PAGEDOWN': 0x22,
    'END': 0x23,
    'HOME': 0x24,
    'LEFT': 0x25,
    'UP': 0x26,
    'RIGHT': 0x27,
    'DOWN': 0x28,
    'INSERT': 0x2D,
    'DELETE': 0x2E,
}

# Keys that require extended flag
EXTENDED_KEYS = {'LEFT', 'RIGHT', 'UP', 'DOWN', 'INSERT', 'DELETE', 'HOME', 'END', 'PAGEUP', 'PAGEDOWN'}

# Ctypes structures
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
    )

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
    )

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD),
    )

class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = (
            ('ki', KEYBDINPUT),
            ('mi', MOUSEINPUT),
            ('hi', HARDWAREINPUT),
        )
    _anonymous_ = ('u',)
    _fields_ = (
        ('type', wintypes.DWORD),
        ('u', _INPUT_UNION),
    )

LPINPUT = ctypes.POINTER(INPUT)

# Function prototypes (only on Windows)
if IS_WINDOWS:
    user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)
    user32.SendInput.restype = wintypes.UINT
    user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)
    user32.MapVirtualKeyW.restype = wintypes.UINT


def _vk_from_str(key: str) -> int:
    k = key.strip().upper()
    if len(k) == 1:
        c = ord(k)
        # digits 0-9
        if 0x30 <= c <= 0x39:
            return c
        # letters A-Z
        if 0x41 <= c <= 0x5A:
            return c
    if k.startswith('F') and k[1:].isdigit():
        n = int(k[1:])
        if 1 <= n <= 24:
            return 0x70 + (n - 1)
    if k in VK:
        return VK[k]
    raise ValueError(f'Unsupported key: {key}')


def _scancode_from_vk(vk: int) -> int:
    sc = user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    return int(sc)


def _send_key_scancode(scancode: int, keyup: bool = False, extended: bool = False):
    flags = KEYEVENTF_SCANCODE
    if keyup:
        flags |= KEYEVENTF_KEYUP
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None))
    sent = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    if sent != 1:
        if IS_WINDOWS:
            raise ctypes.WinError(ctypes.get_last_error())
        else:
            raise RuntimeError(f"Failed to send keyboard input (scancode={scancode})")



def key_down(key: str):
    vk = _vk_from_str(key)
    sc = _scancode_from_vk(vk)
    extended = key.strip().upper() in EXTENDED_KEYS
    _send_key_scancode(sc, keyup=False, extended=extended)


def key_up(key: str):
    vk = _vk_from_str(key)
    sc = _scancode_from_vk(vk)
    extended = key.strip().upper() in EXTENDED_KEYS
    _send_key_scancode(sc, keyup=True, extended=extended)


def tap(key: str, press_ms: int = 50):
    key_down(key)
    time.sleep(max(press_ms, 1) / 1000.0)
    key_up(key)


__all__ = ['key_down', 'key_up', 'tap', 'IS_WINDOWS']
