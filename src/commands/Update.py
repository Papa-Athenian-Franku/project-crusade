import csv
from discord.ext import commands
from utilities import google_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def updatesheets(self, ctx):
        sheet_names = ["Claims", "Wars", "Domestics", "Holdings", 
                   "Garrisons", "Armies", "Fleets", 
                   "Movements", "References"]
    
        for sheet in sheet_names:
            # Open the local CSV file and read its contents
            with open(f"src/sheets/{sheet}.csv", mode='r', newline='') as file:
                reader = csv.reader(file)
                data = list(reader)  # Convert the CSV rows into a list of lists

                # Write the data to the corresponding Google Sheet
                result = sheet_utils.overwrite_sheet_by_name(sheet, data)

                if result:
                    await ctx.send(f"Successfully updated the Google Sheet for {sheet}.")
                else:
                    await ctx.send(f"Failed to update the Google Sheet for {sheet}.")

async def setup(bot):
    await bot.add_cog(Update(bot))
