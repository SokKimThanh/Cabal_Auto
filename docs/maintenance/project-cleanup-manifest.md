# Project Cleanup Manifest

## Summary
- Delete candidates: 2 entries (cache patterns)
- Files archived: 9 (patch/orig/rej files)
- Status: BLOCKED_REVIEW_REQUIRED (Baseline Failure in tests blocking safe cleanup without modifying code rules)

## DELETE_SAFE (R2)
* `__pycache__/` and `.pytest_cache/` - Cleaned across repo
* `*.pyc` and `*.pyo` - Cleaned across repo

## ARCHIVE (R2)
* `ui/tabs/hunt_tab.py.orig` -> `docs/archive/scripts/hunt_tab.py.orig` (Patch artifact)
* `ui/tabs/hunt_tab.py.rej` -> `docs/archive/scripts/hunt_tab.py.rej` (Patch artifact)
* `tests/unit/test_target_bar_detector.py.orig` -> `docs/archive/scripts/test_target_bar_detector.py.orig` (Patch artifact)
* `tests/unit/test_target_bar_detector.py.rej` -> `docs/archive/scripts/test_target_bar_detector.py.rej` (Patch artifact)
* `patch_test_target_bar_detector_hwnd.py` -> `docs/archive/scripts/patch_test_target_bar_detector_hwnd.py` (One-off patch)
* `patch_test_publish_callback.py` -> `docs/archive/scripts/patch_test_publish_callback.py` (One-off patch)
* `patch_test_ocr_db_fallback.py` -> `docs/archive/scripts/patch_test_ocr_db_fallback.py` (One-off patch)
* `patch_conftest_dup.py` -> `docs/archive/scripts/patch_conftest_dup.py` (One-off script)
* `patch_conftest_mock.py` -> `docs/archive/scripts/patch_conftest_mock.py` (One-off script)

## BASELINE FAILURE EXPLANATION
- Found a critical syntax error (IndentationError: unexpected indent) in `lib/features/hunt/hunt_orchestrator.py` on line 153.
- The instructions state: "Nếu baseline không chạy được, ghi nhận failure nhưng vẫn được tiếp tục inventory; không dùng cleanup để che failure" and "Không được xóa hoặc sửa nội dung trong session này nếu chưa có task riêng: lib/".
- Since tests were failing from baseline and fixing it requires touching `lib/`, the final status for this batch is `BLOCKED_REVIEW_REQUIRED` due to `BASELINE_FAILURE`.
