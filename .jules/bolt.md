## 2025-08-18 - Vectorized NMS in VisionEngine
**Learning:** Standard Python loops with IoU checks during Non-Maximum Suppression (NMS) in template/monster detection scale poorly ($O(N^2)$ scalar iterations). Vectorizing bounding box intersection and union operations with NumPy yields an ~8x-10x speedup for candidate detection sets.
**Action:** Always prefer NumPy vectorized bounding box calculations for NMS and IoU evaluation in vision pipelines.

## 2025-08-19 - Grayscale Conversion & Caching in VisionEngine Template Matching
**Learning:** `cv2.matchTemplate` on 3-channel BGR images is ~3x slower than on 1-channel grayscale images. Pre-converting templates to grayscale on load and converting search frame regions to grayscale once per matching call yields a ~3x speedup without sacrificing detection accuracy.
**Action:** Always perform OpenCV `matchTemplate` on single-channel grayscale images and cache grayscale template images on load.

## 2026-08-24 - PR chain regression: PR #64 truncated app_gui after PR #47 modularization
**Learning:** When a large file has just been decomposed into modules, follow-up cleanup PRs are high-risk if they edit the remaining coordinator file directly. In this incident, PR #64 deleted the tail of `app_gui.py` after the `# Phase 3: Multi-Monster Support Handlers` marker, which removed `main()`, runtime callbacks, and close-path wiring while leaving extracted tabs still calling those callbacks.

**What broke main/app launch:**
- `app_gui.py` lost its executable tail, including `main()` and the WM_DELETE close path.
- Startup still referenced methods that no longer existed (`on_hunt_refresh_windows`, `_open_overlay_settings`, `_validate_hunt_prerequisites`, `_after_hunt_stop`, etc.).
- Notebook tabs were mounted as empty placeholder frames instead of the extracted `HuntTab`/`SetupTab`/`StatsTab`/`HelpTab` instances.
- `_normalize_window_bounds()` was used as if it returned bounds, but it actually mutates and returns the whole config object.
- Vision template startup code assumed `vision_templates.json` was always an object with a `templates` key, but the repo file is a raw list.

**Action for Jules:**
- Before merging a “cleanup” PR touching a coordinator file, diff the line count and verify the file still ends with the expected entry point / close path / callbacks.
- If logic was extracted to modules, add a bridge layer (controller/mixin) instead of re-growing the God Class or leaving dangling UI callbacks.
- For config loaders, accept both legacy and current shapes during migrations; do not assume a single JSON schema unless a migration rewrites it eagerly.
- Run at least these smoke checks after any PR touching app startup:
  1. instantiate `App()`
  2. enter `mainloop()` and close via `on_close()`
  3. verify second-instance lock rejects a duplicate process
  4. run targeted GUI/exclusivity tests
