import json
import time
from pathlib import Path

import pyautogui

from win_input import tap

CONFIG_PATH = Path(__file__).with_name('hunt_config.json')


def load_cfg():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def locate_target(cfg):
    """
    Try to locate the target frame on screen.
    Returns a box (left, top, width, height) or None.
    Note: Without OpenCV, confidence will be ignored and fallback locate is used.
    """
    region = cfg.get('region')  # [left, top, width, height] or None
    template = cfg.get('template_path')
    grayscale = bool(cfg.get('grayscale', True))

    if not template or not Path(template).exists():
        return None

    try:
        # If OpenCV installed, use confidence
        if hasattr(pyautogui, 'locateOnScreen'):
            if region:
                box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale, confidence=cfg.get('confidence', None))
            else:
                box = pyautogui.locateOnScreen(template, grayscale=grayscale, confidence=cfg.get('confidence', None))
            return box
    except TypeError:
        # confidence not supported without opencv; retry without it
        try:
            if region:
                box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale)
            else:
                box = pyautogui.locateOnScreen(template, grayscale=grayscale)
            return box
        except Exception:
            return None
    except Exception:
        return None

    return None


def bring_window_to_front(title_substring: str) -> bool:
    """Best-effort bring a window whose title contains substring to front using PyAutoGUI helper."""
    try:
        import pygetwindow as gw
    except Exception:
        return False

    wins = [w for w in gw.getAllTitles() if title_substring.lower() in w.lower()]
    if not wins:
        return False
    try:
        win = gw.getWindowsWithTitle(wins[0])[0]
        win.activate()
        return True
    except Exception:
        return False


def main():
    cfg = load_cfg()
    pyautogui.FAILSAFE = True

    target_key = cfg.get('target_key', 'TAB')
    attack_keys = cfg.get('attack_keys', ['1', '2'])
    attack_press_ms = int(cfg.get('attack_press_ms', 60))
    target_cycle_delay = float(cfg.get('target_cycle_delay', 0.2))
    search_interval = float(cfg.get('search_interval', 0.25))
    attack_interval = float(cfg.get('attack_interval', 0.15))
    template_path = cfg.get('template_path')
    bring_front = bool(cfg.get('bring_to_front_each_cycle', True))
    window_title = cfg.get('window_title', 'Cabal')

    if bring_front:
        bring_window_to_front(window_title)

    print('Auto Hunt started')
    print(f'Template: {template_path}')
    print('Press Ctrl+C to stop')

    last_search = 0.0
    have_target = False

    try:
        while True:
            now = time.time()
            if now - last_search >= search_interval:
                box = locate_target(cfg)
                have_target = box is not None
                last_search = now
                # Debug print minimal
                # print('target', have_target)

            if not have_target:
                # cycle target key to find next
                tap(target_key)
                time.sleep(target_cycle_delay)
                continue

            # We have a target, execute attack keys in sequence
            for k in attack_keys:
                tap(k, attack_press_ms)
                time.sleep(attack_interval)

            # Small delay before next search/attack cycle
            time.sleep(0.05)
    except KeyboardInterrupt:
        print('Auto Hunt stopped')


if __name__ == '__main__':
    main()
