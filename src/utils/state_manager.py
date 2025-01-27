import json

CONFIG_FILE_PATH = 'config/config.json'

def load_config():
    try:
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {}

_toggle_sunraku = load_config().get('TOGGLE_SUNRAKU', False)

def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def get_chat_mode():
    config = load_config()
    return config.get('CHAT_MODE', False)

def set_chat_mode(value):
    # Only updates in-memory state
    pass

def get_reece_enable():
    config = load_config()
    return config.get('REECE_ENABLE', False)

def set_reece_enable(value):
    config = load_config()
    config['REECE_ENABLE'] = value
    save_config(config)

def get_toggle_bot():
    config = load_config()
    return config.get('TOGGLE_BOT', True)

def set_toggle_bot(value):
    config = load_config()
    config['TOGGLE_BOT'] = value
    save_config(config)

def get_toggle_sunraku():
    global _toggle_sunraku
    return _toggle_sunraku

def set_toggle_sunraku(value):
    global _toggle_sunraku
    _toggle_sunraku = value