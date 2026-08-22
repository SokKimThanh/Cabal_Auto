"""
Mock utilities and fallback definitions for UI components and lib modules when dependencies are unavailable.
"""

from __future__ import annotations
import tkinter as tk
from typing import Optional, Dict, Any, Callable, List

def check_duplicate_name(
    monsters: List[Dict[str, Any]], name: str, current_id: Optional[str] = None
) -> bool:
    if not name:
        return False
    tn = name.strip().lower()
    for m in monsters:
        if current_id and str(m.get("id", "")) == str(current_id):
            continue
        if str(m.get("name", "")).strip().lower() == tn:
            return True
    return False

def generate_unique_name(
    monsters: List[Dict[str, Any]], name: str, current_id: Optional[str] = None
) -> str:
    import re
    base = name.strip() if name else "Quái Mới"
    match = re.search(r"^(.*?)\s*\(\d+\)$", base)
    root = match.group(1).strip() if match else base
    candidate, idx = base, 1
    while check_duplicate_name(monsters, candidate, current_id):
        candidate = f"{root} ({idx})"
        idx += 1
    return candidate

def ensure_unique_monster_id(
    monster_data: Dict[str, Any],
    existing_monsters: Optional[List[Dict[str, Any]]] = None,
) -> str:
    import uuid
    m_id = str(monster_data.get("id", "")).strip()
    if not m_id:
        m_id = str(uuid.uuid4())
        monster_data["id"] = m_id
    return m_id

def i18n_t(
    key: str,
    *,
    ns: Optional[str] = None,
    lang: Optional[str] = None,
    default: Optional[str] = None,
) -> str:
    return default if default else key

def get_lang() -> str:
    return "vi"

def i18n_register_bulk(namespace: str, translations: dict) -> None:
    pass

def attach_i18n_tooltip(
    widget, key: str, ns: Optional[str], lang_provider: Callable, delay: int = 400
) -> Any:
    pass

def get_button_config(button_type: str) -> dict:
    return {"font": ("Arial", 10, "bold")}

def create_icon_button(
    parent,
    icon_name: str,
    command=None,
    text: Optional[str] = None,
    button_type: str = "green_light",
    **kwargs,
):
    config = get_button_config(button_type)
    invalid_params = [
        "icon_fallback",
        "icon_size",
        "variant",
        "tooltip_key",
        "tooltip_ns",
        "tooltip_text",
        "auto_hover_disabled",
    ]
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
    config.update(filtered_kwargs)
    icon_fallback = kwargs.get("icon_fallback", icon_name)
    display_text = text if text is not None else icon_fallback
    btn = tk.Button(parent, text=display_text, command=command, **config)
    if command:
        _orig = btn.invoke

        def _cust():
            if callable(command):
                return command()
            return _orig()

        btn.invoke = _cust
    return btn

def create_icon_label(
    parent, icon_name: str, text: str = "", icon_fallback: str = "❓", **kwargs
):
    invalid_params = ["icon_size"]
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in invalid_params}
    return tk.Label(parent, text=f"{icon_fallback} {text}", **filtered_kwargs)

def create_add_button(parent, command=None, text=None, **kwargs):
    return create_icon_button(
        parent,
        icon_name="add",
        command=command,
        text=text,
        button_type="green_light",
        **kwargs,
    )

def create_delete_button(parent, command=None, text=None, **kwargs):
    return create_icon_button(
        parent,
        icon_name="delete",
        command=command,
        text=text,
        button_type="red",
        **kwargs,
    )

def create_save_button(parent, command=None, text=None, **kwargs):
    return create_icon_button(
        parent,
        icon_name="save",
        command=command,
        text=text,
        button_type="green_light",
        **kwargs,
    )

def create_cancel_button(parent, command=None, text=None, **kwargs):
    return create_icon_button(
        parent,
        icon_name="cancel",
        command=command,
        text=text,
        button_type="refresh",
        **kwargs,
    )

def create_refresh_button(parent, command=None, text=None, **kwargs):
    return create_icon_button(
        parent,
        icon_name="refresh",
        command=command,
        text=text,
        button_type="refresh",
        **kwargs,
    )

class ActionNotificationMixin:
    def __init__(self, *args, debug_mode=False, **kwargs):
        if args:
            super().__init__(args[0])

    def show_notification(self, *args, **kwargs):
        pass

    def set_notification_widget(self, *args, **kwargs):
        pass

    def register_action_rules(self, *args, **kwargs):
        pass

    def execute_action(self, *args, **kwargs):
        if len(args) > 1 and callable(args[1]):
            args[1]()

    def has_action_rule(self, *args, **kwargs):
        return False

def set_button_enabled(
    button, enabled: bool, tooltip: Optional[str] = None
) -> None:
    button.config(state="normal" if enabled else "disabled")

class UIStyle:
    FONT_TITLE = ("Segoe UI", 12, "bold")
    FONT_SECTION = ("Segoe UI", 11, "bold")
    FONT_LABEL = ("Segoe UI", 10)
    FONT_TEXT = ("Segoe UI", 10)
    FONT_BUTTON = ("Arial", 10, "bold")
    FONT_SMALL = ("Segoe UI", 8)
    COLOR_PRIMARY = "#2196F3"
    COLOR_PRIMARY_TEXT = "#0D47A1"
    COLOR_TEXT = "#333"
    COLOR_SUBTEXT = "#666"
    COLOR_ACCENT = "#357A38"
    COLOR_DANGER = "#C62828"
    COLOR_WARNING = "#FF9800"
    BG_DEFAULT = "#FFFFFF"
    BG_PANEL = "#F5F5F5"

class MockIconHelper:
    def get_icon(self, name: str, fallback: str = "", size: int = 16) -> str:
        return fallback
