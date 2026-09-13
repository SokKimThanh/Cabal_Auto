# Sprint 30 - Implement Global Pylint Scan UI Feature

## Context & Prerequisites
This task involves adding a new UI feature to scan the entire codebase using Pylint directly from the application's UI.
**Important Constraint:** Do not execute this task if the application is currently undergoing heavy UI architecture refactoring (e.g., God Class decomposition in `app_gui.py`). Ensure the `TaskScheduler` and background threading architectures are stable before proceeding to avoid race conditions and UI freezing.

## Objective
Implement a "Pylint App" button in the `ActivityLogsFrame` that triggers a background process to run `pylint` on all `.py` files in the project. The output should stream to the UI logs, and a full report should be saved to a `.txt` file.

## Execution Steps for Dev/AI Bot

### 1. Update Translations (i18n)
- File: `lib/i18n/translations.py`
- Action: Add the following keys to both 'en' and 'vi' dictionaries in the general UI section (near other `logs_...` keys):
  - `logs_pylint`: "Run Pylint" (EN) / "Quét lỗi hệ thống" (VI)
  - `logs_pylint_confirm_title`: "Confirm Pylint Scan" (EN) / "Xác nhận Quét Pylint" (VI)
  - `logs_pylint_confirm_msg`: "Scanning the entire codebase may take a few minutes. Continue?" (EN) / "Quá trình quét toàn bộ mã nguồn có thể mất vài phút. Bạn có muốn tiếp tục?" (VI)

### 2. Update the UI Component
- File: `ui/views/activity_logs_frame.py`
- Action: In the `__init__` method, inside the `toolbar_frame`, add a new `tk.Button` for Pylint.
  - Position it on the `right` side, next to the `copy_btn` and `folder_btn`.
  - Use `self.app._t("logs_pylint")` for the text (or `self.app.bind_text` if available).
  - Bind the command to a new method `self._confirm_and_run_pylint()`.

### 3. Implement the Logic in ActivityLogsFrame
- Add the method `_confirm_and_run_pylint(self)`:
  - Call `DialogService.ask_yes_no()` (using the new translation keys) to confirm the user's intent.
  - If yes, append an INFO message to the logs: "Starting Pylint scan...".
  - Disable the Pylint button to prevent multiple concurrent scans.
  - Spawn a background thread to run the scan: `threading.Thread(target=self._run_pylint_worker, daemon=True).start()`.

- Add the worker method `_run_pylint_worker(self)`:
  - **Do not modify Tkinter UI elements directly from this thread.**
  - **Finding Files:** Use `pathlib` or `os.walk` to find all `.py` files in the project root. Exclude directories like `venv`, `.git`, `__pycache__`, `logs`, `docs`.
  - **Execution:** Use `subprocess.run` or `subprocess.Popen` to run `pylint [file_list]`. Capture the `stdout` and `stderr`.
  - **Save Report:** Write the captured output to a file, e.g., `logs/pylint_report.txt`. Ensure the `logs` directory exists.
  - **UI Callback:** Once finished, use the application's `TaskScheduler` (if available) or `self.after(0, ...)` to safely re-enable the Pylint button and append a summary message to the logs: "Pylint scan complete! Report saved to logs/pylint_report.txt".

## Acceptance Criteria
- [ ] Clicking "Run Pylint" shows a confirmation dialog.
- [ ] Confirming the dialog starts a background thread (UI does not freeze).
- [ ] Progress/Status is updated in the `ActivityLogsFrame` text widget.
- [ ] A detailed report is written to `logs/pylint_report.txt`.
- [ ] The application remains stable and does not crash during or after the scan.
