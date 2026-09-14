# Sprint 30 Phase 4 Prompt 028: Finalize App Class

## Goal
Strip the `App` class down to its bare essentials.

## Details
- The `App` class should only be responsible for:
  - Initializing `tk.Tk()` (via `AppShell`).
  - Instantiating dependency injection container services (`AppContainer`).
  - Starting the `AppLifecycleController` and Tkinter main loop.
- Ensure any remaining stray event handlers (`on_start_stop_clicked`, `_refresh_start_stop_visual`, etc.) are moved to their respective domain controllers (`HuntController`, etc.).

## Acceptance Criteria
- `app_gui.App` contains no more than 30 methods, strictly related to application bootstrapping and shutdown.
- Running `python -c 'import app_gui; print(len([x for x in dir(app_gui.App) if callable(getattr(app_gui.App, x))]))'` shows `< 100` total methods (including inherited Tkinter methods).
- Application successfully launches, hunts, and logs output without crashing.
- `pylint app_gui.py` remains at 10.0/10.0.
