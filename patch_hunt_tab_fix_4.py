import re

with open("ui/tabs/hunt_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """        if hasattr(self.app, "skill_stats_tree"):
            self.app.skill_stats_tree.insert(
                "",
                "end",
                values=(self.app._t("skill_stats_empty"), "", "", "", ""),
                tags=("placeholder",),
            )"""

content = re.sub(r'        self\.app\._show_skill_stats_placeholder\(\)', replacement, content)

with open("ui/tabs/hunt_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
