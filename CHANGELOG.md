# Changelog

## 2025-10-22 — pr/hotkey-image-2025-10-22

Summary
- Add README section describing Launching & Hotkey Diagnostics and run_venv launchers
- Document intentional use of dynamic image references (`_image_refs`) in `lib/ui`
- Add minimal type-check annotations/ignores to silence static analyzer warnings for dynamic widget attributes

Files changed
- `README.md` — added diagnostics section
- `ui/setup_wizard.py` — type-ignore annotations for LibraryManagerWindow parent arg and safer setattr usage in demo block
- `app_gui.py` — documented `_image_refs` usage and ensured central storage for PhotoImage refs
- `lib/ui/__init__.py` — package note about image refs and type-ignores

Notes
- Tests: targeted unit tests for tooltip/image-ref retention passed locally.
- Static diagnostics: no current errors after changes. Some uses include deliberate `# type: ignore` comments.

## Refactor: decompose app_gui God Class into modular MVC architecture
- Extract core services to lib/system (InstanceLock, HotkeyManager)
- Extract domain repos and runner to lib/features (hunt, monsters, skills)
- Split GUI tabs into standalone components in ui/tabs (Hunt, Setup, Stats, Help)
- Extract dialogs and modals into ui/windows
- Ensure clean separation of concerns and fix all flake8/test regressions
