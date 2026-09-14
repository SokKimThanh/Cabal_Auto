import logging

logger = logging.getLogger(__name__)

class EventDispatcher:
    """
    Hệ thống bưu tá: Nhận đăng ký theo dõi sự kiện và gửi thông báo khi sự kiện xảy ra.
    Chịu trách nhiệm hoàn toàn cho logic _callbacks, register_callback, và emit.
    """
    def __init__(self):
        self._callbacks = {}

    def register_callback(self, event: str, handler) -> None:
        if event not in self._callbacks:
            self._callbacks[event] = []
        if handler not in self._callbacks[event]:
            self._callbacks[event].append(handler)

    def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._callbacks:
            for handler in self._callbacks[event]:
                try:
                    handler(*args, **kwargs)
                except Exception:
                    logger.exception("Error in callback for %s", event)
