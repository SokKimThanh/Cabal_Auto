import tkinter as tk
from typing import TYPE_CHECKING

from lib.i18n import t as i18n_t, GLOBAL_NS as I18N_GLOBAL

if TYPE_CHECKING:
    from app_gui import App


class SkillManagerWin(tk.Toplevel):
    def __init__(self, app: "App"):
        super().__init__(app)
        self.app = app
        self.title(self._t("skill_section"))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self.deiconify()
        self.lift()
        self.focus_set()

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, "_t"):
            return self.app._t(key, **kwargs)
        return i18n_t(key, ns=I18N_GLOBAL, lang=getattr(self.app, "lang", "vi"), **kwargs)

    def _on_close(self):
        controller = getattr(self.app, "skill_manager_controller", None)
        if controller:
            controller.on_window_closed()
        elif getattr(self.app, "skill_manager_win", None) is self:
            self.app.skill_manager_win = None
        self.destroy()

    def _build_ui(self):
        container = tk.Frame(self, padx=10, pady=10)
        container.pack(fill="both", expand=True)
