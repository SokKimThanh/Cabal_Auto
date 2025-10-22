"""
Vision Menu Integration - Code Patches for app_gui.py
Sprint 22 Phase 1B

Apply these patches to integrate Vision menu into main app.
"""

import tkinter as tk
from tkinter import messagebox, filedialog

# ==================================================================
# PATCH 1: Add Vision Menu (sau settings_menu, khoảng dòng 685)
# ==================================================================

PATCH_1_LOCATION = "After: menubar.add_cascade(label='Settings', menu=settings_menu)"

PATCH_1_CODE = """
        # --- Menu: Vision (Sprint 22 Phase 1B) ---
        try:
            vision_menu = tk.Menu(menubar, tearoff=0)
            
            # Open Vision Wizard (Ctrl+Shift+V)
            vision_menu.add_command(
                label=self._t("vision_open_wizard", default="Open Vision Wizard"),
                accelerator="Ctrl+Shift+V",
                command=self._open_vision_wizard
            )
            
            vision_menu.add_separator()
            
            # Scan Region (Ctrl+Alt+S)
            vision_menu.add_command(
                label=self._t("vision_scan_region", default="Scan Region"),
                accelerator="Ctrl+Alt+S",
                command=self._scan_region
            )
            
            # Add Template (Ctrl+T)
            vision_menu.add_command(
                label=self._t("vision_add_template", default="Add Template"),
                accelerator="Ctrl+T",
                command=self._add_template
            )
            
            # Manage Templates (Ctrl+Shift+T)
            vision_menu.add_command(
                label=self._t("vision_manage_templates", default="Manage Templates"),
                accelerator="Ctrl+Shift+T",
                command=self._manage_templates
            )
            
            vision_menu.add_separator()
            
            # Toggle Overlay (Ctrl+Shift+O)
            vision_menu.add_command(
                label=self._t("vision_toggle_overlay", default="Toggle Overlay"),
                accelerator="Ctrl+Shift+O",
                command=self._toggle_overlay
            )
            
            menubar.add_cascade(label="Vision", menu=vision_menu)
            print("[Vision Menu] Created successfully")
        except Exception as e:
            print(f"[Vision Menu] Error creating menu: {e}")
"""


# ==================================================================
# PATCH 2: Bind Global Hotkeys (trong __init__, sau UI setup)
# ==================================================================

PATCH_2_LOCATION = "In __init__(), after all UI setup, before window show"

PATCH_2_CODE = """
        # Bind Vision hotkeys globally (Sprint 22 Phase 1B)
        try:
            self.bind_all('<Control-Shift-V>', lambda e: self._open_vision_wizard())
            self.bind_all('<Control-Alt-s>', lambda e: self._scan_region())
            self.bind_all('<Control-t>', lambda e: self._add_template())
            self.bind_all('<Control-Shift-T>', lambda e: self._manage_templates())
            self.bind_all('<Control-Shift-O>', lambda e: self._toggle_overlay())
            print("[Vision] Global hotkeys registered")
        except Exception as e:
            print(f"[Vision] Error binding hotkeys: {e}")
"""


# ==================================================================
# PATCH 3: Implement Vision Callbacks (cuối class AutoHuntApp)
# ==================================================================

PATCH_3_LOCATION = "At the end of AutoHuntApp class definition"

