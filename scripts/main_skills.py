import json
import time
import threading
from pathlib import Path

import keyboard
from win_input import tap

CONFIG_SKILLS = Path(__file__).with_name('skills.json')


def load_skills():
    if not CONFIG_SKILLS.exists():
        raise FileNotFoundError('Missing skills.json')
    with open(CONFIG_SKILLS, 'r', encoding='utf-8') as f:
        data = json.load(f)
    skills = []
    for item in data:
        if not item.get('enabled', True):
            continue
        name = str(item.get('name', 'Unnamed'))
        key = str(item.get('key', '1'))
        cooldown = float(item.get('cooldown_sec', 2.0))
        press_ms = int(item.get('press_ms', 60))
        skills.append({
            'name': name,
            'key': key,
            'cooldown': cooldown,
            'press_ms': press_ms,
            'next_at': 0.0,
        })
    return skills


def run_loop(stop_flag):
    skills = load_skills()
    print('Loaded skills:')
    for s in skills:
        print(f" - {s['name']} ({s['key']}), cd={s['cooldown']}s")
    if not skills:
        print('No enabled skills. Enable some in skills.json')
        return

    while not stop_flag['value']:
        now = time.time()
        for s in skills:
            if now >= s['next_at']:
                try:
                    tap(s['key'], s['press_ms'])
                except Exception as e:
                    print(f"[ERROR] sending key {s['key']}: {e!r}")
                s['next_at'] = now + s['cooldown']
        time.sleep(0.01)


def main():
    stop = {'value': False}

    def toggle_run():
        # Not used in this simple loop; you can add pause if needed
        pass

    def request_exit():
        stop['value'] = True
        print('Exit requested')

    keyboard.add_hotkey('f8', toggle_run)
    keyboard.add_hotkey('f9', request_exit)

    t = threading.Thread(target=run_loop, args=(stop,), daemon=True)
    t.start()

    try:
        while not stop['value']:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt: exiting...')
    finally:
        stop['value'] = True
        t.join(timeout=1.0)


if __name__ == '__main__':
    main()
