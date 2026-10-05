# MyBot

A Discord study-group bot built with [discord.py](https://discordpy.readthedocs.io/). It answers quick questions with OpenAI, does web research with cited sources via [Exa](https://exa.ai), runs per-channel Pomodoro timers, and adds a few moderation helpers.

## Features

| Command | What it does |
| --- | --- |
| `/hello` | Greets you. |
| `/send <text>` | Posts the text into the current channel. |
| `/joined [member]` | Shows when a member joined the server (defaults to you). |
| `/ask <question>` | Short (2–4 sentence) AI answer. 5-second per-user cooldown. |
| `/web <query> [depth] [public]` | Searches the web with Exa and summarizes the results with `[n]` citations. `basic` uses 3 sources, `deep` uses 6. |
| `/pomodoro_start <minutes>` | Starts a 1–180 minute timer in this channel and pings when it ends. |
| `/pomodoro_pause` / `/pomodoro_resume` | Pauses or resumes the channel's timer. |
| `/pomodoro_status` | Shows the time remaining. |
| `/pomodoro_cancel` | Stops the timer. |
| **Show Join Date** (right-click a member) | Shows that member's join date. |
| **Report To Moderators** (right-click a message) | Sends the message, with a jump link, to the moderator log channel. |

`/ask` and `/web` are optional. If `OPENAI_API_KEY` or `EXA_API_KEY` isn't set, the bot still starts and those commands reply that they aren't configured.

## Project structure

```
MyBot/
├── bot.py                     # Entry point: builds the client, registers commands, runs the bot
├── mybot/
│   ├── config.py              # Loads .env; IDs, model name, cost/length limits
│   ├── client.py              # MyClient: command tree + guild sync + on_ready
│   ├── utils.py               # Text helpers (trim, format_sources)
│   ├── commands/
│   │   ├── __init__.py        # register_all(): wires every command module to the tree
│   │   ├── general.py         # /hello, /send, /joined
│   │   ├── ai.py              # /ask, /web
│   │   ├── pomodoro.py        # /pomodoro_* commands and timer state
│   │   └── moderation.py      # Right-click context menu commands
│   └── services/
│       ├── openai_service.py  # OpenAI client, concise answers, cited summaries
│       └── exa_service.py     # Exa client, search + highlight fetching
├── requirements.txt
├── .env.example               # Template for your .env
└── .gitignore
```

To add a command, put it in the matching module under `mybot/commands/` (inside that module's `setup(tree)` function). For a new group of commands, create a new module with a `setup(tree)` function and add it to `MODULES` in `mybot/commands/__init__.py`.

## Setup

### 1. Prerequisites

- Python 3.10+
- A Discord application with a bot user ([Developer Portal](https://discord.com/developers/applications)). Invite it to your server with the `bot` and `applications.commands` scopes.

### 2. Install

```bash
git clone <your-repo-url>
cd MyBot
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure

Copy the template and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Your bot token. |
| `OPENAI_API_KEY` | No | Turns on `/ask` and the summaries for `/web`. |
| `OPENAI_MODEL` | No | Defaults to `gpt-4o-mini`. |
| `EXA_API_KEY` | No | Turns on `/web`. |
| `GUILD_ID` | No | Server the commands sync to. Defaults to the ID in `mybot/config.py`. |
| `REPORT_CHANNEL_ID` | No | Channel that receives reports. Defaults to the ID in `mybot/config.py`. |

> Never commit `.env`. It's already listed in `.gitignore`.

### 4. Run

```bash
python bot.py
```

You should see `Logged in as <bot name> (ID: ...)`. Commands are synced to `GUILD_ID` on startup, so they appear in that server right away.

## Notes

- Pomodoro timers live in memory, so restarting the bot clears them.
- Cost limits for the AI calls (input length, output tokens, number of sources) are in `mybot/config.py`.
