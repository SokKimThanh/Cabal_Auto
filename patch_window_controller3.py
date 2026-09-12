with open('ui/controllers/app_window_controller.py', 'r') as f:
    content = f.read()

func = """
    def update_window_bounds_display(self) -> None:
        if self.root.state_controller.get_ui_var("window_bounds_display") is None:
            return

        from lib.features.hunt.window_selection_service import WindowSelectionService
        from lib.ui_style_v2 import UIStyleV2 as UIStyle
        from lib.i18n import t as i18n_t

        bounds = WindowSelectionService.resolve_bounds(
            self.root.state_controller.hunt_cfg, self.root.state_controller.current_window_bounds
        )
        if bounds:
            self.root.state_controller.set_ui_var("window_bounds_display", f"{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}")
        else:
            self.root.state_controller.set_ui_var("window_bounds_display", "")

        if self.root.state_controller.get_ui_var("bounds_status") is not None and "bounds_readiness_label" in self.root.state_controller.ui_widgets:
            selected_window = self.root.state_controller.get_ui_var("win_combo")

            is_minimized = False
            if selected_window and self.root.state_controller.win_items:
                selected_hwnd = self.root.state_controller.hunt_selected.get("hwnd") if self.root.state_controller.hunt_selected else None
                for item in self.root.state_controller.win_items:
                    if selected_hwnd and item.get("hwnd") == selected_hwnd:
                        is_minimized = item.get("is_minimized", False)
                        break
                    elif item.get("title") == selected_window:
                        is_minimized = item.get("is_minimized", False)
                        break

            compact = getattr(self.root, "_bounds_compact_mode", False)
            if not selected_window:
                text = "[!]" if compact else i18n_t("bounds_state_select")
                self.root.state_controller.set_ui_var("hunt_status", text)
                if self.root.state_controller.ui_widgets.get('bounds_readiness_label'): self.root.state_controller.ui_widgets['bounds_readiness_label'].config(fg=UIStyle.COLOR_WARNING)
            elif self.root.state_controller.bounds_recovery_failed:
                text = "[!]" if compact else i18n_t("bounds_state_failed")
                self.root.state_controller.set_ui_var("hunt_status", text)
                if self.root.state_controller.ui_widgets.get('bounds_readiness_label'): self.root.state_controller.ui_widgets['bounds_readiness_label'].config(fg=UIStyle.COLOR_DANGER)
            elif is_minimized or (bounds and (bounds[0] <= -32000 or bounds[1] <= -32000)):
                text = "[!]" if compact else i18n_t("bounds_state_minimized")
                self.root.state_controller.set_ui_var("hunt_status", text)
                if self.root.state_controller.ui_widgets.get('bounds_readiness_label'): self.root.state_controller.ui_widgets['bounds_readiness_label'].config(fg=UIStyle.COLOR_DANGER)
            elif not bounds:
                text = "[!]" if compact else i18n_t("bounds_state_invalid")
                self.root.state_controller.set_ui_var("hunt_status", text)
                if self.root.state_controller.ui_widgets.get('bounds_readiness_label'): self.root.state_controller.ui_widgets['bounds_readiness_label'].config(fg=UIStyle.COLOR_WARNING)
            else:
                text = "[✓]" if compact else i18n_t("bounds_state_ready").format(title=f"{bounds[2]}x{bounds[3]}")
                self.root.state_controller.set_ui_var("hunt_status", text)
                if self.root.state_controller.ui_widgets.get('bounds_readiness_label'): self.root.state_controller.ui_widgets['bounds_readiness_label'].config(fg=UIStyle.COLOR_ACCENT)
"""

if "def update_window_bounds_display" not in content:
    content += "\n" + func
    with open('ui/controllers/app_window_controller.py', 'w') as f:
        f.write(content)
