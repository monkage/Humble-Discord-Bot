"""Entry point: `python bot.py`"""
import discord

from mybot import config
from mybot.client import MyClient
from mybot.commands import register_all


def main() -> None:
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing from your .env")

    #this gives access to all the standard non privileged intents on,
    # with the privileged ones off(stuff luke presences, members and message_content)
    intents = discord.Intents.default()
    #making your bot and handing it a list of things it wants to hear about from discord
    client = MyClient(intents=intents)

    #attach every slash/context menu command to the tree before logging in
    register_all(client.tree)

    client.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
