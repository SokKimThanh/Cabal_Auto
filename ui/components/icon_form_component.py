import tkinter as tk
from tkinter import ttk
import re
from lib.ui_style_v2 import UIStyleV2 as UIStyle
from lib.i18n import t

class IconFormComponent(tk.Frame):
    def __init__(self, parent, app=None, on_name_changed_callback=None, **kwargs):
        super().__init__(parent, bg=UIStyle.BG_SURFACE, **kwargs)
        self.app = app
        self.on_name_changed_callback = on_name_changed_callback

        self.var_name = tk.StringVar()
        self.var_icon_key = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_fallback_emoji = tk.StringVar()
        self.var_tooltip_key = tk.StringVar()
        self.var_filepath = tk.StringVar()
        self.var_tooltip_en = tk.StringVar()
        self.var_tooltip_vi = tk.StringVar()

        self._available_keys = []

        self._setup_ui()
        self._load_i18n_keys()

    def i18n_t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, '_t'):
            return self.app._t(key, **kwargs)

        lang = getattr(self.app, 'lang', 'vi')
        t_kwargs = {"lang": lang}
        if "default" in kwargs:
            t_kwargs["default"] = kwargs.pop("default")
        if "ns" in kwargs:
            t_kwargs["ns"] = kwargs.pop("ns")

        translated = t(key, **t_kwargs)

        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        return translated

    def _validate_name_input(self, action, value_if_allowed):
        if action == '1': # Insert
            if len(value_if_allowed) > 50: return False
            vi_chars = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
            vi_chars += vi_chars.upper()
            pattern = rf'^[a-zA-Z0-9_\-\s{vi_chars}]*$'
            if not re.match(pattern, value_if_allowed): return False
        return True

    def _validate_key_input(self, action, value_if_allowed):
        if action == '1':
            if len(value_if_allowed) > 100: return False
            if not re.match(r'^[a-zA-Z0-9_]*$', value_if_allowed): return False
        return True

    def _validate_emoji_input(self, action, value_if_allowed):
        if action == '1' and len(value_if_allowed) > 5: return False
        return True

    def _validate_text_input(self, action, value_if_allowed):
        if action == '1' and len(value_if_allowed) > 200: return False
        return True

    def _setup_ui(self):
        # Configure columns for form labels and entries
        self.grid_columnconfigure(0, weight=0, minsize=120)
        self.grid_columnconfigure(1, weight=1, minsize=400)

        # Validations commands
        vcmd_name = (self.register(self._validate_name_input), '%d', '%P')
        vcmd_key = (self.register(self._validate_key_input), '%d', '%P')
        vcmd_emoji = (self.register(self._validate_emoji_input), '%d', '%P')
        vcmd_text = (self.register(self._validate_text_input), '%d', '%P')

        # 1. Name
        tk.Label(self, text=self.i18n_t("lbl_name", default="Name:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_name = ttk.Entry(self, textvariable=self.var_name, validate="key", validatecommand=vcmd_name)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Add auto-fill trigger
        if hasattr(self.var_name, 'trace_add'):
            self.var_name.trace_add('write', self._on_name_changed)

        # 2. Icon Key
        tk.Label(self, text="Icon Key:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_icon_key = ttk.Entry(self, textvariable=self.var_icon_key, validate="key", validatecommand=vcmd_key)
        self.entry_icon_key.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # 3. Category
        tk.Label(self, text=self.i18n_t("lbl_category", default="Category:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.combo_category = ttk.Combobox(self, textvariable=self.var_category, state="readonly")
        self.combo_category.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # 4. Fallback Emoji
        tk.Label(self, text=self.i18n_t("lbl_fallback_emoji", default="Fallback Emoji:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entry_fallback = ttk.Entry(self, textvariable=self.var_fallback_emoji, validate="key", validatecommand=vcmd_emoji)
        self.entry_fallback.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # 5. Tooltip Key
        tk.Label(self, text=self.i18n_t("lbl_tooltip_key", default="Tooltip Key:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=4, column=0, sticky="e", padx=5, pady=2)

        tooltip_frame = tk.Frame(self, bg=UIStyle.BG_SURFACE)
        tooltip_frame.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        tooltip_frame.grid_columnconfigure(0, weight=1)

        self.entry_tooltip = ttk.Combobox(tooltip_frame, textvariable=self.var_tooltip_key)
        self.entry_tooltip.grid(row=0, column=0, sticky="ew")

        self.lbl_tooltip_hint = tk.Label(tooltip_frame, text="Gợi ý: bắt đầu bằng icon_tooltip_...", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 9))
        self.lbl_tooltip_hint.grid(row=1, column=0, sticky="w", pady=(0, 2))

        self.lbl_tooltip_warning = tk.Label(tooltip_frame, text="", bg=UIStyle.BG_SURFACE, fg="#ff9800", font=(UIStyle.FONT_FAMILY_UI, 9, "bold"))
        self.lbl_tooltip_warning.grid(row=2, column=0, sticky="w")

        # English translation display
        en_frame = tk.Frame(tooltip_frame, bg=UIStyle.BG_SURFACE)
        en_frame.grid(row=3, column=0, sticky="ew", pady=(2,0))
        tk.Label(en_frame, text="EN:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 9, "bold"), width=3).pack(side="left")
        self.entry_tooltip_en = ttk.Entry(en_frame, textvariable=self.var_tooltip_en, font=(UIStyle.FONT_FAMILY_UI, 9), validate="key", validatecommand=vcmd_text)
        self.entry_tooltip_en.pack(side="left", fill="x", expand=True)

        # Vietnamese translation display
        vi_frame = tk.Frame(tooltip_frame, bg=UIStyle.BG_SURFACE)
        vi_frame.grid(row=4, column=0, sticky="ew", pady=(2,2))
        tk.Label(vi_frame, text="VI:", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 9, "bold"), width=3).pack(side="left")
        self.entry_tooltip_vi = ttk.Entry(vi_frame, textvariable=self.var_tooltip_vi, font=(UIStyle.FONT_FAMILY_UI, 9), validate="key", validatecommand=vcmd_text)
        self.entry_tooltip_vi.pack(side="left", fill="x", expand=True)

        self.lbl_tooltip_priority_info = tk.Label(tooltip_frame, text="ⓘ Tooltip của Icon sẽ được ưu tiên hơn Tooltip của Button", bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_MUTED, font=(UIStyle.FONT_FAMILY_UI, 8, "italic"))
        self.lbl_tooltip_priority_info.grid(row=5, column=0, sticky="w")

        # Validation bindings
        if hasattr(self.var_tooltip_key, 'trace_add'):
            self.var_tooltip_key.trace_add('write', self._validate_tooltip_key)
        self.entry_tooltip.bind('<KeyRelease>', self._autocomplete_tooltip)

        # 6. Filepath (Read-only)
        tk.Label(self, text=self.i18n_t("lbl_filepath", default="Filepath:"), bg=UIStyle.BG_SURFACE, fg=UIStyle.TEXT_PRIMARY).grid(row=5, column=0, sticky="e", padx=5, pady=2)

        filepath_frame = tk.Frame(self, bg=UIStyle.BG_SURFACE)
        filepath_frame.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        filepath_frame.grid_columnconfigure(0, weight=1)

        self.entry_filepath = ttk.Entry(filepath_frame, textvariable=self.var_filepath, state="disabled")
        self.entry_filepath.grid(row=0, column=0, sticky="ew")

    def _on_name_changed(self, *args):
        if self.on_name_changed_callback:
            self.on_name_changed_callback(self.var_name.get())

        name = self.var_name.get()
        if name and self.entry_name.cget("state") != "disabled":
            slug = name.strip()
            slug = self._to_non_accent_vietnamese(slug)
            slug = re.sub(r'[^a-z0-9]+', '_', slug)
            slug = slug.strip('_')

            if not self.var_icon_key.get().strip():
                self.var_icon_key.set(slug)

            if not self.var_tooltip_key.get().strip():
                self.var_tooltip_key.set(f"icon_tooltip_{slug}")

    def _to_non_accent_vietnamese(self, s: str) -> str:
        s = s.lower()
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'đ', 'd', s)
        return s

    def _load_i18n_keys(self):
        self._available_keys = []
        try:
            from lib.i18n import _REGISTRY
            keys_set = set()
            for _, langs in _REGISTRY.items():
                for _, mapping in langs.items():
                    keys_set.update(mapping.keys())
            self._available_keys = sorted(list(keys_set))
        except Exception:
            pass
        self.entry_tooltip['values'] = self._available_keys

    def _validate_tooltip_key(self, *args):
        key = self.var_tooltip_key.get().strip()

        # Reset translations
        self.var_tooltip_en.set("")
        self.var_tooltip_vi.set("")

        if not key:
            self.lbl_tooltip_warning.config(text="")
            return

        try:
            test_missing = "___MISSING___"
            val = t(key, default=test_missing, ns=None, lang=None)
            if val == test_missing:
                self.lbl_tooltip_warning.config(text="⚠️ Tooltip chưa được khai báo trong thư viện ngôn ngữ!", fg="#ff9800")
            else:
                self.lbl_tooltip_warning.config(text="✓ Tooltip hợp lệ", fg="green")

            val_en = t(key, default="___MISSING___", ns=None, lang="en")
            if val_en != "___MISSING___":
                self.var_tooltip_en.set(val_en)

            val_vi = t(key, default="___MISSING___", ns=None, lang="vi")
            if val_vi != "___MISSING___":
                self.var_tooltip_vi.set(val_vi)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error resolving tooltip key {key}: {e}")

    def _autocomplete_tooltip(self, event):
        if event.keysym not in ['BackSpace', 'Delete', 'Return', 'Tab'] and not event.char:
            return

        typed = self.entry_tooltip.get()
        if typed == '':
            self.entry_tooltip['values'] = self._available_keys
        else:
            hits = [item for item in self._available_keys if typed.lower() in item.lower()]
            self.entry_tooltip['values'] = hits

    def update_category_values(self, values):
        self.combo_category.config(values=values)

    def add_tooltip_key_if_missing(self, key):
        if key and key not in self._available_keys:
            self._available_keys.append(key)
            self._available_keys.sort()
            self.entry_tooltip['values'] = self._available_keys

    def get_form_data(self) -> dict:
        return {
            "name": self.var_name.get().strip(),
            "icon_key": self.var_icon_key.get().strip(),
            "category": self.var_category.get().strip(),
            "fallback_emoji": self.var_fallback_emoji.get().strip(),
            "tooltip_key": self.var_tooltip_key.get().strip(),
            "filepath": self.var_filepath.get().strip(),
            "tooltip_en": self.var_tooltip_en.get().strip(),
            "tooltip_vi": self.var_tooltip_vi.get().strip()
        }

    def set_form_data(self, data: dict):
        self.var_name.set(data.get("name", ""))
        self.var_icon_key.set(data.get("icon_key", ""))
        self.var_category.set(data.get("category", ""))
        self.var_fallback_emoji.set(data.get("fallback_emoji", ""))
        self.var_tooltip_key.set(data.get("tooltip_key", ""))
        self.var_filepath.set(data.get("filepath", ""))
        # Re-validate to fetch translations
        self._validate_tooltip_key()

    def enter_view_mode(self):
        self.entry_name.config(state="disabled")
        self.entry_icon_key.config(state="disabled")
        self.combo_category.config(state="disabled")
        self.entry_fallback.config(state="disabled")
        self.entry_tooltip.config(state="disabled")
        self.entry_tooltip_en.config(state="disabled")
        self.entry_tooltip_vi.config(state="disabled")

    def enter_add_mode(self):
        self.entry_name.config(state="normal")
        self.entry_icon_key.config(state="normal")
        self.combo_category.config(state="readonly")
        self.entry_fallback.config(state="normal")
        self.entry_tooltip.config(state="normal")
        self.entry_tooltip_en.config(state="normal")
        self.entry_tooltip_vi.config(state="normal")

    def enter_edit_mode(self):
        self.entry_name.config(state="normal")
        self.entry_icon_key.config(state="disabled") # PK is locked
        self.combo_category.config(state="readonly")
        self.entry_fallback.config(state="normal")
        self.entry_tooltip.config(state="normal")
        self.entry_tooltip_en.config(state="normal")
        self.entry_tooltip_vi.config(state="normal")
