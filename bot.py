import discord
import requests
import json
import os, discord, requests, json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


def get_meme():
    r = requests.get("https://meme-api.com/gimme", timeout=10)
    j = r.json()
    # returns: title, image url (direct), and the source Reddit post
    return j["title"], j["url"], j.get("postLink")

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('$meme'):
            title, image_url, source = get_meme()

            embed = discord.Embed(
                title=title,       # the meme’s title (clickable because we set url=…)
                url=source,        # clicking the title opens the Reddit post
                color=0x2F3136     # optional accent color
            )
            embed.set_image(url=image_url)               # show the meme image
            embed.set_footer(text="Powered by meme-api") # optional footer

            await message.channel.send(embed=embed)

        

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)
