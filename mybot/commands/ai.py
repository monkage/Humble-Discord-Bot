"""AI commands: /ask (OpenAI) and /web (Exa search + OpenAI summary)."""
import asyncio
import time
from typing import Literal

import discord
from discord import app_commands

from mybot import config
from mybot.services import exa_service
from mybot.services.openai_service import ai_concise, summarize_with_citations
from mybot.utils import format_sources

# simple per-user cooldown store
_ask_cd: dict[int, float] = {}


def setup(tree: app_commands.CommandTree) -> None:
    @tree.command(description="Ask the AI (2–4 sentence answer).")
    @app_commands.describe(
        question="Your question",
        public="Post to the channel (default: only you can see it)"
    )
    async def ask(
        interaction: discord.Interaction,
        question: str,
        public: bool = False
    ):
        # cooldown
        now = time.monotonic()
        last = _ask_cd.get(interaction.user.id, 0.0)
        if now - last < config.ASK_COOLDOWN:
            await interaction.response.send_message("⏳ Try again in a few seconds.", ephemeral=False)
            return
        _ask_cd[interaction.user.id] = now

        if not (question or "").strip():
            await interaction.response.send_message("Please ask a non-empty question.", ephemeral=False)
            return

        # if public == True, do NOT make the initial defer ephemeral
        await interaction.response.defer(thinking=True, ephemeral=False)

        answer = await asyncio.to_thread(ai_concise, question)

        content = f"**Q:** {question}\n**A:** {answer}"

        # send based on chosen visibility
        await interaction.followup.send(content, ephemeral=False)

    @tree.command(description="Web research with sources (Exa + concise summary).")
    @app_commands.describe(
        query="What do you want to research?",
        depth="basic (fast, 3 sources) or deep (6 sources)",
        public="Post to the channel (default: only you can see it)"
    )
    async def web(
        interaction: discord.Interaction,
        query: str,
        depth: Literal["basic", "deep"] = "basic",
        public: bool = False,
    ):
        # quick guards
        if not (query or "").strip():
            await interaction.response.send_message("Please provide a non-empty query.", ephemeral=not public)
            return
        if exa_service.exa is None:
            await interaction.response.send_message("Exa API not configured. Set EXA_API_KEY.", ephemeral=not public)
            return

        await interaction.response.defer(thinking=True, ephemeral=not public)

        # choose result count
        k = config.EXA_MAX_RESULTS_BASIC if depth == "basic" else config.EXA_MAX_RESULTS_DEEP

        # Run network-bound work off the event loop
        def _do():
            items, err = exa_service.fetch_highlights(query, k=k, per_url=config.EXA_HIGHLIGHTS_PER_URL)
            if err and not items:
                return f"Search error: {err}"
            summary = summarize_with_citations(query, items)
            srcs = format_sources(items) if items else "No sources."
            return f"**Q:** {query}\n\n{summary}\n\n**Sources**\n{srcs}"

        text = await asyncio.to_thread(_do)
        await interaction.followup.send(text, ephemeral=not public)
