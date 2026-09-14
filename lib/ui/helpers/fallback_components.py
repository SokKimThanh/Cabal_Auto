import tkinter as tk

def _create_icon_btn_component(
    parent,
    icon_name,
    command=None,
    text=None,
    button_type="green_light",
    icon_size=16,
    button_size=None,
    icon_fallback="",
    tooltip_key=None,
    tooltip_ns=None,
    tooltip_text=None,
    state="normal",
    variant=None,
    width=None,
    padding=None,
    on_hover=None,
    on_leave=None,
    on_focus=None,
    auto_hover_disabled=True,
    **kwargs,
):
    """Fallback icon button creator when component not available."""
    from typing import Literal, cast

    # Cast state to proper type
    btn_state = cast(
        Literal["normal", "active", "disabled"],
        state if state in ["normal", "active", "disabled"] else "normal",
    )
    # Handle None command
    btn_command = command if command is not None else lambda: None

    # Filter out custom options that tk.Button doesn't understand
    valid_button_options = {
        "bg",
        "fg",
        "activebackground",
        "activeforeground",
        "relief",
        "bd",
        "borderwidth",
        "padx",
        "pady",
        "width",
        "height",
        "highlightthickness",
        "highlightbackground",
        "highlightcolor",
        "font",
        "cursor",
        "wraplength",
        "overrelief",
        "bitmap",
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_button_options}

    btn = tk.Button(
        parent,
        text=icon_fallback or "?",
        command=btn_command,
        state=btn_state,
        **filtered_kwargs,
    )
    return btn
