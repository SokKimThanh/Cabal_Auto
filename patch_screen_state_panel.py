import re

with open('ui/panels/screen_state_panel.py', 'r') as f:
    content = f.read()

import_search = "from typing import Dict, Any"
import_replace = "from typing import Dict, Any\nfrom PIL import ImageTk, Image"
content = content.replace(import_search, import_replace)

ui_search = """        self.lbl_skills = self._create_label(self.container, t("setup.skills_found", default="✅ {count} skills valid").format(count=0))
        self.lbl_skills.grid(row=1, column=1, sticky="w", padx=4, pady=2)"""

ui_replace = """        self.lbl_skills = self._create_label(self.container, t("setup.skills_found", default="✅ {count} skills valid").format(count=0))
        self.lbl_skills.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self.lbl_scan_status = self._create_label(self.container, "⏳ Đang theo dõi...")
        self.lbl_scan_status.grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        self.lbl_thumbnail = tk.Label(self.container, bg=UI.BG_BASE)
        self.lbl_thumbnail.grid(row=3, column=0, columnspan=2, sticky="w", padx=4, pady=2)"""
content = content.replace(ui_search, ui_replace)

update_method = """    def update_thumbnail(self, thumbnail_img: Image.Image):
        \"\"\"Updates the thumbnail from a PIL image.\"\"\"
        if thumbnail_img:
            self._photo_img = ImageTk.PhotoImage(thumbnail_img)
            self.lbl_thumbnail.config(image=self._photo_img)
            self.lbl_scan_status.config(text="✅ Đã cập nhật scan")"""

content = content + "\n\n" + update_method

with open('ui/panels/screen_state_panel.py', 'w') as f:
    f.write(content)
