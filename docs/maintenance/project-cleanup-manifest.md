# Project Cleanup Manifest

## KEEP
- script_checker.py (Reason: Config/tooling, Evidence: Standard tooling)
- runner.py (Reason: Runtime source or main entrypoint/tests, Evidence: Imported or main app)
- conftest.py (Reason: Runtime source or main entrypoint/tests, Evidence: Imported or main app)
- database.py (Reason: Runtime source or main entrypoint/tests, Evidence: Imported or main app)
- inventory_script.py (Reason: Config/tooling, Evidence: Standard tooling)
- app_gui.py (Reason: Runtime source or main entrypoint/tests, Evidence: Imported or main app)
- run_app_smoke.py (Reason: Runtime source or main entrypoint/tests, Evidence: Imported or main app)
- CHANGELOG.md (Reason: Main documentation, Evidence: Referenced in rules/README)
- CODING_RULES_QUICK_REFERENCE.md (Reason: Main documentation, Evidence: Referenced in rules/README)
- PROJECT_STRUCTURE.md (Reason: Main documentation, Evidence: Referenced in rules/README)
- README.md (Reason: Main documentation, Evidence: Referenced in rules/README)
- db5_consolidated_manifest_v1.0.0.json (Reason: Data files, Evidence: Do not delete data json in session)
- db5_mapping_manifest.json (Reason: Data files, Evidence: Do not delete data json in session)
- db5a_audit_report.json (Reason: Data files, Evidence: Do not delete data json in session)

## ARCHIVE
- patch_indent.py -> docs/archive/patch_indent.py (Links: None)
- patch_hunt_config_mutation.py -> docs/archive/patch_hunt_config_mutation.py (Links: None)
- test_script.py -> docs/archive/test_script.py (Links: None)
- test_parse_bug.py -> docs/archive/test_parse_bug.py (Links: None)
- test_concurrent_lock.py -> docs/archive/test_concurrent_lock.py (Links: None)
- patch_migrator4.py -> docs/archive/patch_migrator4.py (Links: None)
- patch_test_priority.py -> docs/archive/patch_test_priority.py (Links: None)
- patch_concurrency_test.py -> docs/archive/patch_concurrency_test.py (Links: None)
- test_target_bar.py -> docs/archive/test_target_bar.py (Links: None)
- test_log_queue.py -> docs/archive/test_log_queue.py (Links: None)
- test_dpi_matrix.py -> docs/archive/test_dpi_matrix.py (Links: None)
- patch_concurrency_test2.py -> docs/archive/patch_concurrency_test2.py (Links: None)
- OVERLAY_FIX.md -> docs/archive/OVERLAY_FIX.md (Links: Update PROJECT_STRUCTURE or other links if any)
- DATABASE_README.md -> docs/archive/DATABASE_README.md (Links: Update PROJECT_STRUCTURE or other links if any)
- DATABASE_IMPLEMENTATION_SUMMARY.md -> docs/archive/DATABASE_IMPLEMENTATION_SUMMARY.md (Links: Update PROJECT_STRUCTURE or other links if any)
- plan.md -> docs/archive/plan_archive.md (Links: Update PROJECT_STRUCTURE or other links if any)
- report.md -> docs/archive/report.md (Links: Update PROJECT_STRUCTURE or other links if any)
- palette.md -> docs/archive/palette.md (Links: Update PROJECT_STRUCTURE or other links if any)
- REORGANIZATION_SUMMARY.md -> docs/archive/REORGANIZATION_SUMMARY_root.md (Links: Update PROJECT_STRUCTURE or other links if any)
- plan_review.md -> docs/archive/plan_review.md (Links: Update PROJECT_STRUCTURE or other links if any)
- db5a_audit_report.md -> docs/archive/db5a_audit_report.md (Links: Update PROJECT_STRUCTURE or other links if any)
- fix_flake8_hunt_logger.patch -> docs/archive/fix_flake8_hunt_logger.patch (Links: None)
- fix_app.patch -> docs/archive/fix_app.patch (Links: None)
- patch_handlers.patch -> docs/archive/patch_handlers.patch (Links: None)
- fix_flake8.patch -> docs/archive/fix_flake8.patch (Links: None)
- fix_flake8_hunt_tab.patch -> docs/archive/fix_flake8_hunt_tab.patch (Links: None)
- fix_win32gui_mock.patch -> docs/archive/fix_win32gui_mock.patch (Links: None)
- fix_flake8_ui_style.patch -> docs/archive/fix_flake8_ui_style.patch (Links: None)
- fix_tests.patch -> docs/archive/fix_tests.patch (Links: None)
- patch_auto_bring.diff -> docs/archive/patch_auto_bring.diff (Links: None)
- patch_main.diff -> docs/archive/patch_main.diff (Links: None)
- patch_first_time.diff -> docs/archive/patch_first_time.diff (Links: None)
- patch_geometry.diff -> docs/archive/patch_geometry.diff (Links: None)
- patch_try_close.diff -> docs/archive/patch_try_close.diff (Links: None)
- app_gui.py.orig -> docs/archive/app_gui.py.orig (Links: None)
- app_gui.py.rej -> docs/archive/app_gui.py.rej (Links: None)

## DELETE_SAFE
- out.txt (Type: temporary, Reason: Command output log)

## DELETE_REVIEW
- read_comments.py (Type: temporary, Risk: Low, Decision: Need review to delete test script in root)

## UNKNOWN


## SUMMARY
- Total files scanned: 52 (Total bytes: ~500KB)
- Files to KEEP: 14
- Files to ARCHIVE: 36
- Files to DELETE_SAFE: 1
- Files to DELETE_REVIEW: 1
- Expected state after cleanup: 14 files kept in place, 36 moved to docs/archive/, 1 deleted, ~100KB freed/moved.
