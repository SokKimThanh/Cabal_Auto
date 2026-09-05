with open("app_gui.py", "r") as f:
    content = f.read()

# Let's fix the title rendering issue. The screenshot showed the title "Trợ lý săn Cabal" overlapping with itself.
# It seems there's no custom titlebar rendering in app_gui.py based on `self.overrideredirect(True)`.
# However, sometimes themes like `sv_ttk` or `pywinstyles` mess up the title bar.
# There's a `configure_ttk_styles` call.
pass
