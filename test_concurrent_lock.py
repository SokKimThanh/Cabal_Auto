import threading
import time
from lib.features.hunt import hunt_config
import pytest

def test_config_concurrency(tmp_path, monkeypatch):
    config_file = tmp_path / "hunt_config.json"

    # Patch HUNT_CONFIG_PATH for this test only.
    monkeypatch.setattr(hunt_config, "HUNT_CONFIG_PATH", config_file)

    # Init file
    hunt_config.save_hunt_config({"schema_version": 3, "counter": 0})

    def writer_thread(increments):
        for _ in range(increments):
            def increment_counter(cfg):
                cfg["counter"] = cfg.get("counter", 0) + 1
                return cfg

            hunt_config.update_hunt_config(increment_counter)

    threads = []
    for _ in range(5):
        t = threading.Thread(target=writer_thread, args=(20,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    final_cfg = hunt_config.load_hunt_config()
    assert final_cfg["counter"] == 100
