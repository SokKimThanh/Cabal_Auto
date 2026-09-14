# Review Prompt 022: Extract Main Menu

## Verification Steps
1. Open `app_gui.py` and confirm that `tk.Menu` instantiation and `add_command`/`add_cascade` logic have been removed.
2. Verify the existence of `ui/components/main_menu_bar.py` (or `MenuController`) containing the extracted menu logic.
3. Check that the global hotkeys settings toggle and vision shortcuts are routed through `EventBus` rather than tightly coupled app callbacks.
4. Ensure the menu is instantiated correctly after the main `AppShell` and Tk root are initialized.

## Checklist
- [ ] `tk.Menu` logic removed from `app_gui.py`.
- [ ] `MenuController` or `MainMenuBar` component created.
- [ ] Global hotkey toggle triggers EventBus or appropriate Controller methods.
- [ ] Application launches successfully with the menu intact.
