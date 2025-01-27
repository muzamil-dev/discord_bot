discord_bot/
├── README.md
├── main.py
├── requirements.txt
├── structure.md
├── config/
│   ├── config.json
│   └── reminders.json
├── logs/
│   └── bot.log
└── src/
    ├── __init__.py
    ├── commands/
    │   ├── __init__.py
    │   ├── fun/
    │   │   ├── coin_command.py
    │   │   ├── dice_command.py
    |   |   ├── die_command.py
    │   │   ├── dox_command.py
    │   │   ├── meme_command.py
    |   |   ├── shoot_command.py
    │   │   └── spam_command.py
    │   ├── quotes/
    │   │   ├── inspire_command.py
    │   │   └── lotr_command.py
    │   ├── system/
    │   │   ├── list_commands.py
    │   │   └── toggle_commands.py
    │   └── utility/
    │       └── remind_command.py
    │       └── search_command.py
    ├── events/
    │   ├── __init__.py
    │   ├── error_handler.py
    │   ├── ready_handler.py
    │   └── messages/
    │       ├── hello_response.py
    │       ├── leetcode_response.py
    │       ├── message_router.py
    │       ├── millbot_responses.py
    │       ├── moonraku_handler.py
    │       └── sunraku_handler.py
    ├── features/
    │   ├── __init__.py
    │   └── reminder/
    │       └── reminder_manager.py
    └── utils/
        ├── __init__.py
        ├── api_client.py
        ├── llm.py
        └── state_manager.py