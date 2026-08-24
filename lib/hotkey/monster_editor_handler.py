"""Monster Editor Hotkey Handler Module.

Handles all Ctrl+Shift+M hotkey logic for opening Quick Monster Editor.
Extracted from app_gui.py for better separation of concerns.

Sprint 24 - Code Reorganization
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Any


class MonsterEditorHandler:
    """Handles Monster Editor hotkey (Ctrl+Shift+M) and opening logic.
    
    Features:
    - Singleton pattern validation
    - Double-open prevention
    - Thread-safe main thread scheduling
    - Detailed debug logging (configurable)
    """
    
    def __init__(self, app_window: tk.Tk, debug: bool = False):
        """Initialize Monster Editor handler.
        
        Args:
            app_window: Main application window (Tk instance)
            debug: Enable detailed debug logging
        """
        self.app = app_window
        self.debug = debug
        self._opening_flag = False
        
    def on_hotkey_pressed(self) -> None:
        """Callback for Monster Editor hotkey (Ctrl+Shift+M).
        
        Opens Quick Monster Editor for rapid CRUD operations.
        Always available regardless of UI mode.
        """
        try:
            print("[Hotkeys] Monster Editor hotkey (Ctrl+Shift+M) pressed")
            
            # Detailed debug logs (enabled by debug flag)
            if self.debug:
                import os
                print(f"  Trigger PID: {os.getpid()}")
                print(f"  App window exists: {self.app.winfo_exists()}")
                print(f"  App window class: {self.app.winfo_class()}")
                print(f"  Opening flag: {self._opening_flag}")
                
                # Log all current toplevel windows
                try:
                    all_toplevels = [w for w in self.app.winfo_children() if isinstance(w, tk.Toplevel)]
                    print(f"  Current Toplevel windows: {len(all_toplevels)}")
                    for i, w in enumerate(all_toplevels):
                        try:
                            print(f"    [{i}] {w.winfo_class()} - {w.title() if hasattr(w, 'title') else 'N/A'}")
                        except:
                            print(f"    [{i}] <destroyed or invalid>")
                except Exception as e:
                    print(f"  Error listing toplevels: {e}")
            
            # Schedule Monster Editor to open in main thread
            self.app.after(0, self.open_monster_editor)
            
        except Exception as e:
            print(f"[Hotkeys] Error opening Monster Editor: {e}")
            import traceback
            traceback.print_exc()

    def open_monster_editor(self, on_save_callback: Optional[Callable[[str, dict], None]] = None) -> None:
        """Open Quick Monster Editor dialog.
        
        Opens the quick monster editor for fast monster CRUD operations.
        Uses singleton pattern to prevent multiple instances.
        
        Args:
            on_save_callback: Optional callback when monster is saved (monster_id, monster_data)
        """
        print("[Monster Editor] Opening...")
        
        # Detailed debug logs (enabled by debug flag)
        if self.debug:
            import os
            print(f"  Current PID: {os.getpid()}")
            print(f"  Opening flag: {self._opening_flag}")
        
        # ✅ FIX: Don't open editor if app is not fully initialized
        if not hasattr(self.app, '_first_time_check_complete'):
            print("[Monster Editor] ⚠ App not fully initialized, ignoring request")
            return
        
        # Prevent double-opening if already in progress
        if self._opening_flag:
            print("[Monster Editor] ⚠ Already opening, ignoring duplicate request")
            return
        
        try:
            self._opening_flag = True
            
            # Import quick editor (lazy import to avoid circular dependencies)
            try:
                import ui.windows.quick_monster_editor as monster_editor_module
                
                if self.debug:
                    print(f"[Monster Editor] Import successful")
                    print(f"  Singleton instance exists: {monster_editor_module._quick_editor_instance is not None}")
                    if monster_editor_module._quick_editor_instance:
                        try:
                            print(f"  Singleton valid: {monster_editor_module._quick_editor_instance.winfo_exists()}")
                        except:
                            print(f"  Singleton valid: <error checking>")
            except ImportError as ie:
                print(f"[Monster Editor] ✗ Failed to import: {ie}")
                messagebox.showerror(
                    "Import Error",
                    f"Could not load Monster Editor module:\n{ie}"
                )
                self._opening_flag = False
                return
            
            # ✅ Sprint 24 Fix: Check singleton via module reference (not local import)
            # This ensures we see the actual global variable state
            try:
                instance = monster_editor_module._quick_editor_instance
                instance_exists = instance is not None
                instance_alive = False
                
                if instance_exists and instance:  # Explicit None check for type checker
                    try:
                        instance_alive = bool(instance.winfo_exists())
                    except Exception as check_err:
                        print(f"[Monster Editor] Stale instance detected: {check_err}")
                        monster_editor_module._quick_editor_instance = None
                        instance_alive = False
                
                print(f"[Monster Editor] Check: exists={instance_exists}, alive={instance_alive}")
                
                if instance_exists and instance_alive and instance:
                    print("[Monster Editor] ✓ Instance already exists, bringing to front")
                    print(f"  Instance: {instance}")
                    instance.lift()
                    instance.focus_force()
                    self._opening_flag = False
                    return
            except Exception as e:
                print(f"[Monster Editor] Error checking singleton: {e}")
                # Continue to create new instance
            
            print(f"[Monster Editor] No valid instance found, creating new...")
            
            if self.debug:
                print(f"[Monster Editor] Creating new instance with parent: {self.app}")
                print(f"  Parent type: {type(self.app)}")
                print(f"  Parent class: {self.app.__class__.__name__}")
            
            # Use callback from app if not provided
            save_callback = on_save_callback
            if save_callback is None and hasattr(self.app, '_on_monster_saved'):
                save_callback = self.app._on_monster_saved
            
            # Show quick editor (singleton pattern handles existing instances)
            editor = monster_editor_module.show_quick_monster_editor(
                parent=self.app,
                monster_id=None,  # None = create new monster
                on_save=save_callback
            )
            
            # ✅ FIX: Reset flag immediately after successful creation
            self._opening_flag = False

            print(f"[Monster Editor] ✓ Opened successfully")
            
            if self.debug:
                print(f"  Editor instance: {editor}")
                print(f"  Editor type: {type(editor)}")
            
        except Exception as e:
            print(f"[Monster Editor] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Monster Editor Error",
                f"Failed to open Monster Editor:\n{e}"
            )
            # Reset flag immediately on error
            self._opening_flag = False


def create_monster_editor_handler(app_window: tk.Tk, debug: bool = False) -> MonsterEditorHandler:
    """Factory function to create MonsterEditorHandler instance.
    
    Args:
        app_window: Main application window (Tk instance)
        debug: Enable detailed debug logging
        
    Returns:
        MonsterEditorHandler instance
    """
    return MonsterEditorHandler(app_window, debug=debug)