PATCH_3_CODE = '''
    # ========================================================================
    # Vision Menu Callbacks (Sprint 22 Phase 1B)
    # ========================================================================
    
    def _open_vision_wizard(self):
        """
        Open Vision Wizard window (Ctrl+Shift+V).
        Uses singleton pattern - only one instance at a time.
        """
        try:
            from ui.setup_wizard_vision import create_or_show_vision_wizard
            
            wizard = create_or_show_vision_wizard(
                self,
                config_path=self.config_path,
                on_close=self._on_vision_wizard_closed
            )
            print(f"[Vision] Wizard opened/focused: {wizard}")
            
        except Exception as e:
            print(f"[Vision] Error opening wizard: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                self._t("error", default="Error"),
                f"Cannot open Vision Wizard:\\n{e}"
            )
    
    def _on_vision_wizard_closed(self):
        """Callback when Vision Wizard is closed"""
        print("[Vision] Wizard closed")
        # TODO Phase 2: Refresh templates or update UI if needed
    
    def _scan_region(self):
        """
        Scan region for template matching (Ctrl+Alt+S).
        TODO Phase 2: Implement region scanning with overlay.
        """
        print("[Vision] Scan region - TODO Phase 2")
        messagebox.showinfo(
            "Vision - Scan Region",
            "Scan Region feature will be available in Phase 2.\\n\\n"
            "This will allow you to:\\n"
            "• Select a region on screen\\n"
            "• Scan for templates in real-time\\n"
            "• Save ROI coordinates"
        )
    
    def _add_template(self):
        """
        Quick add template (Ctrl+T).
        Opens file dialog to select template image.
        TODO Phase 2: Add to config and Vision Wizard list.
        """
        print("[Vision] Add template")
        
        try:
            filetypes = [
                ('Image files', '*.png *.jpg *.jpeg *.bmp'),
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg *.jpeg'),
                ('All files', '*.*')
            ]
            
            file_path = filedialog.askopenfilename(
                parent=self,
                title=self._t("vision_add_template", default="Add Template"),
                filetypes=filetypes
            )
            
            if file_path:
                print(f"[Vision] Selected template: {file_path}")
                
                # TODO Phase 2: Add to config
                # For now, just show success message
                messagebox.showinfo(
                    "Vision - Add Template",
                    f"Template selected:\\n{file_path}\\n\\n"
                    "Full integration will be available in Phase 2.\\n"
                    "Use Vision Wizard (Ctrl+Shift+V) to manage templates."
                )
                
        except Exception as e:
            print(f"[Vision] Error adding template: {e}")
            messagebox.showerror(
                self._t("error", default="Error"),
                f"Cannot add template:\\n{e}"
            )
    
    def _manage_templates(self):
        """
        Open template management (Ctrl+Shift+T).
        Shortcut to Vision Wizard.
        """
        print("[Vision] Manage templates - opening wizard")
        self._open_vision_wizard()
    
    def _toggle_overlay(self):
        """
        Toggle overlay display (Ctrl+Shift+O).
        TODO Phase 5: Toggle overlay on/off.
        """
        print("[Vision] Toggle overlay - TODO Phase 5")
        messagebox.showinfo(
            "Vision - Toggle Overlay",
            "Overlay toggle will be available in Phase 5.\\n\\n"
            "This will allow you to:\\n"
            "• Show/hide detection overlay\\n"
            "• See real-time template matching\\n"
            "• Display confidence scores"
        )
'''


# ==================================================================
# PATCH 4: Add Translations (lib/i18n/translations.py)
# ==================================================================

PATCH_4_LOCATION = "In lib/i18n/translations.py, add to GLOBAL_TRANSLATIONS"

PATCH_4_CODE = """
# Vision Menu translations (Sprint 22 Phase 1B)
'vision_open_wizard': {
    'vi': 'Mở Vision Wizard',
    'en': 'Open Vision Wizard'
},
'vision_scan_region': {
    'vi': 'Quét Vùng',
    'en': 'Scan Region'
},
'vision_add_template': {
    'vi': 'Thêm Template',
    'en': 'Add Template'
},
'vision_manage_templates': {
    'vi': 'Quản Lý Template',
    'en': 'Manage Templates'
},
'vision_toggle_overlay': {
    'vi': 'Bật/Tắt Overlay',
    'en': 'Toggle Overlay'
},
"""


# ==================================================================
# QUICK APPLY GUIDE
# ==================================================================

QUICK_APPLY = """
📋 QUICK APPLY GUIDE
====================

1. Open app_gui.py

2. Find line ~685: menubar.add_cascade(label="Settings", menu=settings_menu)
   → Insert PATCH_1_CODE right after

3. Find __init__ method, after all UI setup (before window show)
   → Insert PATCH_2_CODE

4. Scroll to end of AutoHuntApp class
   → Insert PATCH_3_CODE before the last closing bracket

5. Open lib/i18n/translations.py
   → Add PATCH_4_CODE to GLOBAL_TRANSLATIONS dict

6. Test:
   python app_gui.py
   → Check menu "Vision" appears
   → Press Ctrl+Shift+V → Vision Wizard opens
   → Press other hotkeys → See TODO messages

7. Commit:
   git add app_gui.py lib/i18n/translations.py
   git commit -m "feat: Add Vision menu integration (Sprint 22 Phase 1B)"
"""

print(__doc__)
print(QUICK_APPLY)

