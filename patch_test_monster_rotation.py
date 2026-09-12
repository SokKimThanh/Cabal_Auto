with open('tests/integration/features/hunt/test_monster_rotation_queue.py', 'r') as f:
    content = f.read()

content = content.replace("mock_app.rotation_mode_var = MagicMock()", "mock_app.state_controller = MagicMock()\n    mock_app.state_controller.ui_vars = {'rotation_mode': MagicMock()}\n    mock_app.state_controller.ui_vars['rotation_mode'].get.return_value = 'Priority'\n    mock_app.rotation_mode_var = MagicMock()")
content = content.replace("assert mock_app.hunt_cfg[\"rotation_mode\"] == \"priority\"", "assert mock_app.state_controller.hunt_cfg[\"rotation_mode\"] == \"priority\"")
content = content.replace("mock_app.hunt_cfg = {}", "mock_app.state_controller.hunt_cfg = {}")

with open('tests/integration/features/hunt/test_monster_rotation_queue.py', 'w') as f:
    f.write(content)
