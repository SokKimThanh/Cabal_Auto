import os
import re

with open('ui/controllers/app_state_controller.py', 'r') as f:
    content = f.read()

# I will leave _apply_monster_to_hunt_quick in MonsterManagerController, but it's called from where?
