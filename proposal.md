Here are the answers and proposals for your questions:

1. **Naming and Location:** Let's create the file at `lib/ui/components/main_menu_bar.py` and name the class `MainMenuBar`. Since Tkinter's `Menu` class is intrinsically tied to UI construction, a "Component" makes architectural sense. It constructs UI elements (`tk.Menu`) but delegates logic outward.
2. **EventBus Usage:** You don't need to create new `EventBus` events for everything. For domain-specific actions like "toggle hotkeys" or "open vision wizard", the component should ideally invoke methods on the specific domain controller or `WindowController` directly (if injected) OR we can use the `AppContainer` injected via `App` to reach `HotkeyController` and `AppWindowController`. However, the prompt specifically asks to "ensure these menu items trigger updates via the `EventBus` or directly interact with their specific domain controllers". So we will just pass references to the necessary controllers (like `HotkeyController`, `AppWindowController`, `OverlayController`) when initializing `MainMenuBar`.
3. **Dependencies:** The `MainMenuBar` should accept `parent` (the `tk.Tk()` root window, which is `App`), `app_state_controller`, and references to other needed controllers (like `hotkey_controller`, `window_controller`, `overlay_controller`). This avoids the Menu being tightly coupled to the `App` God Class itself. It will just call `self.hotkey_controller.register_all()` directly, etc.
4. **Menu Attachment:** The `MainMenuBar` should subclass `tk.Menu` and take responsibility for constructing itself. The actual attachment (`root.config(menu=menubar)`) can happen either inside the component (if it gets `root`) or returned. The prompt states: "Instantiate this menu component properly within `app_gui.py` after the root Tk instance is initialized". So we will create it in `App.__init__` and attach it there:
```python
self.main_menu = MainMenuBar(
    parent=self,
    state_controller=self.state_controller,
    hotkey_controller=self.hotkey_controller,
    window_controller=self.window_controller,
    # etc...
)
self.config(menu=self.main_menu)
```
