# -*- coding: utf-8 -*-
"""
Centralized tooltip utilities with i18n support.

Usage:
    from ui.helpers.tooltip import attach_i18n_tooltip
    attach_i18n_tooltip(widget, key='tip_apply_all', ns='library_manager', lang_provider=lambda: self.lang)

Design:
- Tooltips are translated at display-time using the current language via lang_provider.
- Keys are organized by namespace (screen/feature), e.g., 'library_manager', 'global', etc.
- Keep all tooltip copy in lib/translations.py under each namespace's translations.
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Optional

try:
    from lib.i18n import t as i18n_t  # type: ignore[assignment]
except Exception:
    # Fallback: identity signature-compatible with keyword-only args
    def i18n_t(key: str, *, ns: Optional[str] = None, lang: Optional[str] = None, default: Optional[str] = None) -> str:  # type: ignore
        return default or key


class I18nToolTip:
    """i18n-enabled tooltip for Tkinter widgets.

    The text is resolved lazily on show using i18n.t with (key, ns, lang_provider()).
    """

    def __init__(
        self,
        widget: tk.Widget,
        key: str,
        ns: Optional[str],
        lang_provider: Callable[[], str],
        delay: int = 400,
    ):
        self.widget = widget
        self.key = key
        self.ns = ns
        self.lang_provider = lang_provider
        self.delay = delay
        self._after_id = None
        self._tip_win: Optional[tk.Toplevel] = None
        try:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<ButtonPress>", self._on_leave, add="+")
        except Exception:
            pass

    def _on_enter(self, _evt=None):
        self._cancel()
        try:
            self._after_id = self.widget.after(self.delay, self._show)
        except Exception:
            self._after_id = None

    def _on_leave(self, _evt=None):
        self._cancel()
        self._hide()

    def _show(self):
        if self._tip_win:
            return
        try:
            # Resolve text at show-time for current language
            lang = None
            try:
                lang = self.lang_provider()
            except Exception:
                lang = None
            text = i18n_t(self.key, ns=self.ns, lang=lang)
            if not text:
                return
            x, y = self.widget.winfo_pointerxy()
            self._tip_win = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x+12}+{y+12}")
            label = tk.Label(
                tw,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=6,
                pady=3,
                justify="left",
            )
            label.pack()
        except Exception:
            self._tip_win = None

    def _hide(self):
        try:
            if self._tip_win is not None:
                self._tip_win.destroy()
        except Exception:
            pass
        self._tip_win = None

    def _cancel(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None


def attach_i18n_tooltip(
    widget: tk.Widget,
    key: str,
    ns: Optional[str],
    lang_provider: Callable[[], str],
    delay: int = 400,
) -> I18nToolTip:
    """Attach an i18n-enabled tooltip to a widget.

    - key: translation key
    - ns: i18n namespace (screen/module), e.g., 'library_manager'
    - lang_provider: function returning the current language code, e.g., lambda: app.lang
    - delay: ms before showing tooltip
    """
    tip = I18nToolTip(widget, key=key, ns=ns, lang_provider=lang_provider, delay=delay)
    # Keep a reference on the widget to avoid GC of bindings (optional)
    try:
        setattr(widget, "_i18n_tooltip", tip)
    except Exception:
        pass
    return tip
