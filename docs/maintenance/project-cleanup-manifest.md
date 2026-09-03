# Cleanup Manifest

## Summary
- Delete candidates: 4 entries (3 files + 1 directory; safe artifacts)
- Files to archive: 51 (One-off scripts, patches, old reports)
- Expected bytes reclaimed: TBD
- Status: BLOCKED_REVIEW_REQUIRED (>20 candidates)

## DELETE_SAFE
* `__pycache__/` - Python cache directory (Safe)
* `app_gui.py.orig` - Git/patch artifact (Safe)
* `app_gui.py.rej` - Git/patch artifact (Safe)
* `out.txt` - Random output log (Safe)

## ARCHIVE
* `patch_app_gui_metadata.py` -> `docs/archive/scripts/patch_app_gui_metadata.py` (One-off script)
* `patch_app_gui_reorder.py` -> `docs/archive/scripts/patch_app_gui_reorder.py` (One-off script)
* `patch_auto_bring.diff` -> `docs/archive/scripts/patch_auto_bring.diff` (Patch file)
* `patch_concurrency_test.py` -> `docs/archive/scripts/patch_concurrency_test.py` (One-off test)
* `patch_concurrency_test2.py` -> `docs/archive/scripts/patch_concurrency_test2.py` (One-off test)
* `patch_first_time.diff` -> `docs/archive/scripts/patch_first_time.diff` (Patch file)
* `patch_geometry.diff` -> `docs/archive/scripts/patch_geometry.diff` (Patch file)
* `patch_hunt_config_mutation.py` -> `docs/archive/scripts/patch_hunt_config_mutation.py` (One-off script)
* `patch_hunt_tab_fix.py` -> `docs/archive/scripts/patch_hunt_tab_fix.py` (One-off script)
* `patch_hunt_tab_fix_2.py` -> `docs/archive/scripts/patch_hunt_tab_fix_2.py` (One-off script)
* `patch_hunt_tab_fix_3.py` -> `docs/archive/scripts/patch_hunt_tab_fix_3.py` (One-off script)
* `patch_hunt_tab_fix_4.py` -> `docs/archive/scripts/patch_hunt_tab_fix_4.py` (One-off script)
* `patch_main.diff` -> `docs/archive/scripts/patch_main.diff` (Patch file)
* `patch_migrator4.py` -> `docs/archive/scripts/patch_migrator4.py` (One-off script)
* `patch_monster_picker_headings.py` -> `docs/archive/scripts/patch_monster_picker_headings.py` (One-off script)
* `patch_monster_picker_int.py` -> `docs/archive/scripts/patch_monster_picker_int.py` (One-off script)
* `patch_monster_picker_map.py` -> `docs/archive/scripts/patch_monster_picker_map.py` (One-off script)
* `patch_monster_picker_minsize.py` -> `docs/archive/scripts/patch_monster_picker_minsize.py` (One-off script)
* `patch_rename_rotation.py` -> `docs/archive/scripts/patch_rename_rotation.py` (One-off script)
* `patch_rename_rotation2.py` -> `docs/archive/scripts/patch_rename_rotation2.py` (One-off script)
* `patch_test_fix.py` -> `docs/archive/scripts/patch_test_fix.py` (One-off script)
* `patch_test_priority.py` -> `docs/archive/scripts/patch_test_priority.py` (One-off script)
* `patch_test_queue.py` -> `docs/archive/scripts/patch_test_queue.py` (One-off script)
* `patch_tests.py` -> `docs/archive/scripts/patch_tests.py` (One-off script)
* `patch_tests_2.py` -> `docs/archive/scripts/patch_tests_2.py` (One-off script)
* `patch_tests_picker.py` -> `docs/archive/scripts/patch_tests_picker.py` (One-off script)
* `patch_try_close.diff` -> `docs/archive/scripts/` (Patch file)
* `fix_app.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_flake8.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_flake8_hunt_logger.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_flake8_hunt_tab.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_flake8_ui_style.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_tests.patch` -> `docs/archive/scripts/` (Patch file)
* `fix_win32gui_mock.patch` -> `docs/archive/scripts/` (Patch file)
* `test_concurrent_lock.py` -> `docs/archive/scripts/` (One-off script)
* `test_dpi_matrix.py` -> `docs/archive/scripts/` (One-off script)
* `test_log_queue.py` -> `docs/archive/scripts/` (One-off script)
* `test_parse_bug.py` -> `docs/archive/scripts/` (One-off script)
* `test_script.py` -> `docs/archive/scripts/` (One-off script)
* `test_target_bar.py` -> `docs/archive/scripts/` (One-off script)
* `run_app_smoke.py` -> `docs/archive/scripts/` (One-off script)
* `runner.py` -> `docs/archive/scripts/` (One-off script)
* `read_comments.py` -> `docs/archive/scripts/` (One-off script)
* `DATABASE_IMPLEMENTATION_SUMMARY.md` -> `docs/archive/docs/` (Completed doc, link to update: NONE)
* `OVERLAY_FIX.md` -> `docs/archive/docs/` (Completed doc, link to update: NONE)
* `REORGANIZATION_SUMMARY.md` -> `docs/archive/docs/` (Completed doc, link to update: NONE)
* `palette.md` -> `docs/archive/docs/` (Random info, link to update: NONE)
* `plan.md` -> `docs/archive/docs/` (Task info, link to update: NONE)
* `plan_review.md` -> `docs/archive/docs/` (Task info, link to update: NONE)
* `report.md` -> `docs/archive/docs/` (Task info, link to update: NONE)
* `db5a_audit_report.md` -> `docs/archive/db_audit/` (Audit report)

## KEEP
* `CHANGELOG.md` - Core project doc, 10 refs
* `CODING_RULES_QUICK_REFERENCE.md` - Core project doc, 9 refs
* `PROJECT_STRUCTURE.md` - Core project doc, 12 refs
* `README.md` - Core project doc, 189 refs
* `DATABASE_README.md` - Core documentation (keeping based on name and 3 refs)
* `app_gui.py` - Main app entrypoint
* `conftest.py` - Core test file
* `database.py` - Core app file
* `install_dependencies.bat` - Utility script
* `monsters.db` - SQLite DB
* `monsters.db.sql` - DB backup
* `pytest.ini` - Core configuration
* `requirements.txt` - Core configuration
* `run.bat` - App runner
* `db5_consolidated_manifest_v1.0.0.json` - Data file (Keeping per rules)
* `db5_mapping_manifest.json` - Data file (Keeping per rules)
* `db5a_audit_report.json` - Data file (Keeping per rules)

