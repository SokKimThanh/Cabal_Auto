#!/usr/bin/env python3
"""Compare wizard window enumeration vs hunt controller enumeration"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s | %(message)s')

print("\n" + "="*70)
print("COMPARISON: Wizard vs Hunt Controller Window Enumeration")
print("="*70)

# Test 1: Wizard's _enum_windows
print("\n[1] WIZARD'S _enum_windows():")
print("-" * 70)

# Copy wizard's _enum_windows logic
import ctypes
import psutil
from ctypes import wintypes

user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
IsWindowVisible = user32.IsWindowVisible
GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowThreadProcessId = user32.GetWindowThreadProcessId

wizard_results = []

def callback(hwnd, lParam):
    try:
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if not title:
            return True

        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pid_val = int(pid.value)

        proc_name = None
        try:
            p = psutil.Process(pid_val)
            proc_name = p.name()
        except Exception:
            proc_name = None

        wizard_results.append({
            "hwnd": int(hwnd),
            "pid": pid_val,
            "title": title,
            "proc": proc_name,
        })
    except Exception:
        pass
    return True

try:
    EnumWindows(EnumWindowsProc(callback), 0)
except Exception:
    pass

print(f"Found {len(wizard_results)} total windows")
cabal_windows = [w for w in wizard_results if "cabal" in w["title"].lower() or (w.get("proc") and "cabal" in w["proc"].lower())]
print(f"Found {len(cabal_windows)} Cabal-related windows:\n")
for w in cabal_windows:
    print(f"  [OK] {w['title']:<50} [PID: {w['pid']:<5}] ({w.get('proc', 'Unknown')})")

# Test 2: Hunt controller's _list_windows
print("\n[2] HUNT CONTROLLER'S _list_windows():")
print("-" * 70)

from lib.system.window_manager import WindowManager

wm = WindowManager()
all_windows = wm.list_windows(visible_only=True)
print(f"WindowManager found {len(all_windows)} total visible windows")

from ui.controllers.app_window_controller import AppWindowController
import tkinter as tk

root = tk.Tk()
controller = AppWindowController(root)

hunt_results = controller._list_windows()
print(f"Hunt _list_windows() returned {len(hunt_results)} Cabal windows:\n")
for w in hunt_results:
    print(f"  [OK] {w['title']:<50} [PID: {w['pid']:<5}] ({w.get('proc', 'Unknown')})")

# Test 3: Compare
print("\n[3] COMPARISON:")
print("-" * 70)

wizard_cabal = {w['hwnd']: w for w in cabal_windows}
hunt_cabal = {w['hwnd']: w for w in hunt_results}

print(f"Wizard found: {len(wizard_cabal)} Cabal windows")
print(f"Hunt found:   {len(hunt_cabal)} Cabal windows")

print(f"\nIn wizard but NOT in hunt:")
for hwnd in wizard_cabal:
    if hwnd not in hunt_cabal:
        w = wizard_cabal[hwnd]
        print(f"  [MISSING] {w['title']:<50} [PID: {w['pid']:<5}] ({w.get('proc')})")

print(f"\nIn hunt but NOT in wizard:")
for hwnd in hunt_cabal:
    if hwnd not in wizard_cabal:
        w = hunt_cabal[hwnd]
        print(f"  [EXTRA] {w['title']:<50} [PID: {w['pid']:<5}] ({w.get('proc')})")

root.destroy()
print("\n" + "="*70)
