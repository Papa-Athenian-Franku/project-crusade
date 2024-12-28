from discord.ext import commands
from services.ArmyService import ArmyService
from utils.misc.AuthorisationUtils import AuthorisationUtils

class ArmyController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.army_service = ArmyService()
        self.auth = AuthorisationUtils()
        
    @commands.command()
    async def army(self, ctx, army):
        id = self.auth.get_player_id_from_army_fleet_name("Army", army)
        if id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            await ctx.send(embed=self.army_service.retrieve_army(army))

async def setup(bot):
    await bot.add_cog(ArmyController(bot))