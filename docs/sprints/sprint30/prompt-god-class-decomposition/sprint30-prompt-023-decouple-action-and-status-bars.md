# Sprint 30 - Prompt 023: Decouple Action and Status Bars

## Goal
Remove strict dependencies on the `App` God Class from `ActionBarView` and `StatusBarView`.

## Context (Nợ Kỹ Thuật)
Mặc dù `AppShell` đã tách phần layout cơ bản, các component con như `ActionBarView` và `StatusBarView` vẫn đang phụ thuộc vào biến `app` (chứa toàn bộ God Class). Các view này gọi trực tiếp các hàm từ `app` thay vì giao tiếp qua Controller hoặc EventBus.

## Required Actions

1. **Refactor `ActionBarView` dependencies**
   - Update `ui/components/action_bar_view.py` (or similar file).
   - Change the constructor signature from accepting `app` to accepting `state_controller` (the `AppStateController`) and any specific required domain controllers (e.g., `HuntController`).
   - Replace any direct method calls to `self.app.something()` with EventBus emissions or specific controller methods.

2. **Refactor `StatusBarView` dependencies**
   - Update `ui/components/status_bar_view.py`.
   - Update the constructor to take `state_controller`.
   - Remove references to `app` inside the view logic.

3. **Global UI Updates via EventBus**
   - For UI-wide actions triggered from these bars (for example, `on_language_change`), implement or use an existing `EventBus` event to broadcast the change, rather than calling a direct refresh function on the `App` class.

4. **Update `app_gui.py` Instantiation**
   - Update how `ActionBarView` and `StatusBarView` are instantiated in `app_gui.py` to pass the `state_controller` instead of `self`.

## Acceptance Criteria
- `ActionBarView` and `StatusBarView` no longer store or use the `app` God Class instance.
- Button clicks on Action/Status bars function normally, communicating via EventBus or domain controllers.
