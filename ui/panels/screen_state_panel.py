import tkinter as tk
from typing import Dict, Any
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.i18n.translations import t

class ScreenStatePanel(tk.Frame):
    def __init__(self, parent: tk.Widget, *args, **kwargs):
        super().__init__(parent, bg=UI.BG_BASE, *args, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Container frame
        self.container = tk.Frame(self, bg=UI.BG_BASE)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Labels for state
        self.lbl_class = self._create_label(self.container, t("setup.character_class_label", "Character Class: ") + "Unknown")
        self.lbl_class.grid(row=0, column=0, sticky="w", padx=4, pady=2)

        self.lbl_location = self._create_label(self.container, "📍 Unknown")
        self.lbl_location.grid(row=0, column=1, sticky="w", padx=4, pady=2)

        self.lbl_monster = self._create_label(self.container, "🟢 Ready")
        self.lbl_monster.grid(row=1, column=0, sticky="w", padx=4, pady=2)

        self.lbl_skills = self._create_label(self.container, t("setup.skills_found", "✅ {count} skills valid").format(count=0))
        self.lbl_skills.grid(row=1, column=1, sticky="w", padx=4, pady=2)

    def _create_label(self, parent: tk.Widget, text: str) -> tk.Label:
        lbl = tk.Label(
            parent,
            text=text,
            bg=UI.BG_BASE,
            fg=UI.TEXT_PRIMARY,
            font=(UI.FONT_MAIN, 9)
        )
        return lbl

    def update_from_scan(self, state: Dict[str, Any]):
        """Updates the panel with scan state results."""
        if not state:
            return

        char_class = state.get("character_class", "Unknown")
        self.lbl_class.config(text=t("setup.character_class_label", "Character Class: ") + char_class)

        loc = state.get("location", "ZONE")
        if loc == "TOWN":
            self.lbl_location.config(text=t("setup.location_town", "📍 Town"))
        else:
            self.lbl_location.config(text=t("setup.location_zone", "📍 Zone"))

        has_monster = state.get("has_monster", False)
        if has_monster:
            self.lbl_monster.config(text=t("setup.monster_found", "👹 Found"))
        else:
            self.lbl_monster.config(text=t("setup.monster_not_found", "🟢 Ready"))

        mismatches = state.get("skill_mismatches", [])
        if mismatches:
            self.lbl_skills.config(text=t("setup.skills_invalid", "⚠️ {n} invalid").format(n=len(mismatches)))
        else:
            self.lbl_skills.config(
                text=t("setup.skills_found", "✅ {count} skills valid").format(
                    count=state.get("skills_valid_count", "—")
                )
            )
