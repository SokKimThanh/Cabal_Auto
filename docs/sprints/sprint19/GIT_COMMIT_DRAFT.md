# Git Commit Draft

## Commit Message:

```
feat: Add Skill Rotation Builder UI (Sprint 19 Task #5 Phase 2)

Implement complete visual builder for precise skill rotation timing with
cooldown tracking and cast time calculations.

Features:
- Visual skill selection with checkboxes
- Drag-and-drop style sequence editor
- Real-time rotation timeline preview
- Precise cooldown tracking per skill
- Support for buff + attack skill mix
- Save/load rotation from hunt_config.json
- Second-by-second execution timeline

UI Components:
- Two-panel layout (Available Skills | Rotation Sequence)
- Move up/down/remove buttons for reordering
- Calculate button generates detailed timeline
- Apply button saves to hunt_config with execution preview

Technical:
- New module: lib/features/skill_rotation/
  - builder.py: Core calculation logic
  - ui_integration.py: Complete GUI implementation
  - __init__.py: Module exports
- Modified: lib/ui/library_manager.py
  - Added Tab 4: "🎮 Skill Rotation"
  - Integrated SkillRotationUI class

Documentation:
- docs/sprints/sprint19/TASK5_SKILL_ROTATION_BUILDER.md
- docs/sprints/sprint19/TASK5_PHASE2_COMPLETE.md
- docs/sprints/sprint19/SUMMARY_SKILL_ROTATION_UI_COMPLETE.md
- docs/sprints/sprint19/test_skill_rotation_ui.py

Example Output:
- Input: 3 skills (Dark Explosion, Regeneration, Bone Javelin)
- Calculated: 5.30s total cycle time
- Timeline: 0.00s → 1.80s → 2.90s → repeat
- Saved to hunt_config.json with complete rotation data

Next: Phase 3 - Auto Hunt Integration to execute rotation

Closes: #TASK5-PHASE2
```

## Files to Add:

```bash
git add lib/features/skill_rotation/
git add lib/ui/library_manager.py
git add docs/sprints/sprint19/TASK5_*.md
git add docs/sprints/sprint19/SUMMARY_*.md
git add docs/sprints/sprint19/test_skill_rotation_ui.py
```

## Or Add All:

```bash
git add -A
git commit -m "feat: Add Skill Rotation Builder UI (Sprint 19 Task #5 Phase 2)

Complete visual builder with:
- Visual skill selection & sequencing
- Precise cooldown/cast time tracking
- Real-time timeline preview
- Save to hunt_config.json

New module: lib/features/skill_rotation/
New tab: 🎮 Skill Rotation in Library Manager
Documentation: 4 new docs + test script

Example: 3-skill rotation → 5.30s cycle calculated

Next: Phase 3 Auto Hunt Integration"
```

## Verify Before Commit:

```bash
# Check what will be committed
git status

# Check diff
git diff --cached

# Verify no sensitive data
git diff --cached | grep -i "password\|secret\|token"

# Run tests
python docs/sprints/sprint19/test_skill_rotation_ui.py

# Test in app
python app_gui.py
# → Library Manager → Skill Rotation tab
```

## Alternative: Create Branch First

```bash
# Create feature branch
git checkout -b feature/skill-rotation-builder

# Add files
git add -A

# Commit
git commit -m "feat: Add Skill Rotation Builder UI"

# Push to remote
git push -u origin feature/skill-rotation-builder

# Create PR on GitHub
# Then merge to main after review
```
