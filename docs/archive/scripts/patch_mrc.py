with open("lib/ui/controllers/monster_rotation_controller.py", "r") as f:
    content = f.read()

new_methods = """
    def load_monster_rotation_list(self):
        saved_list = self.state_controller.hunt_cfg.get("monster_rotation", [])
        self.state_controller.monster_rotation = []
        for item in saved_list:
            if isinstance(item, dict):
                self.state_controller.monster_rotation.append(
                    {
                        "monster_id": item.get("monster_id", 0),
                        "name": item.get("name", ""),
                        "priority": item.get("priority", 1),
                        "dungeon_id": item.get("dungeon_id", None),
                    }
                )

    def refresh_monster_select_options(self, select_name=None):
        pass

    def update_monster_frame_title(self):
        pass

    def on_monster_select_change(self, *args, **kwargs):
        pass

    def on_monster_apply_from_select(self, *args, **kwargs):
        pass

    def on_monster_use_for_hunt(self, *args, **kwargs):
        pass
"""
content += new_methods

with open("lib/ui/controllers/monster_rotation_controller.py", "w") as f:
    f.write(content)
