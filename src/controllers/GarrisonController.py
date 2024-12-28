from discord.ext import commands
from services.GarrisonService import GarrisonService
from utils.misc.AuthorisationUtils import AuthorisationUtils
from utils.sheets.LocalSheetUtils import LocalSheetUtils

class GarrisonController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.garrison_service = GarrisonService()
        self.auth = AuthorisationUtils()
        self.local_sheet_utils = LocalSheetUtils()
        
    @commands.command()
    async def garrison(self, ctx, garrison):
        player_id = self.auth.get_player_id_from_garrison_name(garrison)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            await ctx.send(embed=self.garrison_service.retrieve_garrison(garrison))

async def setup(bot):
    await bot.add_cog(GarrisonController(bot))