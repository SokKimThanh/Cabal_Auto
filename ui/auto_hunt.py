import json
import time
from pathlib import Path

import pyautogui

from lib.system.win_input import tap
from lib.system.hunt_logger import get_hunt_logger
from lib.vision.template_matcher import locate_template
from lib.features.skills.runtime import SkillRuntime

# CONFIG_PATH points to lib/data/ for centralized data management
CONFIG_PATH = Path(__file__).parent.parent / 'lib' / 'data' / 'hunt_config.json'


def load_cfg():
    """Load hunt config with Phase 3 migration support."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # Phase 3: Backward compatibility migration
    if 'monster_selected_name' in cfg and cfg['monster_selected_name']:
        if not cfg.get('monster_list'):
            cfg['monster_list'] = [{"name": cfg['monster_selected_name'], "priority": 1, "enabled": True}]
    
    # Ensure Phase 3 fields exist
    cfg.setdefault('monster_list', [])
    cfg.setdefault('rotation_mode', 'sequence')
    cfg.setdefault('current_monster_index', 0)
    
    return cfg


def get_monster_rotation_targets(cfg):
    """
    Phase 3: Get list of monsters to hunt based on rotation_mode.
    
    Returns:
        list of monster dicts sorted by rotation order:
        - sequence mode: order as they appear in monster_list
        - priority mode: sorted by priority (ascending)
        
    Each monster dict contains:
        {'name': str, 'priority': int, 'templates': [template_dict, ...]}
    """
    monster_list = cfg.get('monster_list', [])
    enabled_monsters = [m for m in monster_list if m.get('enabled', True)]
    
    if not enabled_monsters:
        return []
    
    rotation_mode = cfg.get('rotation_mode', 'sequence')
    
    # Build monster objects with their templates
    all_templates = cfg.get('templates', [])
    result = []
    
    for monster in enabled_monsters:
        name = monster.get('name', '')
        priority = monster.get('priority', 1)
        
        # Find templates for this monster (fuzzy case-insensitive matching)
        # Remove special chars for better matching: "Coc go~" → "coc go"
        import re
        name_clean = re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()
        
        monster_templates = []
        for t in all_templates:
            tmpl_name = t.get('name', '')
            tmpl_clean = re.sub(r'[^a-z0-9\s]', '', tmpl_name.lower()).strip()
            
            # Match if cleaned names overlap significantly
            if name_clean in tmpl_clean or tmpl_clean in name_clean or \
               tmpl_clean.startswith(name_clean) or name_clean.startswith(tmpl_clean):
                monster_templates.append(t)
        
        if monster_templates:
            result.append({
                'name': name,
                'priority': priority,
                'templates': monster_templates
            })
    
    # Sort based on rotation mode
    if rotation_mode == 'priority':
        result.sort(key=lambda m: m['priority'])
    
    return result


def locate_target(cfg):
    """
    Try to locate the target frame on screen using templates[] or fallback to template_path.
    Uses template_matcher.locate_template() for accurate confidence tracking with OpenCV.
    
    Returns a tuple (box, template_info) or (None, None).
    box: (left, top, width, height) or None
    template_info: {'name': ..., 'path': ..., 'threshold': ..., 'confidence': ...} or None
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
            
            # Use template_matcher for accurate confidence tracking
            box, confidence = locate_template(path, region, threshold, method='auto')
            if box:
                return box, {
                    'name': tmpl.get('name', ''), 
                    'path': path, 
                    'threshold': threshold,
                    'confidence': confidence
                }
        
        # No match found in templates
        return None, None
    
    # Fallback to legacy template_path
    region_list = cfg.get('region')  # [left, top, width, height] or None
    region = tuple(region_list) if region_list else None
    template = cfg.get('template_path')
    threshold = cfg.get('confidence', 0.8)

    if not template or not Path(template).exists():
        return None, None

    # Use template_matcher for accurate confidence tracking
    box, confidence = locate_template(template, region, threshold, method='auto')
    return (box, {'path': template, 'threshold': threshold, 'confidence': confidence}) if box else (None, None)


