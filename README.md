"""
This Discord bot is a multi-functional assistant with features such as YouTube audio playback, random meme generation, AI-powered text generation, user timeouts, and fun chat interactions. It leverages the Discord API, Hugging Face's GPT-Neo model, and various public APIs for its functionality.

The bot supports the following features:
- 🎶 **Play YouTube Audio**: Plays audio from YouTube videos in voice channels.
- 🤖 **AI-Powered Text Generation**: Generates responses using Hugging Face's GPT-Neo model.
- 😂 **Random Memes**: Fetches memes from a meme API.
- 🛑 **User Timeouts**: Temporarily mutes users for specified durations.
- 🎲 **Fun Commands**: Includes dice rolls, coin flips, and other interactive chat features.
- 🎄 **Seasonal Updates**: Updates bot status for special occasions like Christmas.

The bot requires Python 3.8 or later, the `discord.py` library, `youtube-dl` or `yt-dlp` for audio playback, and public APIs like Hugging Face and Meme API. It also requires a `.env` file to store sensitive data like bot tokens and API keys.
"""
# Discord Bot

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Bot](#running-the-bot)
7. [Commands](#commands)
8. [Contributing](#contributing)
9. [License](#license)

---

## Introduction
This Discord bot is a multi-functional assistant with features such as YouTube audio playback, random meme generation, AI-powered text generation, user timeouts, and fun chat interactions. It leverages the Discord API, Hugging Face's GPT-Neo model, and various public APIs for its functionality.

---

## Features
- 🎶 **Play YouTube Audio**: Plays audio from YouTube videos in voice channels.
- 🤖 **AI-Powered Text Generation**: Generates responses using Hugging Face's GPT-Neo model.
- 😂 **Random Memes**: Fetches memes from a meme API.
- 🛑 **User Timeouts**: Temporarily mutes users for specified durations.
- 🎲 **Fun Commands**: Includes dice rolls, coin flips, and other interactive chat features.
- 🎄 **Seasonal Updates**: Updates bot status for special occasions like Christmas.

---

## Requirements
- Python 3.8 or later
- `discord.py` library
- `youtube-dl` or `yt-dlp` for audio playback
- Public APIs like Hugging Face and Meme API
- `.env` file to store sensitive data like bot tokens and API keys

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo-name/discord-bot.git
   cd discord-bot
   ```

2. **Install Dependencies**:
   Install required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add the following:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   HUGGINGFACE_API_KEY=your_hugging_face_api_key
   ```

4. **Verify Installation**:
   Ensure all dependencies are installed and the `.env` file is properly configured.

---

## Configuration
1. **Bot Token**:
   - Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
   - Add the token to the `.env` file.

2. **Hugging Face API Key**:
   - Obtain your API key from [Hugging Face](https://huggingface.co/).
   - Add the key to the `.env` file.

3. **Voice Channel Permissions**:
   - Ensure your bot has the necessary permissions in your Discord server:
     - Manage Channels
     - Connect
     - Speak
     - Timeout Members (optional for timeout features)

---

## Running the Bot
1. Start the bot by running:
   ```bash
   python3 bot.py
   ```
2. The bot will log in and display its status in the console.

---

## Commands
Here’s a list of available commands and their usage:

| Command      | Description                                                                                     |
|--------------|-------------------------------------------------------------------------------------------------|
| `!llm`       | Generates a response using Hugging Face's GPT-Neo model. Example: `!llm Write a poem.`         |
| `!play`      | Plays YouTube audio in a voice channel. Example: `!play <YouTube URL>`                         |
| `!stop`      | Disconnects the bot from the voice channel.                                                    |
| `!timeout`   | Times out a user for a random duration. Example: `!timeout @username`                          |
| `!meme`      | Fetches and displays a random meme.                                                            |
| `!dice roll` | Rolls a dice and returns a random number between 1 and 6.                                      |
| `!coin flip` | Flips a coin and returns "Heads" or "Tails".                                                   |
| `!hello`     | Responds with a greeting.                                                                      |
| `!good night`| Responds with a good night message.                                                            |

---

## Contributing
We welcome contributions! If you'd like to contribute:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description of your changes.

---

## License
This project is open-source and available under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Troubleshooting
- **Bot not starting?** Check your `.env` file for the correct token and API keys.
- **Permissions error?** Ensure the bot has the required permissions in your server.
- **Dependencies issue?** Reinstall requirements with `pip install -r requirements.txt`.
