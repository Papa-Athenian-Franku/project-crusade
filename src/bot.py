import os
import csv
import discord
from discord.ext import commands
from utils.sheets import GoogleSheetUtils
import config.settings as settings

intents = discord.Intents.all()

# List of cogs to load
cogs: list = ["controllers.ArmyController", "controllers.ClaimController",
              "controllers.DomesticController", "controllers.FleetController",
              "controllers.GarrisonController", "controllers.HoldingController",
              "controllers.MovementController", "controllers.AdminController",
              "controllers.background.MovementBackgroundController"]

client = commands.Bot(command_prefix=settings.Prefix, help_command=None, intents=intents)
sheet_utils = GoogleSheetUtils()

@client.event
async def on_ready():
    # Use a fallback for BotStatus
    await client.change_presence(
        status=discord.Status.online, 
        activity=discord.Game(os.environ.get("BOTSTATUS", settings.BotStatus))
    )

    await download_sheets()
    
    # Load all cogs
    for cog in cogs:
        try:
            print(f"Loading cog {cog}")
            await client.load_extension(cog)
            print(f"Loaded cog {cog}")
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"Failed to load cog {cog}\n{exc}")
    
    print("Bot is ready!")

async def download_sheets():
    # Download sheets.
    sheet_names = ["Claims", "Wars", "Domestics", "Holdings", 
                   "Garrisons", "Armies", "Fleets", 
                   "Movements", "References", "Map"]

    # Ensure the directory exists
    directory = "src/sheets"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for sheet in sheet_names:
        data = get_sheet_by_name(sheet)
        if data:
            print(f"Downloading {sheet}.")
            with open(f"{directory}/{sheet}.csv", mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

# Use a fallback for TOKEN in case it's not in the environment
client.run(os.environ.get("TOKEN", settings.TOKEN))
