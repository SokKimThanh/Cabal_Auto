import re

with open("lib/features/hunt/hunt_orchestrator.py", "r") as f:
    content = f.read()

# Replace the search logic block:
# Look for:
# if now - last_search >= float(cfg.get("search_interval", 0.5)):
# ... until the end of that block

old_block = """                    # periodic detection with multi-template support
                    if now - last_search >= float(cfg.get("search_interval", 0.5)):
                        box, match_info = self.locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                            if match_info and last_match_info != match_info:
                                template_name = (
                                    match_info.get("name")
                                    or Path(match_info.get("path", "")).stem
                                )
                                threshold = match_info.get("threshold", 0.8)
                                confidence = match_info.get("confidence", 0.0)
                                monster_name = match_info.get("monster_name", "")
                                logger.log_match(
                                    template_name,
                                    box,
                                    threshold,
                                    confidence,
                                    monster_name,
                                )

                                status_msg = (
                                    f"Target: {template_name} (conf: {confidence:.3f})"
                                )
                                self.schedule_ui_task(lambda msg=status_msg: self.on_status_update(msg))
                                last_match_info = match_info
                        else:
                            have_target = False
                            if last_match_info:
                                duration = (
                                    now - attack_started if mode == "attack" else 0
                                )
                                template_name = (
                                    last_match_info.get("name")
                                    or Path(last_match_info.get("path", "")).stem
                                )
                                monster_name = last_match_info.get("monster_name", "")
                                logger.log_lost(template_name, monster_name, duration)

                                self.schedule_ui_task(lambda: self.on_state_change("running"))
                                last_match_info = None
                        last_search = now"""

new_block = """                    # Screen capture for this tick
                    frame = None
                    try:
                        if self.bot_manager and self.bot_manager.screen_capture:
                            if getattr(self.bot_manager.screen_capture, 'hwnd', None) != hunt_selected.get("hwnd"):
                                # Ensure we are capturing the right window
                                import win32gui
                                hwnd = int(hunt_selected.get("hwnd", 0))
                                if hwnd:
                                    title = win32gui.GetWindowText(hwnd)
                                    self.bot_manager.screen_capture.start(title)

                            frame = self.bot_manager.screen_capture.get_latest_frame()
                            if frame is not None:
                                frame = frame.copy() # return a copy to readers
                    except Exception as e:
                        logger.log_error("vision_capture", f"Failed to capture frame: {e}")

                    # Target detection logic using TargetBarDetector
                    if frame is not None:
                        is_alive = target_bar_detector.is_target_alive(frame)

                        if is_alive:
                            have_target = True
                            last_seen = now
                            consecutive_false_readings = 0
                        else:
                            consecutive_false_readings += 1
                            if consecutive_false_readings >= int(cfg.get("target_lost_debounce_frames", 3)):
                                have_target = False"""

content = content.replace(old_block, new_block)

# Replace target_key tap in mode == "search":
old_search_tap = """                        if not training_mode_active:
                            tap(cfg.get("target_key", "z"))
                            time.sleep(float(cfg.get("target_cycle_delay", 0.1)))
                        else:"""
new_search_tap = """                        if not training_mode_active:
                            tap(cfg.get("target_key", "z"))
                            time.sleep(float(cfg.get("search_tap_delay_sec", 0.08)))
                        else:"""
content = content.replace(old_search_tap, new_search_tap)

# Replace attack logic target_active condition and remove target_key tap
old_attack_logic = """                    # mode == 'attack'
                    if (
                        have_target
                        or (now - last_seen) <= lost_timeout
                        or (now - attack_started) <= attack_min_duration
                    ):
                        target_active = (
                            have_target
                            or (now - last_seen) <= lost_timeout
                            or (now - attack_started) <= attack_min_duration
                        )
                        if skill_runtime and has_attack_skills:
                            if target_active:
                                tap(
                                    cfg.get("target_key", "z")
                                )
                                time.sleep(0.05)"""
new_attack_logic = """                    # mode == 'attack'
                    if (
                        have_target
                        or (now - last_seen) <= lost_timeout
                    ):
                        target_active = (
                            have_target
                            or (now - last_seen) <= lost_timeout
                        )
                        if skill_runtime and has_attack_skills:
                            # DO NOT send target key in attack mode
                            # just call try_cast_skills"""
content = content.replace(old_attack_logic, new_attack_logic)


with open("lib/features/hunt/hunt_orchestrator.py", "w") as f:
    f.write(content)
