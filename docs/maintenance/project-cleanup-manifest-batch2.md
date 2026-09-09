# Project Cleanup Manifest - Batch 2

## Scope
Duplicate test scripts in `tests/` (causing pytest import file mismatch errors), unreferenced old examples, and obsolete scripts in `scripts/`.

## KEEP (Runtime / Setup / Source / Test Evidence)
| Path | Reason | Evidence |
|------|--------|----------|
| `scripts/main*.py` | Sample CLI runners | Referenced in `docs/` and `scripts/README.md`. |
| `scripts/migrate_translations_to_db.py` | DB Migration | Used in i18n instructions. |
| `scripts/run_cleanup_sessions.py` | Utility | Part of Sprint 26 workflow. |
| `scripts/cleanup_and_verify.py` | Utility | Part of Sprint 26 workflow. |

## ARCHIVE (Move to `docs/archive/`)
| Source Path | Destination Path | Details / Links |
|-------------|------------------|-----------------|
| `scripts/tài liệu mô tả vấn đề an toàn trong chạy file.txt` | `docs/archive/findings/tài_liệu_mô_tả_vấn_đề_an_toàn.txt` | Conversational log of CV error, belongs in findings. |

## DELETE_SAFE (Duplicate Tests & Unreferenced Scripts)
| Path | Artifact Type | Reason for Safety |
|------|---------------|-------------------|
| `tests/test_refresh_button_fix.py` | root test script | Unreferenced root test. |
| `tests/test_ui_style_migration.py` | root test script | Unreferenced root test, already run and legacy. |
| `tests/test_hunt_orchestrator.py` | duplicate test | Duplicate of `tests/integration/features/hunt/test_hunt_orchestrator.py` (legacy version). |
| `tests/test_preset_integration.py` | root test script | Failing legacy test (uses master= kwarg with mock_tk). |
| `tests/sprints/sprint22/test_training_mode.py` | duplicate test | Duplicate of `tests/integration/test_training_mode.py`. |
| `tests/sprints/sprint23/test_overlay_window_old.py` | duplicate test | Duplicate of `tests/integration/ui/test_overlay_window_old.py`. |
| `tests/sprints/sprint23/test_phase8_simple.py` | duplicate test | Duplicate of `tests/unit/features/hunt/test_phase8_simple.py`. |
| `tests/sprints/sprint23/test_screen_capture.py` | duplicate test | Duplicate of `tests/integration/vision/test_screen_capture.py`. |
| `tests/sprints/sprint23/test_vision_integration.py` | duplicate test | Duplicate of `tests/integration/vision/test_vision_integration.py`. |
| `tests/sprints/sprint23/test_window_manager.py` | duplicate test | Duplicate of `tests/integration/system/test_window_manager.py`. |
| `tests/unit/features/hunt/test_orchestrator_ocr_fallback.py` | duplicate test | Duplicate/legacy version of `tests/integration/features/hunt/test_orchestrator_ocr_fallback.py` causing pytest import mismatch. |
| `scripts/convert_training_tests.py` | one-off script | Unreferenced. |
| `scripts/test_delete_sync.py` | one-off script | Example/test script for SyncManager (legacy). |
| `scripts/test_editor_autocreate.py` | one-off script | Unreferenced. |
| `scripts/test_sync_manager.py` | one-off script | Example/test script for SyncManager (legacy). |
| `scripts/manual_state_migration_check.py` | one-off script | Unreferenced. |

## DELETE_REVIEW
None.

## UNKNOWN
None.

## Summary
- **Before:** 16 duplicate tests / scripts / docs scattered.
- **After (Expected):** Reduced by 16 files (15 deleted, 1 archived).
