with open("tests/unit/ui/test_monster_editor_info_tab.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")', '# pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")')

with open("tests/unit/ui/test_monster_editor_info_tab.py", "w", encoding="utf-8") as f:
    f.write(content)
