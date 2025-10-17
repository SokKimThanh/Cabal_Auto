import json
import time
from pathlib import Path

import pyautogui

from win_input import tap
from hunt_logger import get_hunt_logger

CONFIG_PATH = Path(__file__).with_name('hunt_config.json')


def load_cfg():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def locate_target(cfg):
    """
    Try to locate the target frame on screen using templates[] or fallback to template_path.
    Returns a tuple (box, template_info) or (None, None).
    box: (left, top, width, height) or None
    template_info: {'name': ..., 'path': ..., 'threshold': ...} or None
    
    Note: Without OpenCV, confidence will be ignored and fallback locate is used.
    """
    # Try new templates[] array first
    templates = cfg.get('templates', [])
    if templates:
        window_bounds = cfg.get('window_bounds')  # fallback region from monster
        for tmpl in templates:
            path = tmpl.get('path', '')
            if not path or not Path(path).exists():
                continue
            
            threshold = tmpl.get('threshold', 0.85)
            grayscale = tmpl.get('grayscale', True)
            
            # Determine region: use template's region if custom, else window_bounds
            region_strategy = tmpl.get('region_strategy', 'window')
            if region_strategy == 'custom' and tmpl.get('region'):
                reg_dict = tmpl['region']
                region = (reg_dict.get('left', 0), reg_dict.get('top', 0), 
                         reg_dict.get('width', 0), reg_dict.get('height', 0))
            elif window_bounds:
                wb = window_bounds
                region = (wb.get('left', 0), wb.get('top', 0), 
                         wb.get('width', 0), wb.get('height', 0))
            else:
                region = None
            
            box = _try_locate_image(path, region, grayscale, threshold)
            if box:
                return box, {'name': tmpl.get('name', ''), 'path': path, 'threshold': threshold}
        
        # No match found in templates
        return None, None
    
    # Fallback to legacy template_path
    region = cfg.get('region')  # [left, top, width, height] or None
    template = cfg.get('template_path')
    grayscale = bool(cfg.get('grayscale', True))
    confidence = cfg.get('confidence', None)

    if not template or not Path(template).exists():
        return None, None

    box = _try_locate_image(template, region, grayscale, confidence)
    return box, {'path': template, 'threshold': confidence} if box else (None, None)


def _try_locate_image(template_path, region, grayscale, confidence):
    """
    Helper to locate a single image on screen.
    Returns box (left, top, width, height) or None.
    """
    try:
        # If OpenCV installed, use confidence
        if hasattr(pyautogui, 'locateOnScreen'):
            if region:
                box = pyautogui.locateOnScreen(template_path, region=tuple(region), grayscale=grayscale, confidence=confidence)
            else:
                box = pyautogui.locateOnScreen(template_path, grayscale=grayscale, confidence=confidence)
            return box
    except TypeError:
        # confidence not supported without opencv; retry without it
        try:
            if region:
                box = pyautogui.locateOnScreen(template_path, region=tuple(region), grayscale=grayscale)
            else:
                box = pyautogui.locateOnScreen(template_path, grayscale=grayscale)
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

    # Initialize logger
    logger = get_hunt_logger()
    logger.log_hunt_start(cfg)

    print('Auto Hunt started')
    print(f'Template: {template_path}')
    print('Press Ctrl+C to stop')

    last_search = 0.0
    have_target = False
    last_match_info = None
    state = 'search'  # Track state for logging
    attack_start_time = None

    try:
        while True:
            now = time.time()
            if now - last_search >= search_interval:
                box, match_info = locate_target(cfg)
                have_target = box is not None
                last_search = now
                
                # Log template match details
                if have_target and match_info:
                    if last_match_info != match_info:
                        # State transition: search -> attack
                        if state == 'search':
                            logger.log_state_change('search', 'attack', 'target_found')
                            state = 'attack'
                            attack_start_time = now
                        
                        # Log the match
                        template_name = match_info.get('name') or match_info.get('path', 'unknown')
                        threshold = match_info.get('threshold', 0.8)
                        confidence = match_info.get('confidence', 0.0)
                        monster_name = match_info.get('monster_name', '')
                        logger.log_match(template_name, box, threshold, confidence, monster_name)
                        
                        print(f"[Match] Template: {template_name}, " +
                              f"Threshold: {threshold}, Box: {box}")
                        last_match_info = match_info
                elif not have_target and last_match_info:
                    # State transition: attack -> search
                    if state == 'attack':
                        duration = now - attack_start_time if attack_start_time else 0
                        template_name = last_match_info.get('name') or last_match_info.get('path', 'unknown')
                        monster_name = last_match_info.get('monster_name', '')
                        logger.log_lost(template_name, monster_name, duration)
                        logger.log_state_change('attack', 'search', 'target_lost')
                        state = 'search'
                        attack_start_time = None
                    
                    print("[Lost] Target lost")
                    last_match_info = None

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
        logger.log_hunt_stop('manual_stop')
        print('Auto Hunt stopped')
    except Exception as e:
        logger.log_error(f'Hunt error: {str(e)}')
        logger.log_hunt_stop('error')
        print(f'Error: {e}')
        raise


if __name__ == '__main__':
    main()
