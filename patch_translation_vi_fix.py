with open("lib/i18n/translations.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if i > 440:
        if "'target_card.status_idle': 'IDLE'," in line:
            lines[i] = line.replace("'IDLE'", "'IDLE'") # Keep it IDLE for now as it seems to be IDLE in EN but wait, EN is top, VI is bottom.
            # Let's use string replace carefully

content = "".join(lines)
# Top is EN, bottom is VI.
# Lines 18, 450:
