# Sprint 32 - Prompt 02: Refactor IconManagerFrame Scan & Search Logic

## Context
We are refactoring `IconManagerFrame` to decouple UI rendering from business logic. The backend logic is being moved to `ImageLibraryModel` and `IconTreeModel`.

**Focus for this session:** Image Scan and Search Logic.

## Current State
If `IconManagerFrame` directly accesses the filesystem to scan for images or perform search filtering on those images, it needs to be refactored. (Note: Currently, some of this might already be partially implemented in `ImageLibraryModel`, but we need to ensure the UI frame is completely clean).

## Goal
Delegate all directory scanning and image searching to `ImageLibraryModel`.

## Requirements
1. **Scan Library:** Ensure that populating the image listbox is done via `self.image_model.scan_async()`. The frame should only provide a callback to update the UI once the scan is complete.
2. **Search Library:** Ensure that filtering the image list is done via `self.image_model.search(query)`. The frame should only handle the `StringVar` trace, debounce the input, and call the model.
3. **Remove UI Scan Logic:** Ensure methods like `_scan_image_folder()`, `_search_images()`, or `_refresh_images()` (if they exist in the frame and manipulate the filesystem directly) are removed or refactored.

## Output
Modify `ui/views/icon_manager_frame.py` to ensure all scan/search responsibilities belong to `ImageLibraryModel`. Run tests after making the changes.
