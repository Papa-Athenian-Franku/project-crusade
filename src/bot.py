import os
import csv
import discord
from discord.ext import commands
from utilities import google_sheets_utilities as sheet_utils 
import settings

intents = discord.Intents.all()

# List of cogs to load
cogs: list = ["commands.Creation", "commands.Retrieval", 
              "commands.Delete", "commands.Update", 
              "commands.creation_sub_commands.ArmyCommands", 
              "commands.creation_sub_commands.FleetCommands", 
              "commands.background_tasks.Movements"]

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
    
    # Download sheets.
    sheet_names = ["Claims", "Wars", "Domestics", "Holdings", 
                   "Garrisons", "Armies", "Fleets", 
                   "Movements", "References", "Map"]
    
    for sheet in sheet_names:
        data = sheet_utils.get_sheet_by_name(sheet)
        if data:
            with open(f"src/sheets/{sheet}.csv", mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

# Use a fallback for TOKEN in case it's not in the environment
client.run(os.environ.get("TOKEN", settings.TOKEN))
