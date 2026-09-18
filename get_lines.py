with open("ui/views/icon_manager_frame.py", "r") as f:
    lines = f.readlines()
    start = 0
    end = 0
    for i, line in enumerate(lines):
        if "def _build_detail_form" in line:
            start = i
        if "def _build_usages_panel" in line:
            end = i
            break
    print("".join(lines[start:end]))
