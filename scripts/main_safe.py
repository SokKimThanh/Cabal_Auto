import json
import time
import threading
from pathlib import Path

import pyautogui
import keyboard

CONFIG_PATH = Path(__file__).with_name('config.json')


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    cfg = load_config()

    click_x = int(cfg.get('click', {}).get('x', 500))
    click_y = int(cfg.get('click', {}).get('y', 400))
    interval = float(cfg.get('click', {}).get('interval_sec', 2.0))

    toggle_key = cfg.get('hotkeys', {}).get('toggle', 'f8')
    exit_key = cfg.get('hotkeys', {}).get('exit', 'f9')
    pause_key = cfg.get('safety', {}).get('pause_key', 'f7')

    failsafe = bool(cfg.get('safety', {}).get('failsafe', True))

    pyautogui.FAILSAFE = failsafe

    print('Cabal Auto started')
    print(f'Click at: ({click_x}, {click_y}), every {interval}s')
    print(f'Hotkeys: toggle={toggle_key}, pause={pause_key}, exit={exit_key}')
    print('Move mouse to top-left corner to trigger FAILSAFE (if enabled).')

    running = {"value": False}
    paused = {"value": False}
    stop = {"value": False}

    def toggle_run():
        running["value"] = not running["value"]
        print(f"[STATE] running={running['value']}")

    def toggle_pause():
        paused["value"] = not paused["value"]
        print(f"[STATE] paused={paused['value']}")

    def request_exit():
        stop["value"] = True
        print('[STATE] exit requested')

    keyboard.add_hotkey(toggle_key, toggle_run)
    keyboard.add_hotkey(pause_key, toggle_pause)
    keyboard.add_hotkey(exit_key, request_exit)

    def worker():
        while not stop["value"]:
            if running["value"] and not paused["value"]:
                try:
                    pyautogui.click(x=click_x, y=click_y)
                except pyautogui.FailSafeException:
                    print('[FAILSAFE] Triggered. Stopping...')
                    stop["value"] = True
                    break
                except Exception as e:
                    print(f'[ERROR] {e!r}')
            time.sleep(interval)

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    try:
        while not stop["value"]:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt: exiting...')
    finally:
        stop["value"] = True
        t.join(timeout=1.0)
        print('Cabal Auto stopped')


if __name__ == '__main__':
    main()
