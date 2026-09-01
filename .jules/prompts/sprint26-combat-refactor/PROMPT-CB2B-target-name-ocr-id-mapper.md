# Session Prompt CB2B: Implement Target Name Reader & SQLite ID Mapping

Timebox: 25-30 minutes.

Objective:
Read target monster name text from Target Bar HUD, map with `monsters.db` to resolve exact `id` / `hp`, and update active hunt queue via Main Thread scheduling.

Target Files:
- Create: `lib/vision/target_name_reader.py`
- Modify: `database.py` (add query helper `find_monster_by_name`)
- Modify: `lib/features/hunt/hunt_orchestrator.py`
- Modify: `app_gui.py`

Dependencies:
- Requires `pytesseract` + a Tesseract OCR binary installed and on `PATH`, or `pytesseract.pytesseract.tesseract_cmd` set explicitly to the binary path (Windows installs are not on `PATH` by default — set this at module init, fail fast with a clear error if the binary is missing rather than raising deep inside `image_to_string`).

## Implementation Details

1. In `lib/vision/target_name_reader.py`:
   - Crop ROI above Target HP bar (Relative coordinates: y: 0.025-0.048, x: 0.40-0.60). This sits directly above the CB1 HP-bar ROI (y: 0.048-0.065) with no vertical overlap — keep both ROI definitions in sync if either changes.
   - Pre-process: convert to grayscale, then binarize using Otsu's method rather than a fixed threshold: `cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)`. A fixed threshold (e.g. a hard-coded `180`) is fragile against HUD theme/brightness/opacity changes; Otsu adapts per-frame.
   - Extract string using OCR (`pytesseract` with PSM 7 — Single Line) or a lightweight matcher.
   - Performance/caching: do not run OCR on every worker tick. OCR (even PSM 7) typically costs 50-200ms per call depending on ROI size and is too slow for a per-frame budget. Only trigger OCR when the target identity is likely to have changed — e.g. on the `search → attack` transition (new target acquired), or on a separate throttled interval (e.g. every 1-2s) — and cache the last resolved name/id/hp between triggers. Downstream code (orchestrator, UI) reads the cached result, not a fresh OCR call per tick.
2. In `database.py`:
   - Implement `find_monster_by_name(name_str: str, dungeon_id: Optional[str] = None) -> Optional[Dict]`:
     - Exact match first: `SELECT id, name, level, hp, defense FROM monsters WHERE name = ?` with `name_str` as the bound parameter.
     - If multiple rows match the exact query, filter by `dungeonId = ?` when `dungeon_id` is provided; if still multiple after filtering, return the first row ordered by `id ASC` (deterministic tie-break) and log a warning that the name is ambiguous within scope.
     - Fallback (only if exact match returns nothing): fuzzy query `SELECT id, name, level, hp, defense FROM monsters WHERE name LIKE ?`, binding the parameter as `f"%{name_str}%"` (always use a bound parameter here — never interpolate `name_str` directly into the SQL string). Escape any literal `%` or `_` characters already present in `name_str` before wrapping it (e.g. via a helper that escapes then wraps), so OCR text containing those characters doesn't distort the pattern.
     - If the fuzzy query returns multiple rows, pick the one whose `name` length is closest to `len(name_str)` (closest-length heuristic reduces false positives from partial/garbled OCR text) and log the ambiguity.
3. Thread-Safe UI Update:
   - OCR and DB lookup run on the background worker thread. Do not call Tkinter directly from there. Push the resolved result (`id`, `name`, `hp`, or the fallback below) into a thread-safe queue (`queue.Queue`) or a lock-protected shared variable that both the orchestrator and the UI layer read.
   - The orchestrator reads the latest queued result on its own tick without blocking on OCR.
   - When target is locked, push `[ID: #<id>] <name> (HP: <hp>)` to UI strictly via `schedule_ui_task()` / `after(0, ...)`, reading from the same shared result, not by calling OCR/DB itself.
   - When Target Bar disappears (per CB1/CB2's `have_target` debounce logic), schedule listbox cleanup and clear the cached OCR result.
4. Unlisted monster handling:
   - If `find_monster_by_name` returns `None` after both exact and fuzzy attempts, fall back to `{"id": 0, "name": name_str, "hp": None, "defense": None}` and continue without raising. Downstream consumers (orchestrator) must treat `id == 0` as "unknown monster" — e.g. skip any per-monster-specific logic keyed on `id`/`hp` and fall back to generic handling, rather than assuming `id == 0` is a valid catalog entry.

## Validation

- Mock frame with target name "Training Dummy" → assert resolved ID and stats from `monsters.db` (exact match path).
- (Added) Mock frame with a slightly garbled/partial OCR string (e.g. "Trainng Dumm") for a name that exists in `monsters.db` → assert the fuzzy fallback resolves to the correct row via the closest-length heuristic.
- (Added) Mock frame with a name string not present in `monsters.db` at all → assert fallback `{"id": 0, ...}` is returned without raising, and no exception propagates to the caller.
- (Added) Simulate two consecutive ticks with the same target (no transition) → assert OCR is called only once (cached result reused), verifying the throttle/cache behavior.
- Ensure non-blocking execution: OCR + query together should not stall the worker loop; verify via the throttle/cache mechanism above rather than asserting a fixed millisecond ceiling on the raw OCR call itself (Tesseract's own latency is environment-dependent).

## Session Boundary Gate

- Handle unlisted monsters gracefully with fallback ID #0 without raising exceptions.
- Zero Tkinter calls from background threads.
- Confirm OCR is throttled/cached rather than invoked every worker tick.
- Confirm all SQL queries (including the fuzzy fallback) use bound parameters, with no direct string interpolation of OCR text into SQL.
- Report PASSED/REVERTED at minute 25.