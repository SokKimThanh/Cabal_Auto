# Global Rules For Sprint 26 Combat & Vision Refactor Sessions

Paste this block before each Sprint 26 prompt.

```text
Follow the architecture and cleanup rules in Cabal_Auto.

Timebox and recovery (Strict 30-Minute Budget):
- Maximum 30 minutes. At minute 25 stop new feature work and run the focused validation.
- Use minutes 25-30 only for direct, targeted bug fixes that restore basic functionality.
- At minute 30, if validation still fails, revert all code changes made by the current session using a deliberate, reviewed patch. Never use git reset, git checkout --, or a broad discard command.

Core Architectural Rules:
- Vision Scope: Stop full-screen 3D HSV search. Target Bar at top-center of the screen is the single source of truth for monster health and target lock.
- Target Key Logic: 'Z' or target key is pressed ONCE only when in search mode (i.e. no active target). Do NOT add a separate tap on the ALIVE -> DEAD transition — when a target dies, target detection naturally reports it as no-longer-alive, the orchestrator transitions to search mode on its own, and the search-mode branch already taps the key there. A separate death-transition tap path was previously removed as redundant (it caused a double-tap) and must not be reintroduced. NEVER spam the target key while target_active is True.
- Fast-Break: Skill cast-time waits must poll target health every 30-50ms (the finalized default across sessions is a fixed 40ms slice; treat 30-50ms as the acceptable range, not a license to pick a different value per session) and break immediately when health reaches zero to preserve combo flow.
- Main Thread Safety: Only the Main Thread calls Tkinter methods, including constructing `PhotoImage`/`ImageTk` objects. Workers/services communicate via scheduler (`after(0, ...)`/`schedule_ui_task`) or thread-safe callbacks.
- Screen Capture Thread Safety: reads of the latest captured frame (e.g. `get_latest_frame()`) and writes/reallocations inside the capture loop must be protected by a shared lock, so a concurrent reader never observes a partially-written or mismatched-size buffer. Capture readers should receive a copy of the frame, not a live reference to the buffer being written by the capture thread.
- Boundary Checks: Must handle empty frame, game minimized/invalid bounds (-32000), target lost timeout, and missing templates.

i18n & Style Rules:
- Preserve **UIStyle tokens** for fonts, colors, and layouts. Do not hardcode styles in translation files.
- All new UI strings must support both 'en' and 'vi'.
- **Database Synchronization** (applies to all UI strings registered from this point forward; existing dictionaries registered in earlier sessions before this rule was added are not yet compliant and need a dedicated backfill session before this requirement can be considered fully met project-wide):
  - Translation dictionaries in code (e.g., `monster_editor_translations.py`, `translations.py`) must be mirrored in the `translations` table of the database.
  - Each translation entry must include: `namespace`, `key`, `lang`, `text`, and `updated_at`.
  - Sync scripts (`register_bulk`) must push new or updated keys into DB automatically.
  - Validation step: compare dictionary keys vs. DB entries. Missing DB entries → fallback to English.
  - CI/CD pipeline must enforce dictionary ↔ DB consistency before merge.
- **UIStyle Integration**:
  - UI elements must combine `UIStyle` constants with i18n text.
    Example: `tk.Label(parent, text=i18n('monster_name_label'), font=UI.FONT_LABEL, fg=UI.COLOR_TEXT)`
  - Colors and fonts are centralized in `ui_style.py` and must not be duplicated in translation files.
  - Accessibility: All color combinations must meet WCAG AA contrast ratio ≥ 4.5:1.

Before final response:
- Report PASSED or ABORTED/REVERTED, modified files, validation commands/results, boundary case evidence, and deferred next session.
```