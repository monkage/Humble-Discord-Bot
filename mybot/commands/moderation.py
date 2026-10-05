"""Right-click context menu commands: Show Join Date, Report To Moderators."""
import discord
from discord import app_commands

from mybot import config

# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.


def setup(tree: app_commands.CommandTree) -> None:
    #this contex menu command only works on members
    @tree.context_menu(name='Show Join Date')
    async def show_join_date(interaction: discord.Interaction, member: discord.Member):
        if member.joined_at is None:
            await interaction.response.send_message(f'{member} has no join date.', ephemeral=True)
        else:
            await interaction.response.send_message(
                f'{member} joined at {discord.utils.format_dt(member.joined_at)}',
                ephemeral=True
            )

    #this context menu commad only works on messages
    @tree.context_menu(name='Report To Moderators')
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message(f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True)

        #make sure we are inside a guild
        if interaction.guild is None:
            await interaction.followup.send('This command can only be used in a server.', ephemeral=True)
            return

        #handle report by sendig it into a log channel
        log_channel = interaction.guild.get_channel(config.REPORT_CHANNEL_ID)

        #even if a channel exists, confirm that its something that you can send messages to
        if log_channel is None or not isinstance(log_channel, discord.abc.Messageable):
            await interaction.followup.send('Log channel not found or messageable', ephemeral=True)
            return

        embed = discord.Embed(title='Report Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        #creates a view container for ui components like buttons or selects
        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)
