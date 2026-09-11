import sys

with open("app_gui.py", "r") as f:
    content = f.read()

search = """            (
                "btn_class_manager",
                lambda: self.switch_view("class_manager"),
                UI.FONT_SECTION,
                "class_manager",
                "shield",
            ),"""

replace = """            (
                "btn_class_manager",
                lambda: self.switch_view("class_manager"),
                UI.FONT_SECTION,
                "class_manager",
                "shield",
            ),
            (
                "btn_icon_manager",
                lambda: self.switch_view("icon_manager"),
                UI.FONT_SECTION,
                "icon_manager",
                "📁",
            ),"""

if search in content:
    content = content.replace(search, replace)
    with open("app_gui.py", "w") as f:
        f.write(content)
    print("Patch successful!")
else:
    print("Search string not found.")
