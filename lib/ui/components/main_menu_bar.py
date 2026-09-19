import tkinter as tk
from lib.features.hunt.hunt_config import save_hunt_config
from lib.events.event_bus import EventBus, VisionScanRegionEvent, VisionAddTemplateEvent, VisionManageTemplatesEvent

class MainMenuBar(tk.Menu):
    """
    Main menu bar component for the application.
    Extracts the menu construction logic out of the app God Class.
    """

    def __init__(self, parent, app, state_controller, hotkey_controller, window_controller, overlay_controller):
        """
        Initialize the main menu bar.

        Args:
            parent: The parent Tk/Toplevel window.
            app: Reference to the main App class (used for lazy access to _t).
            state_controller: AppStateController instance.
            hotkey_controller: HotkeyController instance.
            window_controller: AppWindowController instance.
            overlay_controller: AppOverlayController instance.
        """
        super().__init__(parent)
        self.app = app
        self.state_controller = state_controller
        self.hotkey_controller = hotkey_controller
        self.window_controller = window_controller
        self.overlay_controller = overlay_controller
        self.lang = getattr(self.app, "lang", "vi")

        # Re-fetch translation helper
        self._t = getattr(self.app, "_t", lambda k, **kw: k)

        self._build_settings_menu()
        self._build_vision_menu()

    def _build_settings_menu(self):
        settings_menu = tk.Menu(self, tearoff=0)

        # BooleanVar reflects hunt_cfg setting
        gh_cfg = self.state_controller.hunt_cfg.get("global_hotkeys", {})
        self.state_controller.ui_vars['global_hotkeys_enabled_legacy'] = tk.BooleanVar(value=bool(gh_cfg.get("enabled", True)))

        def _on_toggle_global_hotkeys():
            enabled = bool(self.state_controller.get_ui_var('global_hotkeys_enabled_legacy'))
            # Persist setting
            self.state_controller.hunt_cfg.setdefault("global_hotkeys", {})["enabled"] = enabled
            try:
                save_hunt_config(self.state_controller.hunt_cfg)
            except Exception:
                pass
            # Apply immediately
            if enabled:
                print("[Hotkeys] User enabled global hotkeys via menu")
                try:
                    self.hotkey_controller.register_all()
                except Exception as e:
                    print(f"[Hotkeys] Error re-registering hotkeys: {e}")
            else:
                print("[Hotkeys] User disabled global hotkeys via menu")
                try:
                    self.hotkey_controller.unregister_all()
                except Exception as e:
                    print(f"[Hotkeys] Error unregistering hotkeys: {e}")

        settings_menu.add_checkbutton(
            label=self._t("help_shortcuts"),
            variable=self.state_controller.ui_vars['global_hotkeys_enabled_legacy'],
            command=_on_toggle_global_hotkeys,
        )
        settings_menu.add_separator()

        def _retry_hotkeys():
            print("[Hotkeys] User requested retry registration")
            try:
                self.hotkey_controller.register_all()
            except Exception as e:
                print(f"[Hotkeys] Retry failed: {e}")

        settings_menu.add_command(
            label="Retry global hotkeys", command=_retry_hotkeys
        )

        settings_menu.add_separator()

        def _toggle_top_bar():
            if hasattr(self.app, "_toggle_action_bar"):
                self.app._toggle_action_bar()

        toggle_label = "Toggle Action Bar" if self.lang == "en" else "Ẩn/Hiện Thanh Công Cụ (Action Bar)"
        settings_menu.add_command(
            label=toggle_label,
            command=_toggle_top_bar
        )
        self.add_cascade(label="Settings", menu=settings_menu)

    def _build_vision_menu(self):
        vision_menu = tk.Menu(self, tearoff=0)

        # Open Vision Wizard (Ctrl+Shift+V)
        vision_label = (
            "Open Vision Wizard" if self.lang == "en" else "Mở Trợ lý Vision"
        )
        vision_menu.add_command(
            label=vision_label,
            accelerator="Ctrl+Shift+V",
            command=self.window_controller.open_vision_wizard,
        )

        vision_menu.add_separator()

        # Scan Region (Ctrl+Alt+S)
        scan_label = "Scan Region" if self.lang == "en" else "Quét Vùng"
        vision_menu.add_command(
            label=scan_label, accelerator="Ctrl+Alt+S", command=self._scan_region
        )

        # Add Template (Ctrl+T)
        add_tmpl_label = "Add Template" if self.lang == "en" else "Thêm Template"
        vision_menu.add_command(
            label=add_tmpl_label, accelerator="Ctrl+T", command=self._add_template
        )

        # Manage Templates (Ctrl+Shift+T)
        manage_tmpl_label = (
            "Manage Templates" if self.lang == "en" else "Quản lý Templates"
        )
        vision_menu.add_command(
            label=manage_tmpl_label,
            accelerator="Ctrl+Shift+T",
            command=self._manage_templates,
        )

        vision_menu.add_separator()

        # Toggle Overlay (Ctrl+Shift+O) - using translations
        vision_menu.add_command(
            label=self._t("vision_toggle_overlay"),
            accelerator="Ctrl+Shift+O",
            command=self._toggle_overlay,
        )

        # Overlay Settings - using translations
        overlay_settings_label = (
            "Overlay Settings..." if self.lang == "en" else "Cài Đặt Overlay..."
        )
        vision_menu.add_command(
            label=overlay_settings_label,
            command=self._open_overlay_settings,
        )

        self.add_cascade(label="Vision", menu=vision_menu)
        print("[Vision Menu] Created successfully")

    def _scan_region(self):
        EventBus.trigger(VisionScanRegionEvent())

    def _add_template(self):
        EventBus.trigger(VisionAddTemplateEvent())

    def _manage_templates(self):
        EventBus.trigger(VisionManageTemplatesEvent())

    def _toggle_overlay(self):
        if self.overlay_controller:
            self.overlay_controller.toggle_overlay()

    def _open_overlay_settings(self):
        if self.overlay_controller:
            self.overlay_controller.open_settings()
