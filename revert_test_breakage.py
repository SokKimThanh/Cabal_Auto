import re

with open('ui/tabs/setup_tab.py', 'r', encoding='utf-8') as f:
    content = f.read()

# revert setup_tab font checking errors
content = content.replace("font=(UIStyle.resolve_font_family('body'), 10)", "font=UIStyle.FONT_LABEL")
content = content.replace("font=(UIStyle.resolve_font_family('display'), 11, 'bold')", "font=UIStyle.FONT_SECTION")
content = content.replace("font=(UIStyle.resolve_font_family('body'), 9)", "font=UIStyle.FONT_SMALL")
content = content.replace("font=(UIStyle.resolve_font_family('body'), 10, 'bold')", "font=UIStyle.FONT_BUTTON")

with open('ui/tabs/setup_tab.py', 'w', encoding='utf-8') as f:
    f.write(content)
