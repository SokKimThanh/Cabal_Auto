# -*- coding: utf-8 -*-
"""
Toolbar and Filter Bar Helper Module for QuickMonsterEditor.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

try:
    from lib.ui_style import UIStyle as UI
except ImportError:
    from mock.fallbacks import UIStyle as UI

try:
    from ui.components import create_icon_label, create_icon_button
    from ui.components.icon_button import create_save_button
except ImportError:
    from mock.fallbacks import create_icon_label, create_icon_button, create_save_button


def create_top_panel(editor: Any) -> None:
    top_frame = tk.Frame(editor, bg=UI.BG_PANEL, height=50)
    top_frame.pack(side="top", fill="x")
    top_frame.pack_propagate(False)

    header_title = create_icon_label(
        top_frame,
        icon_name="monster",
        text="Quản Lý Quái Vật",
        icon_fallback="👹",
        font=UI.FONT_TITLE,
        fg=UI.COLOR_PRIMARY_TEXT,
        bg=UI.BG_PANEL,
    )
    header_title.pack(side="left", padx=15, pady=10)

    btn_frame = tk.Frame(top_frame, bg=UI.BG_PANEL)
    btn_frame.pack(side="right", padx=15, pady=10)

    editor.status_badge = tk.Label(
        btn_frame,
        text="Đã lưu tất cả",
        font=UI.FONT_SMALL,
        fg="white",
        bg="#28A745",
        padx=8,
        pady=2,
    )
    editor.status_badge.pack(side="left", padx=(0, 10))

    editor.settings_button = None

    editor.save_button = create_save_button(
        btn_frame,
        command=editor._on_save,
        icon_size=16,
        variant="compact",
        auto_hover_disabled=True,
    )
    editor.save_button.pack(side="left", padx=3)


def create_search_bar(editor: Any) -> None:
    search_frame = tk.Frame(editor, bg=UI.BG_PANEL)
    search_frame.pack(fill="x", padx=10, pady=(5, 0))

    create_icon_label(
        search_frame,
        icon_name="search",
        text="Tìm kiếm:",
        icon_fallback="🔍",
        font=UI.FONT_LABEL,
        bg=UI.BG_PANEL,
    ).grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

    editor.search_entry = tk.Entry(search_frame, font=UI.FONT_TEXT)
    editor.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
    editor.search_entry.bind("<KeyRelease>", editor._on_search_changed)
    editor.search_entry.bind("<Escape>", editor._on_clear_search)

    editor.monster_type_var = tk.StringVar(value="All Monsters")
    editor.location_var = tk.StringVar(value="All Locations")
    editor.page_size_var = tk.StringVar(value="25")

    editor.monster_type_box = ttk.Combobox(
        search_frame, textvariable=editor.monster_type_var, state="readonly", width=18
    )
    editor.monster_type_box.grid(row=0, column=2, sticky="ew", padx=(0, 5), pady=5)
    editor.monster_type_box.bind("<<ComboboxSelected>>", editor._on_filter_changed)

    editor.location_box = ttk.Combobox(
        search_frame, textvariable=editor.location_var, state="readonly", width=18
    )
    editor.location_box.grid(row=0, column=3, sticky="ew", padx=(0, 5), pady=5)
    editor.location_box.bind("<<ComboboxSelected>>", editor._on_filter_changed)

    editor.page_size_box = ttk.Combobox(
        search_frame,
        textvariable=editor.page_size_var,
        state="readonly",
        width=10,
        values=["10", "25", "50", "100"],
    )
    editor.page_size_box.grid(row=0, column=4, sticky="ew", padx=(0, 5), pady=5)
    editor.page_size_box.bind("<<ComboboxSelected>>", editor._on_filter_changed)

    editor.column_visibility_button = tk.Button(
        search_frame,
        text="Column Visibility",
        command=editor._open_column_visibility_menu,
        bg=UI.BG_DEFAULT,
        fg=UI.COLOR_TEXT,
        font=UI.FONT_LABEL,
    )
    editor.column_visibility_button.grid(
        row=0, column=5, sticky="ew", padx=(0, 5), pady=5
    )

    editor.clear_filters_button = tk.Button(
        search_frame,
        text="Clear All Filters",
        command=editor._clear_all_filters,
        bg="#FDECEC",
        fg="#B42318",
        font=UI.FONT_LABEL,
        borderwidth=1,
        relief="solid",
    )
    editor.clear_filters_button.grid(row=0, column=6, sticky="ew", pady=5)

    search_frame.columnconfigure(1, weight=1)
    editor._refresh_filter_options()
