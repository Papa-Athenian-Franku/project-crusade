from discord.ext import commands
from utilities import sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils

class Retrieval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def domesticinfo(self, ctx, house):
        sheet_values = sheet_utils.get_sheet_by_name("Domestics")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == house:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    @commands.command()
    async def holdinginfo(self, ctx, holding):
        sheet_values = sheet_utils.get_sheet_by_name("Holdings")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == holding:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Either Garrison Name or Holding Name
    @commands.command()
    async def garrisoninfo(self, ctx, garrison):
        sheet_values = sheet_utils.get_sheet_by_name("Garrisons")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == garrison or row[2] == garrison:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Army Name
    @commands.command()
    async def armyinfo(self, ctx, army):
        sheet_values = sheet_utils.get_sheet_by_name("Armies")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == army:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Fleet Name
    @commands.command()
    async def fleetinfo(self, ctx, fleet):
        sheet_values = sheet_utils.get_sheet_by_name("Fleets")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == fleet:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    @commands.command()
    async def priceinfo(self, ctx):
        sheet_values = sheet_utils.get_sheet_by_name("References")
        column_headings = sheet_values[0]
        await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, sheet_values))

async def setup(bot):
    await bot.add_cog(Retrieval(bot))
