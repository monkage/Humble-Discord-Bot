import discord
from discord import app_commands

from mybot import config

MY_GUILD = discord.Object(id=config.GUILD_ID)


class MyClient(discord.Client):  #allows  the cog(or class) to subclass the bot's client
    user: discord.ClientUser #makes sure no error pops up if the user attribute is None, since it will jsut fill it up later

    def __init__(self, *, intents: discord.Intents):
        #calls the base discord.Client constructor so that its properly initialised with those intents.
        #if yo dont pass them, you wont recieve the messages from the events(bot wont see what they need to work)
        super().__init__(intents=intents)
        #creates an application command tree (basically slash command, user/context menu commands) bound to the client
        #you register commands on this tree.
        #you sync the tree to discord so the commands show up in the UI
        #at runtime, it dispatches incoming command invocations to the right handler.
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self): #sets up async for asynchronous function, setup_hook provides a safe place to do so
        #copies all the global commands to a specific guild scope for fast testing.
        self.tree.copy_global_to(guild=MY_GUILD)
        #publishes the commands synced to the specified guild on discord.
        #await is basically a non blocking wait for the I/O, not run whenever.
        #when you send a message or fetch something from the server,
        # that takes time, so to not waste that time, the function pauses and
        # does other things, such as responding to other users'
        # commands or run background tasks or maintain the gateway.
        await self.tree.sync(guild=MY_GUILD)

    #after calling the token, the bot logs in
    #discord basically says youre ready and fires the on_ready event,
    # and because the method has this name, discord.py calls it for you.
    async def on_ready(self):
        #writes the information to your terminal
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('--------')
