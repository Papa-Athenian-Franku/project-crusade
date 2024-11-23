import os
import discord
from discord.ext import commands
import settings

intents = discord.Intents.all()

# List of cogs to load
cogs: list = ["commands.Retrieval", "commands.Creation"]

client = commands.Bot(command_prefix=settings.Prefix, help_command=None, intents=intents)

@client.event
async def on_ready():
    print("Bot is ready!")
    # Use a fallback for BotStatus
    await client.change_presence(
        status=discord.Status.online, 
        activity=discord.Game(os.environ.get("BOTSTATUS", settings.BotStatus))
    )
    
    # Load all cogs
    for cog in cogs:
        try:
            print(f"Loading cog {cog}")
            await client.load_extension(cog)
            print(f"Loaded cog {cog}")
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"Failed to load cog {cog}\n{exc}")

# Use a fallback for TOKEN in case it's not in the environment
client.run(os.environ.get("TOKEN", settings.TOKEN))
