"""Central config: loads .env once and exposes every setting/limit the bot uses."""
import os

from dotenv import load_dotenv

load_dotenv()

# ---- discord ----
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# guild the slash commands are synced to (guild sync is instant, global sync can take ~1h)
GUILD_ID = int(os.getenv("GUILD_ID") or "1415867953152262188")

# channel that "Report To Moderators" posts into
REPORT_CHANNEL_ID = int(os.getenv("REPORT_CHANNEL_ID") or "1422635688393703455")

# ---- openAI (Q&A, summaries) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"  # cheap + capable
SYSTEM_CONCISE = (
    "You are a concise study coach. Answer in 2–4 short sentences. "
    "No preamble, no disclaimers, no markdown headers."
)
MAX_INPUT_CHARS   = 600     # ~150 tokens in; keeps costs tiny
MAX_OUTPUT_TOKENS = 160     # hard cap on output length
ASK_COOLDOWN      = 5.0     # seconds per-user

# ---- exa (search) ----
EXA_API_KEY = os.getenv("EXA_API_KEY")

#Exa summarizer limits (keeps costs low)
EXA_MAX_RESULTS_BASIC = 3
EXA_MAX_RESULTS_DEEP  = 6
EXA_HIGHLIGHTS_PER_URL = 3           # how many highlight snippets to pull per URL
EXA_HIGHLIGHT_CHAR_CAP = 450         # cap each highlight (safety)
EXA_TOTAL_CLIP_CHAR_CAP = 3200       # total context sent to OpenAI

SUMMARIZER_MAX_TOKENS = 380          # allow a bit more than /ask
