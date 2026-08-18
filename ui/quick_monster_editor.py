"""Backward compatibility alias module for ui.quick_monster_editor."""
import sys
from ui.windows import quick_monster_editor
from ui.windows.quick_monster_editor import *

sys.modules['ui.quick_monster_editor'] = quick_monster_editor
