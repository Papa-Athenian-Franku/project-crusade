from discord.ext import commands
from services.DomesticService import DomesticService

class DomesticController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.domestic_service = DomesticService()
        
    @commands.command()
    async def domestic(self, ctx, house):
        constructed_embed = await self.domestic_service.get_domestic_info(ctx.message.author, house)
        if constructed_embed is not None:
            await ctx.send(embed=constructed_embed)
        else:
            await ctx.send("**You are not the associated claim dumb dumb!**")

async def setup(bot):
    await bot.add_cog(DomesticController(bot))