import json

# This is probably not the best way to go about changing variable data without chaning it inside config file

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize state variables with values from config.json
REECE_ENABLE = config.get("REECE_ENABLE", False)
CHAT_MODE = config.get("CHAT_MODE", False)

def get_reece_enable():
    global REECE_ENABLE
    return REECE_ENABLE

def set_reece_enable(value):
    global REECE_ENABLE
    REECE_ENABLE = value

def get_chat_mode():
    global CHAT_MODE
    return CHAT_MODE

def set_chat_mode(value):
    global CHAT_MODE
    CHAT_MODE = value