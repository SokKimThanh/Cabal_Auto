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

## 2026-08-24 - Follow-up architecture roadmap for PR debt cleanup
**Learning:** After a launch fix, the next safest move is not another giant refactor but a sequence of bounded sprints that peel responsibilities away from `app_gui.py` and the runtime bridge without reintroducing regression risk.
**Action:** See `.jules/architecture-sprint-roadmap.md` for the exact sprint plan, module boundaries, file targets, validation steps, and PR ordering to continue the architecture cleanup safely.

## 2025-08-27 - Feature Detector & Descriptor Caching in VisionEngine
**Learning:** Instantiating `cv2.ORB_create` and running `detectAndCompute` on the template image *every time* `detect_features` is called causes severe CPU overhead, especially since templates are static.
**Action:** Always cache OpenCV feature detector instances (ORB/SIFT) at the class level (`VisionEngine`), and cache the resulting keypoints and descriptors (`kp1`, `des1`) on the `Template` object on the first pass to avoid O(N) redundant computations per frame.

## 2023-10-27 - Direct RGB to GRAY conversion in OpenCV
**Learning:** PyAutoGUI screenshot returns RGB arrays. Converting directly via `cv2.COLOR_RGB2GRAY` instead of doing `RGB -> BGR -> GRAY` saves an intermediate array allocation and executes ~40% faster.
**Action:** When converting PIL images to Grayscale for OpenCV template matching, always use `cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)` directly.

## 2023-10-27 - OpenCV Feature Detector Instantiation Overhead
**Learning:** Instantiating `cv2.ORB_create` or `cv2.SIFT_create` multiple times per frame inside feature detection loops creates significant unnecessary overhead.
**Action:** Cache the instantiated OpenCV feature detectors (like ORB or SIFT) using a thread-local object (`threading.local()`) to prevent redundant creation overhead per frame while avoiding shared mutable state issues across threads.
