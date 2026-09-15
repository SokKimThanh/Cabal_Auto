# Project Cleanup Manifest (R2)

## DELETE_SAFE

| Path | Artifact Type | Safety Reason |
|---|---|---|
| `__pycache__/` | Cache | Python bytecode cache, safely auto-regenerated. |
| `.pytest_cache/` | Cache | Pytest test cache, safely auto-regenerated. |
| `*.pyc` | Cache | Python compiled files, safely auto-regenerated. |
| `*.pyo` | Cache | Python optimized compiled files, safely auto-regenerated. |

## ARCHIVE_CANDIDATE

| Source Path | Destination Path | Reason & Links to Update |
|---|---|---|
| `./patch_*.py` (23 files) | `docs/archive/scripts/` | Obsolete patching scripts from previous refactors. To be moved to archive script folder. |

## Summary

* Pre-cleanup state identified multiple bytecode caches and old root level patch scripts.
* Planned to delete all `__pycache__` and `*.pyc` files.
* Planned to archive 23 `patch_*.py` files in root.
