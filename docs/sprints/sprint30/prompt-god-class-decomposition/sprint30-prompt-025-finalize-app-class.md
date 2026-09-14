# Sprint 30 - Prompt 025: Finalize App Class Decomposition

## Goal
Strip the `App` class in `app_gui.py` down to its bare essentials, achieving true Single Responsibility as the application bootstrapper.

## Context (Nợ Kỹ Thuật)
Sau các giai đoạn trước, `app_gui.py` vẫn còn kẹt lại một số hàm xử lý sự kiện rác (event handlers) và các logic không thuộc về khởi tạo hệ thống. Mục tiêu cuối cùng là biến `App` thành một class siêu mỏng (thin class).

## Required Actions

1. **Relocate Remaining Domain Handlers**
   - Identify all leftover event handlers in `app_gui.py` (e.g., `on_start_stop_clicked`, `on_monster_select_change`, etc.).
   - Move these methods directly into their respective domain controllers (e.g., `HuntController` or `MonsterRotationController`).

2. **Restrict App Responsibilities**
   - Ensure `app_gui.App` is ONLY responsible for:
     1. Initializing `tk.Tk()` (delegated primarily to `AppShell`).
     2. Instantiating the dependency injection container (`AppContainer` or similar services).
     3. Starting the `AppLifecycleController` and invoking the Tkinter main loop (`self.mainloop()`).

3. **Cleanup and Verify**
   - Remove any remaining unused imports.
   - Run a strict linting and method count check on `app_gui.py`.

## Acceptance Criteria
- `app_gui.App` contains strictly 20-30 methods or fewer (excluding inherited `tk.Tk` methods).
- `app_gui.py` is focused solely on application bootstrapping, DI container setup, and shutdown.
- `pylint app_gui.py` yields 10.0/10.0.
- Command `python -c "import app_gui; print(len([x for x in dir(app_gui.App) if callable(getattr(app_gui.App, x)) and not x.startswith('__')]))"` verifies a massively reduced method count.
