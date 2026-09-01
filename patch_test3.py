with open("tests/integration/test_orchestrator_loop.py", "r") as f:
    content = f.read()

# Instead of monkeypatching the module directly which we faked, patch it as a MagicMock attribute
# or just mock sys.modules completely
content = content.replace(
    'monkeypatch.setattr("lib.features.hunt.window_selection_service.validate_selected_cabal_window", lambda x, y: mock_validation)',
    'sys.modules["lib.features.hunt.window_selection_service"].validate_selected_cabal_window = lambda x, y: mock_validation'
)

with open("tests/integration/test_orchestrator_loop.py", "w") as f:
    f.write(content)
