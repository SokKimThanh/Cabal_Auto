with open("ui/components/compact_window_selector.py", "r") as f:
    content = f.read()

content = content.replace("self.root._t", "getattr(self.root, '_t', lambda x, **kwargs: x)")

with open("ui/components/compact_window_selector.py", "w") as f:
    f.write(content)
