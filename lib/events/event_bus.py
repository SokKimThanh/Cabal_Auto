from typing import Callable, Dict, List, Type


class Event:
    pass


class IconUpdatedEvent(Event):
    def __init__(self, icon_key: str):
        self.icon_key = icon_key


class IconManagerSyncEvent(Event):
    pass



class HuntStatusUpdatedEvent(Event):
    def __init__(self, status: str):
        self.status = status

class HuntStateChangedEvent(Event):
    def __init__(self, state: str):
        self.state = state

class TargetHpUpdatedEvent(Event):
    def __init__(self, hp_percent: float):
        self.hp_percent = hp_percent

class TargetStatusUpdatedEvent(Event):
    def __init__(self, status: str):
        self.status = status

class TargetInfoUpdatedEvent(Event):
    def __init__(self, info: str):
        self.info = info

class ClearTargetUIEvent(Event):
    pass

class SkillStatsUpdatedEvent(Event):
    def __init__(self, stats: dict):
        self.stats = stats

class SceneMonstersDetectedEvent(Event):
    def __init__(self, snapshot):
        self.snapshot = snapshot


class MonsterRotationUpdatedEvent(Event):
    def __init__(self, selected_index: int = None):
        self.selected_index = selected_index


class MonsterMoveUpEvent(Event):
    def __init__(self, index: int):
        self.index = index

class MonsterMoveDownEvent(Event):
    def __init__(self, index: int):
        self.index = index

class MonsterDeleteEvent(Event):
    def __init__(self, indices: List[int]):
        self.indices = indices


class MonsterAddSmartEvent(Event):
    def __init__(self, record: dict):
        self.record = record


class VisionScanRegionEvent(Event):
    pass

class VisionAddTemplateEvent(Event):
    pass

class VisionManageTemplatesEvent(Event):
    pass

class EventBus:
    _listeners: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    @classmethod
    def bind(cls, event_type: Type[Event], listener: Callable[[Event], None]) -> None:
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(listener)

    @classmethod
    def unbind(cls, event_type: Type[Event], listener: Callable[[Event], None]) -> None:
        if event_type in cls._listeners:
            try:
                cls._listeners[event_type].remove(listener)
            except ValueError:
                pass

    @classmethod
    def trigger(cls, event: Event) -> None:
        event_type = type(event)
        if event_type in cls._listeners:
            for listener in cls._listeners[event_type]:
                listener(event)

    @classmethod
    def clear(cls) -> None:
        """For testing purposes."""
        cls._listeners.clear()

class LanguageChangedEvent(Event):
    def __init__(self, lang: str):
        self.lang = lang

class GlobalApplyEvent(Event):
    pass

class StartStopHuntEvent(Event):
    pass
