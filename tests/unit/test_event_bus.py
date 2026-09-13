import pytest
from lib.events.event_bus import (
    EventBus,
    Event,
    SceneMonstersDetectedEvent,
    MonsterRotationUpdatedEvent
)

class DummyEvent(Event):
    pass

@pytest.fixture(autouse=True)
def clean_event_bus():
    """Ensure the EventBus is cleared before and after each test."""
    EventBus.clear()
    yield
    EventBus.clear()

def test_bind_and_trigger():
    calls = []
    def listener(event):
        calls.append(event)

    EventBus.bind(DummyEvent, listener)
    event_instance = DummyEvent()
    EventBus.trigger(event_instance)

    assert len(calls) == 1
    assert calls[0] is event_instance

def test_unbind_removes_listener():
    calls = []
    def listener(event):
        calls.append(event)

    EventBus.bind(DummyEvent, listener)
    EventBus.unbind(DummyEvent, listener)

    event_instance = DummyEvent()
    EventBus.trigger(event_instance)

    assert len(calls) == 0

def test_unbind_unregistered_listener():
    def listener(event):
        pass

    # Should not raise an exception
    EventBus.unbind(DummyEvent, listener)

    EventBus.bind(DummyEvent, listener)
    def another_listener(event):
        pass

    # Unbinding a listener that isn't bound for this event type
    # should not raise an exception
    EventBus.unbind(DummyEvent, another_listener)

def test_multiple_listeners():
    calls1 = []
    calls2 = []

    def listener1(event):
        calls1.append(event)

    def listener2(event):
        calls2.append(event)

    EventBus.bind(DummyEvent, listener1)
    EventBus.bind(DummyEvent, listener2)

    event_instance = DummyEvent()
    EventBus.trigger(event_instance)

    assert len(calls1) == 1
    assert len(calls2) == 1

    EventBus.unbind(DummyEvent, listener1)

    event_instance2 = DummyEvent()
    EventBus.trigger(event_instance2)

    assert len(calls1) == 1
    assert len(calls2) == 2

def test_scene_monsters_detected_event():
    calls = []
    def listener(event):
        calls.append(event)

    EventBus.bind(SceneMonstersDetectedEvent, listener)

    snapshot_data = {"image": "dummy_data"}
    event_instance = SceneMonstersDetectedEvent(snapshot=snapshot_data)
    EventBus.trigger(event_instance)

    assert len(calls) == 1
    assert isinstance(calls[0], SceneMonstersDetectedEvent)
    assert calls[0].snapshot == snapshot_data

def test_monster_rotation_updated_event():
    calls = []
    def listener(event):
        calls.append(event)

    EventBus.bind(MonsterRotationUpdatedEvent, listener)

    event_instance = MonsterRotationUpdatedEvent()
    EventBus.trigger(event_instance)

    assert len(calls) == 1
    assert isinstance(calls[0], MonsterRotationUpdatedEvent)
