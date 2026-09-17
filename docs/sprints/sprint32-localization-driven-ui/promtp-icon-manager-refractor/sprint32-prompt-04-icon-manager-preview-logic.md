# Sprint 32 - Prompt 04: Refactor IconManagerFrame Preview Logic

## Context
We are refactoring `IconManagerFrame` to decouple UI rendering from business logic.

**Focus for this session:** Grouping Preview Rendering Logic.

## Current State
Preview logic might be scattered across different handlers (`_on_tree_select`, `_on_browse_clicked`, etc.), sometimes manually calling `.config(image=...)` or recreating tooltips.

## Goal
Centralize all preview rendering into a single method.

## Requirements
1. **Single Entry Point:** Ensure `_render_preview(icon_data)` is the ONLY place where the preview label (`self.lbl_preview`) is updated with an image or emoji.
2. **Refactor Callers:** Check the rest of `ui/views/icon_manager_frame.py`. If there are random places configuring the preview label manually, replace them with a call to `self._render_preview(icon_data)`.
3. **Empty States:** Ensure `_render_preview({})` correctly handles an empty state (hiding the preview label and showing the empty state frame).

## Output
Modify `ui/views/icon_manager_frame.py` to strictly use `_render_preview(icon_data)`. Run tests after making the changes.
