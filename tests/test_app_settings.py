import json

import app_settings


def test_load_settings_missing_file_returns_default(tmp_path, monkeypatch):
    monkeypatch.setattr(app_settings, "SETTINGS_FILE", str(tmp_path / "settings.json"))

    assert app_settings.load_settings() == {"welcome_message": app_settings.DEFAULT_WELCOME_MESSAGE}


def test_set_welcome_message_writes_and_persists(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(app_settings, "SETTINGS_FILE", str(settings_file))

    app_settings.set_welcome_message("Hello mesh!")

    assert json.loads(settings_file.read_text()) == {"welcome_message": "Hello mesh!"}
    assert app_settings.load_settings()["welcome_message"] == "Hello mesh!"


def test_set_welcome_message_preserves_other_keys(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"welcome_message": "old", "other_key": 1}))
    monkeypatch.setattr(app_settings, "SETTINGS_FILE", str(settings_file))

    app_settings.set_welcome_message("new")

    assert json.loads(settings_file.read_text()) == {"welcome_message": "new", "other_key": 1}
