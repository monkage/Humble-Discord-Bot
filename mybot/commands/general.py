"""Basic commands: /hello, /send, /joined."""
from typing import Optional

import discord
from discord import app_commands


def setup(tree: app_commands.CommandTree) -> None:
    #registers a slash command with the app command tree.
    # youre not calling it now, but rather decaring
    # that /hello exists, and the function handler to run when a user invokes it.
    @tree.command()
    #this is the handler. when someone types /hello, discord.py calls this
    # function and passes and interaction object that contains who/where/what(user, channel, guild etc).
    # The :discord.interaction is just a type hint
    async def hello(interaction: discord.Interaction):
        #the docstring becomes the comand description shown
        # in the slash command UI unless you explicitly pass one in the decorator.
        # its basiclally the tooltip text users see.
        """Says hello!"""
        #this is the first reply to the interaction.
        # you must send this or defer within ~3 seconds
        await interaction.response.send_message(f'Hi, {interaction.user.mention}')

    @tree.command()
    #calls a rename decorator to change the displauy of the parameter on discord.
    @app_commands.rename(text_to_send='text')
    #calls a describe decorator to change the description display on discord
    @app_commands.describe(text_to_send='Text to send in current channel')
    async def send(interaction: discord.Interaction, text_to_send: str):
        """Sends the text into the current channel."""
        await interaction.response.send_message(text_to_send)

    @tree.command(description="Show when a member joined.")
    @app_commands.describe(member="The member to check (defaults to you)")
    async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if interaction.guild is None:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return

        user = member or interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Could not resolve that member.", ephemeral=True)
            return

        when = discord.utils.format_dt(user.joined_at) if user.joined_at else "unknown"
        await interaction.response.send_message(f"{user} joined {when}", ephemeral=True)
