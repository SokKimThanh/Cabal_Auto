import re
with open("lib/features/hunt/hunt_config.py", "r") as f:
    content = f.read()

update_code_old = """def update_hunt_config(mutator_func):
    \"\"\"Thread-safe read-modify-write operation using a mutation callback.\"\"\"
    with _config_lock:
        cfg = load_hunt_config()
        if mutator_func(cfg) is not False:
            return save_hunt_config(cfg)
        return False
"""
update_code_new = """def update_hunt_config(mutator_func):
    \"\"\"Thread-safe read-modify-write operation using a mutation callback.\"\"\"
    import threading
    _config_lock = getattr(save_hunt_config, '_lock', threading.RLock())
    save_hunt_config._lock = _config_lock
    with _config_lock:
        cfg = load_hunt_config()
        if mutator_func(cfg) is not False:
            return save_hunt_config(cfg)
        return False
"""
content = content.replace(update_code_old, update_code_new)

with open("lib/features/hunt/hunt_config.py", "w") as f:
    f.write(content)
