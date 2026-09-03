import re

with open("app_gui.py", "r") as f:
    content = f.read()

search = """    def _on_orchestrator_state_change(self, state: str):
        self.hunt_tab.update_hunt_status_color(state)"""

replace = """    def _on_orchestrator_state_change(self, state: str):
        self.hunt_tab.update_hunt_status_color(state)

        # Disable policy radios when running
        if hasattr(self.hunt_tab, 'policy_radios'):
            for rb in self.hunt_tab.policy_radios:
                if state == "running":
                    rb.config(state="disabled")
                else:
                    rb.config(state="normal")"""
content = content.replace(search, replace)
with open("app_gui.py", "w") as f:
    f.write(content)
