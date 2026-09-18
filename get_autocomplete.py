with open("ui/views/icon_manager_frame.py", "r") as f:
    lines = f.readlines()
    start = -1
    for i, line in enumerate(lines):
        if "def _autocomplete_tooltip" in line:
            start = i
            break

    if start != -1:
        end = start + 30
        print("".join(lines[start:end]))
