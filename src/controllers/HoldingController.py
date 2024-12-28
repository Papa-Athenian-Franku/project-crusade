from discord.ext import commands
from services.HoldingService import HoldingService

class HoldingController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.holding_service = HoldingService()

    @commands.command()
    async def holding(self, ctx, holding):
        await ctx.send(embed=self.holding_service.retrieve_holding(holding))

async def setup(bot):
    await bot.add_cog(HoldingController(bot))