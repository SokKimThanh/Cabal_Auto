# Session Prompt CB2B: Implement Target Name Reader & SQLite ID Mapping

Timebox: 25-30 minutes.

Objective:
Read target monster name text from Target Bar HUD, map with `monsters.db` to resolve exact `id` / `hp`, and update active hunt queue via Main Thread scheduling.

Target Files:
- Create: `lib/vision/target_name_reader.py`
- Modify: `database.py` (add query helper `find_monster_by_name`)
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py`

Implementation Details:
1. In `lib/vision/target_name_reader.py`:
   - Crop ROI above Target HP bar (Relative coordinates: y: 0.025-0.048, x: 0.40-0.60).
   - Pre-process: Convert to grayscale, apply threshold (`cv2.threshold(..., 180, 255, cv2.THRESH_BINARY)`) to isolate white text.
   - Extract string using fast OCR (`pytesseract` with PSM 7 - Single Line) or lightweight matcher.
2. In `database.py`:
   - Implement `find_monster_by_name(name_str: str, dungeon_id: Optional[str] = None) -> Optional[Dict]`:
     - Query exact match: `SELECT id, name, level, hp, defense FROM monsters WHERE name = ?`
     - If multiple entries match, filter by `dungeonId` if provided.
     - Fallback: fuzzy `LIKE %name%` query.
3. Thread-Safe UI Update:
   - When target is locked, push `[ID: #<id>] <name> (HP: <hp>)` to UI strictly via `schedule_ui_task()` / `after(0, ...)`.
   - When Target Bar disappears, schedule listbox cleanup.

Validation:
- Mock frame with target name "Training Dummy" -> assert resolved ID and stats from `monsters.db`.
- Ensure non-blocking execution (OCR + query takes < 50ms).

Session Boundary Gate:
- Handle unlisted monsters gracefully with fallback ID #0 without raising exceptions.
- Zero Tkinter calls from background threads.
- Report PASSED/REVERTED at minute 25.