from discord.ext import commands
from utilities import sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils

class Retrieval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def domesticinfo(self, ctx, house_name):
        sheet_values = sheet_utils.get_sheet_by_name("House Meta Sheet")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == house_name:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    @commands.command()
    async def retrievemovementpath(self, ctx, movement_type, start, goal):
        await ctx.send(path_utils.retrieve_movement_path(movement_type, start, goal))

async def setup(bot):
    await bot.add_cog(Retrieval(bot))
