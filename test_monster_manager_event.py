from lib.features.monster_manager import MonsterManager

def test_events():
    manager = MonsterManager()

    # State tracking
    called = []

    def my_callback(val):
        called.append(val)

    manager.register_callback("test_event", my_callback)

    manager._emit_event("test_event", 42)

    assert called == [42], f"Expected [42], got {called}"
    print("Test passed!")

if __name__ == "__main__":
    test_events()
