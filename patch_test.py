with open("tests/integration/test_orchestrator_loop.py", "r") as f:
    content = f.read()

content = content.replace(
    "schedule_ui_task=schedule",
    "schedule_ui_task=schedule,\n        prepare_skill_runtime=MagicMock(),\n        try_cast_skills=MagicMock()"
)

with open("tests/integration/test_orchestrator_loop.py", "w") as f:
    f.write(content)
