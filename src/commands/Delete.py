from discord.ext import commands
from utilities import sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils

class Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Delete(bot))
