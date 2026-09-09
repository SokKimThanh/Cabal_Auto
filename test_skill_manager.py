import tkinter as tk
import sys
import os

# Ensure lib and ui are accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from ui.views.skill_manager_frame import SkillManagerFrame

def test_skill_manager_pagination_and_filter():
    root = tk.Tk()
    class MockApp:
        def __init__(self):
            self.db_skill_service = MockSkillService()
            self.db_class_service = MockClassService()
        def _t(self, key, default=None):
            return default or key

    class MockSkillService:
        def get_total_skills_count(self, class_id=None, skill_type=None, search_text=None):
            if search_text == "Fire":
                return 5
            return 45

        def get_skills_by_filter(self, class_id=None, skill_type=None, search_text=None, limit=20, offset=0):
            return [{"skill_id": i, "name": f"Skill {i}"} for i in range(offset, min(offset+limit, self.get_total_skills_count(class_id, skill_type, search_text)))]

    class MockClassService:
        def get_all_classes(self):
            return [{"class_id": 1, "name": "Warrior"}, {"class_id": 2, "name": "Mage"}]

    app = MockApp()
    frame = SkillManagerFrame(root, app=app)

    # Test initialization
    assert frame.current_page == 1
    assert frame.total_pages == 3  # 45 / 20 = 2.25 -> 3
    assert len(frame.skills) == 20
    assert frame.page_lbl.cget("text") == "1 / 3"

    # Test next page
    frame._next_page()
    assert frame.current_page == 2
    assert frame.page_lbl.cget("text") == "2 / 3"
    assert len(frame.skills) == 20
    assert frame.skills[0]["skill_id"] == 20

    # Test next page again
    frame._next_page()
    assert frame.current_page == 3
    assert frame.page_lbl.cget("text") == "3 / 3"
    assert len(frame.skills) == 5

    # Test previous page
    frame._prev_page()
    assert frame.current_page == 2

    # Test filter
    frame.search_var.set("Fire")
    frame._on_filter_changed()
    assert frame.current_page == 1
    assert frame.total_pages == 1
    assert len(frame.skills) == 5

    root.destroy()
    print("Test passed!")

if __name__ == "__main__":
    test_skill_manager_pagination_and_filter()
