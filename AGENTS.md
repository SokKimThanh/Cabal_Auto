
## Technical Debt to address in later refactoring loops (Icon Manager)
- `_build_icons_panel()` inside `IconManagerFrame` is too large (~150 lines) and should be broken down further.
- There is still a slight filesystem awareness around the save flow (checking `self.icon_helper.icon_dirs`) which should be further abstracted into the model or a dedicated service.
- Continue reducing responsibilities inside `IconManagerFrame` overall.
