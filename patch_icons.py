with open("ui/helpers/icon_helper.py", "r", encoding="utf-8") as f:
    content = f.read()

new_icons = """        self.icon_map = {
            'add': ('add.ico', '➕'),
            'accept': ('accept.ico', '✔️'),  # Accept icon for training mode
            'locked': ('locked.ico', '🔒'),  # Locked icon for training mode
            'edit': ('edit.ico', '✏️'),
            'delete': ('delete.ico', '🗑️'),
            'save': ('save.ico', '💾'),
            'cancel': ('cancel.ico', '✖'),
            'folder': ('folder.ico', '📁'),
            'capture': ('capture.png', '📸'),
            'search': ('search.ico', '🔍'),
            'refresh': ('refresh.ico', '🔄'),
            'start': ('start.ico', '▶️'),
            'stop': ('stop.ico', '⏹️'),
            'pause': ('pause.ico', '⏸️'),
            'minimize': ('minimize.ico', '➖'),
            'support': ('support.ico', '🧙'),
            'next': ('next.ico', '→'),
            'previous': ('previous.ico', '←'),
            'preview': ('preview.ico', '👁️'),
            'monster': ('monster.png', '👹'),
            'skill': ('skill.ico', '⚔️'),
            'template': ('template.png', '🖼️'),
            'list': ('list.ico', '🗂️'),
            'info': ('info.ico', '📋'),
            'time': ('time.ico', '⏱️'),
            'hp': ('hp.ico', '❤️'),
            'damage': ('damage.ico', '⚔️'),
            'priority': ('priority.ico', '🎯'),
            'question': ('question_mark.ico', '❓'),
            'up': ('up.ico', '↑'),
            'id': ('id.png', '🔑'),
            'speed': ('speed.png', '⚡'),
            'shield': ('shield.png', '🛡️'),
            'aim': ('aim.png', '🎯'),
            'dungeon': ('dungeon.png', '🏰'),
            'boss': ('boss.png', '👑'),"""

content = content.replace("        self.icon_map = {\n            'add': ('add.ico', '➕'),\n            'accept': ('accept.ico', '✔️'),  # Accept icon for training mode\n            'locked': ('locked.ico', '🔒'),  # Locked icon for training mode\n            'edit': ('edit.ico', '✏️'),\n            'delete': ('delete.ico', '🗑️'),\n            'save': ('save.ico', '💾'),\n            'cancel': ('cancel.ico', '✖'),\n            'folder': ('folder.ico', '📁'),\n            'capture': ('capture.png', '📸'),\n            'search': ('search.ico', '🔍'),\n            'refresh': ('refresh.ico', '🔄'),\n            'start': ('start.ico', '▶️'),\n            'stop': ('stop.ico', '⏹️'),\n            'pause': ('pause.ico', '⏸️'),\n            'minimize': ('minimize.ico', '➖'),\n            'support': ('support.ico', '🧙'),\n            'next': ('next.ico', '→'),\n            'previous': ('previous.ico', '←'),\n            'preview': ('preview.ico', '👁️'),\n            'monster': ('monster.png', '👹'),\n            'skill': ('skill.ico', '⚔️'),\n            'template': ('template.png', '🖼️'),\n            'list': ('list.ico', '🗂️'),\n            'info': ('info.ico', '📋'),\n            'time': ('time.ico', '⏱️'),\n            'hp': ('hp.ico', '❤️'),\n            'damage': ('damage.ico', '⚔️'),\n            'priority': ('priority.ico', '🎯'),\n            'question': ('question_mark.ico', '❓'),\n            'up': ('up.ico', '↑'),", new_icons)

with open("ui/helpers/icon_helper.py", "w", encoding="utf-8") as f:
    f.write(content)
