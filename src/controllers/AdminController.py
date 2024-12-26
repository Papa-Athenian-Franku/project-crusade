import csv
from discord.ext import commands
from utils.sheets.GoogleSheetUtils import GoogleSheetUtils

class AdminController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.google_sheet_utils = GoogleSheetUtils()
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        sheet_names = ["Claims", "Wars", "Domestics", "Holdings", 
                   "Garrisons", "Armies", "Fleets", "Movements"]
    
        for sheet in sheet_names:
            # Open the local CSV file and read its contents
            with open(f"src/sheets/{sheet}.csv", mode='r', newline='') as file:
                reader = csv.reader(file)
                data = list(reader)  # Convert the CSV rows into a list of lists

                # Write the data to the corresponding Google Sheet
                result = self.google_sheet_utils.overwrite_sheet_by_name(sheet, data)

                if result:
                    await ctx.send(f"Successfully updated the Google Sheet for {sheet}.")
                else:
                    await ctx.send(f"Failed to update the Google Sheet for {sheet}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def pause():
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unpause():
        pass

async def setup(bot):
    await bot.add_cog(AdminController(bot))