def locate_monster_target(monster_targets, window_bounds=None):
    """
    Phase 3: Try to locate any monster from the rotation list.
    
    Args:
        monster_targets: list of monster dicts from get_monster_rotation_targets()
        window_bounds: optional window bounds dict for region
        
    Returns:
        (box, template_info, monster_name) or (None, None, None)
    """
    for monster in monster_targets:
        monster_name = monster['name']
        templates = monster['templates']
        
        for tmpl in templates:
            path = tmpl.get('path', '')
            if not path or not Path(path).exists():
                continue
            
            threshold = tmpl.get('threshold', 0.85)
            
            # Determine region
            region_strategy = tmpl.get('region_strategy', 'window')
            if region_strategy == 'custom' and tmpl.get('region'):
                reg_dict = tmpl['region']
                region = (reg_dict.get('left', 0), reg_dict.get('top', 0), 
                         reg_dict.get('width', 0), reg_dict.get('height', 0))
            elif window_bounds:
                region = (window_bounds.get('left', 0), window_bounds.get('top', 0), 
                         window_bounds.get('width', 0), window_bounds.get('height', 0))
            else:
                region = None
            
            # Try to locate
            box, confidence = locate_template(path, region, threshold, method='auto')
            if box:
                return box, {
                    'name': tmpl.get('name', ''),
                    'path': path,
                    'threshold': threshold,
                    'confidence': confidence,
                    'monster_name': monster_name
                }, monster_name
    
    return None, None, None


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

    target_key = cfg.get('target_key', 'z')
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

    # Initialize skill runtime if skills.json exists (centralized in lib/data/)
    skill_runtime = None
    skills_path = Path(__file__).parent.parent / 'lib' / 'data' / 'skills.json'
    if skills_path.exists():
        try:
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_data = json.load(f)
            skill_runtime = SkillRuntime(skills_data)
            print(f'Skill runtime initialized: {len(skill_runtime.attack_skills)} attacks, {len(skill_runtime.buff_skills)} buffs')
        except Exception as e:
            print(f'Warning: Could not load skill runtime: {e}')

    # Phase 3: Initialize monster rotation
    monster_targets = get_monster_rotation_targets(cfg)
    rotation_mode = cfg.get('rotation_mode', 'sequence')
    current_monster_index = cfg.get('current_monster_index', 0)
    window_bounds = cfg.get('window_bounds')
    
    use_rotation = len(monster_targets) > 0
    if use_rotation:
        print(f'Monster rotation enabled: {rotation_mode} mode, {len(monster_targets)} monsters')
        for idx, monster in enumerate(monster_targets):
            prefix = "→" if idx == current_monster_index and rotation_mode == 'sequence' else " "
            print(f'  {prefix} [{idx+1}] {monster["name"]} (P{monster["priority"]}) - {len(monster["templates"])} templates')
    else:
        print('Monster rotation disabled - using legacy template mode')

    # Initialize logger
    logger = get_hunt_logger()
    logger.log_hunt_start(cfg)

    print('Auto Hunt started')
    if not use_rotation:
        print(f'Template: {template_path}')
    print('Press Ctrl+C to stop')

    last_search = 0.0
    have_target = False
    last_match_info = None
    last_monster_name = None
    state = 'search'  # Track state for logging
    attack_start_time = None
    lost_timeout_sec = float(cfg.get('lost_timeout_sec', 1.2))
    attack_min_duration_sec = float(cfg.get('attack_min_duration_sec', 1.5))
    time_target_lost = None  # Track when we lost the target

    try:
        while True:
            now = time.time()
            if now - last_search >= search_interval:
                # Phase 3: Use monster rotation if available
                if use_rotation:
                    # Determine which monsters to try
                    if rotation_mode == 'sequence':
                        # Try current monster, then cycle to next if not found
                        search_order = [monster_targets[current_monster_index % len(monster_targets)]]
                    else:  # priority mode
                        # Try all monsters in priority order
                        search_order = monster_targets
                    
                    box, match_info, monster_name = locate_monster_target(search_order, window_bounds)
                    
                    # If found, update current monster index for sequence mode
                    if box and rotation_mode == 'sequence':
                        # Check if this is a different monster than expected
                        if monster_name != last_monster_name:
                            # Find index of this monster
                            for idx, m in enumerate(monster_targets):
                                if m['name'] == monster_name:
                                    current_monster_index = idx
                                    break
                else:
                    # Legacy mode: use locate_target
                    box, match_info = locate_target(cfg)
                    monster_name = None
                
                have_target = box is not None
                last_search = now
                
                # Log template match details
                if have_target and match_info:
                    # Target found - clear lost timer
                    time_target_lost = None
                    
                    if last_match_info != match_info:
                        # State transition: search -> attack
                        if state == 'search':
                            logger.log_state_change('search', 'attack', 'target_found')
                            state = 'attack'
                            attack_start_time = now
                        
                        # Log the match with accurate confidence from template_matcher
                        template_name = match_info.get('name') or match_info.get('path', 'unknown')
                        threshold = match_info.get('threshold', 0.8)
                        confidence = match_info.get('confidence', 0.0)
                        log_monster_name = match_info.get('monster_name', monster_name or '')
                        logger.log_match(template_name, box, threshold, confidence, log_monster_name)
                        
                        rotation_info = f" [{rotation_mode}]" if use_rotation else ""
                        monster_info = f" Monster: {log_monster_name}" if log_monster_name else ""
                        print(f"[Match{rotation_info}]{monster_info} Template: {template_name}, " +
                              f"Threshold: {threshold:.2f}, Confidence: {confidence:.3f}, Box: {box}")
                        last_match_info = match_info
                        last_monster_name = monster_name
                elif not have_target:
                    # Target lost
                    if last_match_info and time_target_lost is None:
                        time_target_lost = now
                    
                    # Check if we should give up on this target
                    if time_target_lost and (now - time_target_lost >= lost_timeout_sec):
                        # State transition: attack -> search
                        if state == 'attack':
                            duration = now - attack_start_time if attack_start_time else 0
                            
                            # Only transition if we've been attacking long enough
                            if duration >= attack_min_duration_sec:
                                template_name = last_match_info.get('name') or last_match_info.get('path', 'unknown')
                                log_monster_name = last_match_info.get('monster_name', last_monster_name or '')
                                logger.log_lost(template_name, log_monster_name, duration)
                                logger.log_state_change('attack', 'search', 'target_lost')
                                state = 'search'
                                attack_start_time = None
                                
                                rotation_info = f" [{rotation_mode}]" if use_rotation else ""
                                monster_info = f" Monster: {log_monster_name}" if log_monster_name else ""
                                print(f"[Lost{rotation_info}]{monster_info} Target lost after {duration:.1f}s")
                                
                                # Phase 3: Rotate to next monster in sequence mode
                                if use_rotation and rotation_mode == 'sequence':
                                    current_monster_index = (current_monster_index + 1) % len(monster_targets)
                                    next_monster = monster_targets[current_monster_index]['name']
                                    print(f"[Rotation] Switching to: {next_monster} ({current_monster_index+1}/{len(monster_targets)})")
                                    
                                    # Save rotation state
                                    cfg['current_monster_index'] = current_monster_index
                                    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                                        json.dump(cfg, f, ensure_ascii=False, indent=2)
                            
                        last_match_info = None
                        last_monster_name = None
                        time_target_lost = None

            # Cast buff skills (always, regardless of combat state)
            if skill_runtime:
                buff_key = skill_runtime.get_buff_to_cast(now)
                if buff_key:
                    buff_info = skill_runtime.get_skill_info(buff_key)
                    hold_time = buff_info.get_hold_time_ms() if buff_info else attack_press_ms
                    tap(buff_key, hold_time)
                    skill_runtime.mark_cast(buff_key, now)
                    print(f"[Buff] Cast {buff_info.name if buff_info else buff_key}")

            if not have_target:
                # cycle target key to find next
                tap(target_key)
                time.sleep(target_cycle_delay)
                continue

            # We have a target, execute attack skills
            if skill_runtime:
                # Use skill runtime for intelligent attack rotation
                attack_key = skill_runtime.get_attack_to_cast(now)
                if attack_key:
                    attack_info = skill_runtime.get_skill_info(attack_key)
                    hold_time = attack_info.get_hold_time_ms() if attack_info else attack_press_ms
                    tap(attack_key, hold_time)
                    skill_runtime.mark_cast(attack_key, now)
                    time.sleep(attack_interval)
            else:
                # Fallback to legacy attack_keys sequence
                for k in attack_keys:
                    tap(k, attack_press_ms)
                    time.sleep(attack_interval)

            # Small delay before next search/attack cycle
            time.sleep(0.05)
    except KeyboardInterrupt:
        logger.log_hunt_stop('manual_stop')
        print('Auto Hunt stopped')
    except Exception as e:
        logger.log_error('hunt_main', f'Hunt error: {str(e)}', e)
        logger.log_hunt_stop('error')
        print(f'Error: {e}')
        raise


if __name__ == '__main__':
    main()
