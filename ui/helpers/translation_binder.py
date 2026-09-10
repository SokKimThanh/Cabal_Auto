import weakref
import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class TranslationBinder:
    """
    Manages dynamic translations for UI widgets.
    Allows registering widgets with their i18n keys so they can be
    automatically updated when the language changes.
    Uses weak references to avoid memory leaks if widgets are destroyed.
    """
    def __init__(self):
        # We store tuples of (weakref(widget), key, kwargs)
        self._tracked_widgets = []
        self._tracked_vars = []

    def bind(self, widget, key: str, **kwargs):
        """
        Bind a widget to a translation key.
        When language changes, widget.config(text=t(key)) will be called.
        """
        # Immediately set the initial value if we have a valid reference to the app's _t method
        # but we don't have it here. The caller should set it or the first refresh will set it.
        # Actually, let's just track it.
        ref = weakref.ref(widget)
        self._tracked_widgets.append((ref, key, kwargs))
        return widget

    def bind_var(self, tk_var, key: str, **kwargs):
        """
        Bind a tk.Variable (like StringVar) to a translation key.
        """
        ref = weakref.ref(tk_var)
        self._tracked_vars.append((ref, key, kwargs))
        return tk_var

    def refresh_all(self, translator_func):
        """
        Update all tracked widgets and variables using the provided translator_func.
        translator_func should accept (key, **kwargs) and return a string.
        Cleans up dead references.
        """
        alive_widgets = []
        for ref, key, kwargs in self._tracked_widgets:
            widget = ref()
            if widget is not None:
                try:
                    new_text = translator_func(key, **kwargs)
                    if isinstance(widget, (tk.Label, ttk.Label, tk.Button, ttk.Button, tk.Checkbutton, ttk.Checkbutton, tk.Radiobutton, ttk.Radiobutton)):
                        widget.config(text=new_text)
                    # Support for our custom icon button wrapper which might have set_text
                    elif hasattr(widget, 'set_text'):
                        widget.set_text(new_text)
                except Exception as e:
                    logger.debug(f"[TranslationBinder] Error updating widget for key {key}: {e}")
                alive_widgets.append((ref, key, kwargs))
        self._tracked_widgets = alive_widgets

        alive_vars = []
        for ref, key, kwargs in self._tracked_vars:
            var = ref()
            if var is not None:
                try:
                    new_text = translator_func(key, **kwargs)
                    var.set(new_text)
                except Exception as e:
                    logger.debug(f"[TranslationBinder] Error updating var for key {key}: {e}")
                alive_vars.append((ref, key, kwargs))
        self._tracked_vars = alive_vars
