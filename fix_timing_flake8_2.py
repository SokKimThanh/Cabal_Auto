with open("ui/windows/timing_calc_dialog.py", "r") as f:
    text = f.read()

import re
text = re.sub(r'f"(.*?)\n"', r'f"\1\\n"', text)

with open("ui/windows/timing_calc_dialog.py", "w") as f:
    f.write(text)
