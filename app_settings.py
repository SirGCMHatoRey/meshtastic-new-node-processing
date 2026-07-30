import os
import json

DEFAULT_WELCOME_MESSAGE = "Welcome to the mesh!"
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')


def load_settings():
    """Load settings from the settings.json file."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"welcome_message": DEFAULT_WELCOME_MESSAGE}


def set_welcome_message(new_message):
    """Write a new welcome message to settings.json."""
    settings = load_settings()
    settings['welcome_message'] = new_message
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=2)
