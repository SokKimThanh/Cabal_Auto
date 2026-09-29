import time
import tkinter as tk

class UIAnimationManager:
    """
    Singleton manager to handle UI animations (tweens) in a centralized loop,
    avoiding multiple .after() loops that cause resource contention.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIAnimationManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        self.tweens = {}
        self._loop_running = False
        self._root = None

    def register_tween(self, target_id: str, widget, start_val, end_val, duration_ms, update_func):
        """
        Registers or overrides a tween. If the target_id is already running,
        it starts the new tween from the current_val to prevent backward jumping.
        """
        if target_id in self.tweens:
            actual_start = self.tweens[target_id]['current_val']
        else:
            actual_start = start_val

        self.tweens[target_id] = {
            'widget': widget,
            'start_val': actual_start,
            'end_val': end_val,
            'duration_ms': duration_ms,
            'update_func': update_func,
            'start_time': time.time(),
            'current_val': actual_start
        }

        if not self._loop_running:
            # Ensure we have a valid root for .after()
            try:
                if not self._root or not self._root.winfo_exists():
                    self._root = widget
            except (tk.TclError, AttributeError):
                self._root = widget

            self._loop_running = True
            self._run_loop()

    def cancel_tween(self, target_id: str):
        if target_id in self.tweens:
            del self.tweens[target_id]

    def _run_loop(self):
        if not self._loop_running:
            return

        now = time.time()
        to_delete = []

        for target_id, tween in list(self.tweens.items()):
            widget = tween['widget']
            try:
                if not widget.winfo_exists():
                    to_delete.append(target_id)
                    continue
            except (tk.TclError, AttributeError):
                to_delete.append(target_id)
                continue

            elapsed = now - tween['start_time']
            duration = tween['duration_ms'] / 1000.0

            if duration <= 0 or elapsed >= duration:
                tween['current_val'] = tween['end_val']
                try:
                    tween['update_func'](tween['end_val'])
                except Exception:
                    pass
                to_delete.append(target_id)
            else:
                progress = elapsed / duration
                current_val = tween['start_val'] + (tween['end_val'] - tween['start_val']) * progress
                tween['current_val'] = current_val
                try:
                    tween['update_func'](current_val)
                except Exception:
                    # If update_func fails, cancel the tween
                    to_delete.append(target_id)

        for target_id in to_delete:
            if target_id in self.tweens:
                del self.tweens[target_id]

        if self.tweens:
            valid_widget = None
            try:
                if self._root and self._root.winfo_exists():
                    valid_widget = self._root
            except (tk.TclError, AttributeError):
                pass

            if not valid_widget:
                for tween in self.tweens.values():
                    try:
                        if tween['widget'].winfo_exists():
                            valid_widget = tween['widget']
                            self._root = valid_widget
                            break
                    except (tk.TclError, AttributeError):
                        pass

            if valid_widget:
                valid_widget.after(16, self._run_loop)
            else:
                self._loop_running = False
        else:
            self._loop_running = False

    @classmethod
    def reset_instance(cls):
        """For testing purposes."""
        if cls._instance:
            cls._instance._loop_running = False
            cls._instance = None
