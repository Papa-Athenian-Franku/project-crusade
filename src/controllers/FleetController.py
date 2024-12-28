from discord.ext import commands
from services.FleetService import FleetService
from utils.misc.AuthorisationUtils import AuthorisationUtils

class FleetController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fleet_service = FleetService()
        self.auth = AuthorisationUtils()
        
    @commands.command()
    async def fleet(self, ctx, fleet):
        player_id = self.auth.get_player_id_from_army_fleet_name("Fleet", fleet)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            await ctx.send(embed=self.fleet_service.retrieve_fleet(fleet))

async def setup(bot):
    await bot.add_cog(FleetController(bot))