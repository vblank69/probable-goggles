import discord
from discord.ext.commands import Bot
import os

intents = discord.Intents.default()
intents.message_content = True

client = Bot(command_prefix="!", intents=intents, case_insensitive=True)

@client.event
async def on_ready():
    await client.load_extension("multimedia.commands")
    await client.tree.sync()
    print(f'We have logged in as {client.user}')

token = os.getenv('DISCORD_TOKEN')
client.run(token)
