from project import get_extension_paths, validate_config_exists, setup_logging

def test_validate_config_exists():
    assert validate_config_exists("config.py")
    assert not validate_config_exists("non_existent.py")

def test_get_extension_paths(tmp_path):
    d = tmp_path / "cogs"
    d.mkdir()
    (d / "commands.py").write_text(" ")
    (d / "events.py").write_text(" ")
    
    paths = get_extension_paths(directory=str(d))
    assert any("commands" in p for p in paths)
    assert len(paths) == 2

def test_setup_logging():
    assert setup_logging()