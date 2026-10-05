"""Each module here has a setup(tree) that registers its commands on the command tree."""
from discord import app_commands

from mybot.commands import ai, general, moderation, pomodoro

MODULES = (general, ai, pomodoro, moderation)


def register_all(tree: app_commands.CommandTree) -> None:
    for module in MODULES:
        module.setup(tree)
