with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

content = content.replace('lbl.config(text=f"⚡ {cast_str} | ⏳ {cd_str}")',
                          'lbl.config(text=f"C: {cast_str} | CD: {cd_str}")')

content = content.replace('text="⚡ --s | ⏳ --s"',
                          'text="C: --s | CD: --s"')

with open("ui/tabs/hunt_tab.py", "w") as f:
    f.write(content)
