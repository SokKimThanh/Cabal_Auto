# Sprint 32 - Prompt 05: Refactor IconManagerFrame Form State

## Context
We are refactoring `IconManagerFrame` to decouple UI rendering from business logic.

**Focus for this session:** Form State Management.

## Current State
The form state is managed by a monolithic `set_form_state("ADD" | "EDIT" | "VIEW")` method. This method uses conditional blocks (`if state == ...`) to enable/disable specific form entries and buttons.

## Goal
Replace the monolithic conditional state method with explicitly defined transition methods to improve readability and prevent state-related bugs.

## Requirements
1. **Create Explicit Methods:** Implement the following private methods in `IconManagerFrame`:
   - `_enter_add_mode()`
   - `_enter_edit_mode()`
   - `_enter_view_mode()`
2. **Move Logic:** Move the widget enable/disable logic from `set_form_state()` into these respective methods.
3. **Update Callers:** Replace all calls to `self.set_form_state("ADD")`, `self.set_form_state("EDIT")`, and `self.set_form_state("VIEW")` throughout the file with calls to the new explicit methods.
4. **Remove Monolith:** Delete the old `set_form_state` method.

## Output
Modify `ui/views/icon_manager_frame.py` to use the explicit state transition methods. Run tests after making the changes.
