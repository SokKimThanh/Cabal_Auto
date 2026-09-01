import time
from tkinter import messagebox

from lib.features.hunt.hunt_config import save_hunt_config

try:
    import keyboard  # type: ignore
except ImportError:
    keyboard = None  # type: ignore


class AppLifecycleController:
    """Coordinates application startup and shutdown lifecycles."""

    def __init__(self, app):
        self.app = app

    def start_lifecycle(self) -> None:
        """Schedules initial startup checks in a sequence."""
        self.app.after(100, self._step_update_hotkeys)

    def _step_update_hotkeys(self):
        if hasattr(self.app, "_update_hotkeys_state"):
            self.app._update_hotkeys_state()
        self.app.after(50, self._step_diagnostics)

    def _step_diagnostics(self):
        if hasattr(self.app, "_update_hotkey_diagnostics_ui"):
            self.app._update_hotkey_diagnostics_ui()
        self.app.after(50, self._step_db_connection)

    def _step_db_connection(self):
        self.check_db_connection()
        self.app.after(200, self._step_first_time_setup)

    def _step_first_time_setup(self):
        self.check_first_time_setup()
        self.app.after(500, self.auto_bring_to_front_on_startup)

    def check_first_time_setup(self) -> None:
        """Check if this is first-time user and auto-launch wizard if needed."""
        # Check if user has completed basic setup
        # Must have ALL THREE to be considered configured
        window_title = self.app.hunt_cfg.get("window_title", "")
        has_window = bool(window_title.strip() if isinstance(window_title, str) else window_title)

        # Phase 3 compatibility: Check both legacy and new monster fields
        monster_selected_name = self.app.hunt_cfg.get("monster_selected_name", "")
        has_monster_legacy = bool(monster_selected_name.strip() if isinstance(monster_selected_name, str) else monster_selected_name)

        has_monster_list = (
            bool(self.app.hunt_cfg.get("monster_list"))
            and len(self.app.hunt_cfg.get("monster_list", [])) > 0
        )
        has_monster = has_monster_legacy or has_monster_list

        has_skills = (
            bool(self.app.hunt_cfg.get("skill_slots"))
            and len(self.app.hunt_cfg.get("skill_slots", [])) > 0
        )

        is_new_user = not (has_window and has_monster and has_skills)

        # Debug log to understand detection
        print(
            f"[First-time check] window={has_window}, monster={has_monster}, skills={has_skills}, is_new={is_new_user}"
        )

        # Track user response for persistence logic
        user_skipped_wizard = False

        if is_new_user:
            print("[First-time check] Showing messagebox to ask user...")

            # Force main window to front before showing messagebox
            self.app.lift()
            self.app.focus_force()
            self.app.attributes("-topmost", True)
            self.app.update()

            # Ask user if they want to run setup wizard
            response = messagebox.askyesno(
                self.app._t("wizard_first_time_title"),
                self.app._t("wizard_first_time_message"),
                icon="question",
                parent=self.app,  # Ensure messagebox is child of main window
            )

            # Disable topmost after messagebox
            self.app.attributes("-topmost", False)

            print(f"[First-time check] User response: {response}")

            if response:
                # User clicked Yes - launch wizard
                print("[First-time check] Launching wizard...")
                self.app.window_controller.on_setup_wizard()
            else:
                # User clicked No - auto-detect Cabal window and save
                print(
                    "[First-time check] User skipped wizard - attempting auto PID detection..."
                )
                if hasattr(self.app, "_auto_detect_and_save_cabal_window"):
                    self.app._auto_detect_and_save_cabal_window()
                if hasattr(self.app, "hunt_status"):
                    self.app.hunt_status.set(self.app._t("wizard_skipped_hint"))
                user_skipped_wizard = True

        # Check PIL availability and show one-time warning if missing
        if not getattr(self.app, "pil_available", True) and not getattr(self.app, "_is_destroyed", False):

            print("[PIL Check] PIL/Pillow not available - showing install instructions")

            try:

                messagebox.showinfo(

                    self.app._t("info_title"),

                    self.app._t("pil_not_installed_message"),

                    parent=self.app

                )

            except Exception:

                pass
        print("[First-time check] Check completed, global hotkeys now fully active")

        # ✅ Sprint 24 Enhancement: Persist wizard completion state
        # Save to config to avoid re-showing wizard on next launch
        if user_skipped_wizard:
            # User skipped wizard - mark as configured to prevent re-prompt
            try:
                self.app.hunt_cfg["is_configured"] = True
                save_hunt_config(self.app.hunt_cfg)
                print(
                    "[First-time check] Saved is_configured=True to prevent wizard re-prompt"
                )
            except Exception as e:
                print(f"[First-time check] Failed to save is_configured state: {e}")

    def auto_bring_to_front_on_startup(self) -> None:
        """Auto bring saved Cabal window to front BELOW app on startup."""
        try:
            # Check if we have a valid hunt_selected window
            if not hasattr(self.app, "hunt_selected") or not self.app.hunt_selected:
                print("[Auto Bring] No saved window to bring to front")
                # Ensure app deiconifies even if there's no window to bring to front
                if hasattr(self.app, "deiconify"):
                    self.app.deiconify()
                return

            hwnd = self.app.hunt_selected.get("hwnd")
            title = self.app.hunt_selected.get("title", "")
            pid = self.app.hunt_selected.get("pid", "")

            if not hwnd:
                print(f"[Auto Bring] No HWND for window: {title}")
                if hasattr(self.app, "deiconify"):
                    self.app.deiconify()
                return

            print(
                f"[Auto Bring] Bringing window to front (below app): {title} [PID:{pid}]"
            )

            # Bring window to front
            ok = False
            if hasattr(self.app, "_bring_window_to_front_by_hwnd"):
                ok = self.app._bring_window_to_front_by_hwnd(hwnd)

            if ok:
                # Keep app on top of game window
                def _lift_and_focus():
                    self.app.lift()
                    self.app.focus_force()
                    self.app.attributes("-topmost", True)
                    self.app.update_idletasks()
                    self.app.after(100, lambda: self.app.attributes("-topmost", False))

                self.app.after(100, _lift_and_focus)

                print(f"[Auto Bring] ✓ Window ready (below app): {title}")
                # Update status briefly
                if hasattr(self.app, "hunt_status"):
                    current_status = self.app.hunt_status.get()
                    self.app.hunt_status.set(f"✓ Game window ready: {title}")
                    # Restore previous status after 3 seconds
                    self.app.after(3000, lambda: self.app.hunt_status.set(current_status))
            else:
                print(f"[Auto Bring] ✗ Failed to bring window to front: {title}")

            # Run startup auto scan via controller
            if hasattr(self.app, "scan_controller"):
                self.app.scan_controller.run_scan(manual=False)

        except Exception as e:
            print(f"[Auto Bring] Error: {e}")

    def check_db_connection(self) -> None:
        """Kiểm tra tình trạng CSDL khi khởi động và cập nhật thanh trạng thái."""
        try:
            from database import check_db_health, init_database

            # Đảm bảo schema + seed đã được khởi tạo
            try:
                init_database()
            except Exception as init_err:
                print(f"[DB] init_database error (non-fatal): {init_err}")

            result = check_db_health()

            if result.get("ok"):
                counts = result.get("counts", {})
                msg = (
                    f"✅ CSDL sẵn sàng"
                    f" | Quái: {counts.get('monsters', 0)}"
                    f" | Phụ bản: {counts.get('dungeons', 0)}"
                    f" | Loại quái: {counts.get('monster_type', 0)}"
                )
                if hasattr(self.app, "_set_db_status"):
                    self.app._set_db_status(msg, ok=True)
                print(f"[DB] {msg}")
            else:
                missing = result.get("missing_tables", [])
                missing_str = ", ".join(missing)
                bar_msg = f"⚠️ CSDL chưa hoàn chỉnh: Thiếu bảng {missing_str}"
                if result.get("error"):
                    bar_msg = f"❌ {result['error']}"
                if hasattr(self.app, "_set_db_status"):
                    self.app._set_db_status(bar_msg, ok=False)
                print(f"[DB] {bar_msg}")

                detail = (
                    f"CSDL monsters.db chưa hoàn chỉnh!\n\n"
                    f"Các bảng bị thiếu:\n• " + "\n• ".join(missing)
                )
                if result.get("error"):
                    detail = f"Lỗi kết nối CSDL:\n{result['error']}"
                messagebox.showwarning("⚠️ Cảnh báo CSDL", detail)

        except ImportError:
            msg = "⚠️ Không thể import module database"
            if hasattr(self.app, "_set_db_status"):
                self.app._set_db_status(msg, ok=False)
            print(f"[DB] {msg}")
        except Exception as exc:
            msg = f"❌ Lỗi kiểm tra CSDL: {exc}"
            if hasattr(self.app, "_set_db_status"):
                self.app._set_db_status(msg, ok=False)
            print(f"[DB] {msg}")

    def on_close(self) -> None:
        """Handles high-level close orchestration (abort checks, thread joining)."""
        if hasattr(self.app, "try_close_setup_wizard") and not self.app.try_close_setup_wizard():
            return
        if hasattr(self.app, "try_close_library_manager") and not self.app.try_close_library_manager():
            return

        self.app.hunt_running = False
        if getattr(self.app, "hunt_thread", None) is not None:
            try:
                self.app.hunt_thread.join(timeout=1.0)
            except Exception:
                pass

        for attr_name in ("monster_manager_win", "skill_manager_win"):
            win = getattr(self.app, attr_name, None)
            if win is not None:
                try:
                    win.destroy()
                except Exception:
                    pass
                setattr(self.app, attr_name, None)

        self.app.destroy()

    def cleanup_before_destroy(self) -> None:
        """Centralized cleanup of external resources (bot manager, overlay, hotkeys)."""
        try:
            if getattr(self.app, "_overlay_controller", None) is not None:
                self.app._overlay_controller.stop()
                self.app._overlay_controller = None
                print("[MonsterTracking] OverlayController cleaned up")

            if getattr(self.app, "_bot_manager", None) is not None:
                self.app._bot_manager.destroy()
                self.app._bot_manager = None
                print("[MonsterTracking] BotManager cleaned up")
        except Exception as e:
            print(f"[MonsterTracking] Error during cleanup: {e}")

        if hasattr(self.app, "_stop_overlay_window_tracker"):
            try:
                self.app._stop_overlay_window_tracker()
            except Exception:
                pass

        # Unregister global hotkeys on exit
        if keyboard is not None and hasattr(self.app, "_registered_hotkey_handlers"):
            for hk, handler in list(self.app._registered_hotkey_handlers.items()):
                try:
                    # keyboard.remove_hotkey accepts either the hotkey string or the handler id/function
                    keyboard.remove_hotkey(handler)
                except Exception:
                    try:
                        keyboard.remove_hotkey(hk)
                    except Exception:
                        pass

        if hasattr(self.app, "_unregister_global_hotkeys"):
            try:
                self.app._unregister_global_hotkeys()
            except Exception:
                pass
