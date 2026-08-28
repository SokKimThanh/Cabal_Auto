# UI Windows

Main window and dialog classes for the Cabal Auto Manager application.

## Modules

### auto_hunt.py
Auto hunt window for managing hunt configuration and execution.

### library_manager.py
Library manager dialog for managing monsters and skills libraries.

### overlay_window.py
Overlay window for displaying hunt information on top of the game.

### monster_manager_win.py
Quick monster editor dialog (Ctrl+Shift+M) for fast monster editing.

### setup_wizard.py
Setup wizard window for first-time configuration.

### setup_wizard_vision.py
Vision setup wizard for configuring detection regions.

### template_matcher.py
Template matcher dialog for testing and adjusting template matching.

## Migration from ui/ and lib/ui

All window modules have been consolidated into `ui/windows/` for better organization.

**Old imports (Historical / Removed):**
```python
from lib.ui.library_manager import LibraryManagerWindow  # Removed
from ui.monster_manager_win import MonsterManagerWin    # Removed
```

**New imports:**
```python
from ui.windows.library_manager import LibraryManagerWindow
from ui.windows.monster_manager_win import MonsterManagerWin
```
