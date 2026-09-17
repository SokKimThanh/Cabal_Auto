# Sprint 32 - Prompt 01: Refactor IconManagerFrame Import Logic

## Context
We are refactoring `IconManagerFrame` to decouple UI rendering from business logic. The backend logic is being moved to `ImageLibraryModel` and `IconTreeModel`.

**Focus for this session:** Import Image Logic.

## Current State
The `IconManagerFrame` contains a monolithic method `_on_browse_clicked()` that handles:
- File selection dialog
- Checking if the file is outside the `assets` folder
- Prompting to copy or overwrite
- Copying the file using `shutil` or `icon_file_manager`
- Checking the database for `icon_key` duplication
- Invalidating caches
- Updating the UI

## Goal
Delegate all file handling, validation, and copying to `ImageLibraryModel`.

## Requirements
1. **Unify Import Flow:** Currently, there are two entry points for importing images: `_on_browse_clicked()` and `_on_import_image_clicked()`. Both must delegate to `self.image_model.import_image(...)`. There should be no duplicate business logic.
2. **Remove File Operations from UI:** Remove all direct usages of `os.path.exists`, `shutil.copy`, `copy2`, or `Path.glob` for import/copying purposes inside `IconManagerFrame`.
3. **Use the Model:** Ensure `_on_browse_clicked()` or `_on_import_image_clicked()` only handles the UI dialogs (`filedialog`, `messagebox`) and then calls `self.image_model.import_image()`.
4. **Update Previews:** After a successful import, only the UI state (e.g. `var_filepath`, `_is_dirty`) and the preview should be updated.

## Output
Modify `ui/views/icon_manager_frame.py` to satisfy the requirements. Run tests after making the changes to ensure no syntax errors.
