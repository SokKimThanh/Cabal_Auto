import pytest
from lib.system.task_scheduler import TaskScheduler

class MockTk:
    def __init__(self):
        self.after_calls = []
        self.cancel_calls = []
        self.timer_id = 0

    def after(self, ms, func):
        self.timer_id += 1
        tid = f"after#{self.timer_id}"
        self.after_calls.append((ms, func, tid))
        return tid

    def after_cancel(self, tid):
        self.cancel_calls.append(tid)

def test_task_scheduler_schedule_one_off():
    root = MockTk()
    scheduler = TaskScheduler(root)

    mock_called = []
    def callback():
        mock_called.append(True)

    scheduler.schedule_task("test_task", 100, callback, recurring=False)
    assert "test_task" in scheduler._after_tasks
    assert len(root.after_calls) == 1

    ms, func, tid = root.after_calls[0]
    assert ms == 100

    # execute the wrapper
    func()
    assert len(mock_called) == 1
    # execution should NOT schedule the next iteration
    assert len(root.after_calls) == 1
    assert "test_task" not in scheduler._after_tasks

def test_task_scheduler_schedule_recurring():
    root = MockTk()
    scheduler = TaskScheduler(root)

    mock_called = []
    def callback():
        mock_called.append(True)

    scheduler.schedule_recurring_task("test_task", 100, callback)
    assert "test_task" in scheduler._after_tasks
    assert len(root.after_calls) == 1

    ms, func, tid = root.after_calls[0]

    # execute the wrapper
    func()
    assert len(mock_called) == 1
    # execution should schedule the next iteration
    assert len(root.after_calls) == 2

def test_task_scheduler_schedule_no_id():
    root = MockTk()
    scheduler = TaskScheduler(root)

    task_id = scheduler.schedule_task(None, 100, lambda: None, recurring=False)
    assert task_id is not None
    assert task_id in scheduler._after_tasks
