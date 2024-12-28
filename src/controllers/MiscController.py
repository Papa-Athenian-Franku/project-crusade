from discord.ext import commands
from services.MiscService import MiscService

class MiscController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.misc_service = MiscService()

    @commands.command()
    async def prices(self, ctx):
        await ctx.send(embed=self.misc_service.retrieve_prices_info())

    @commands.command()
    async def wars(self, ctx):
        await ctx.send(embed=self.misc_service.retrieve_wars_info())

    @commands.command()
    async def hex(self, ctx, hex):
        await ctx.send(embed=self.misc_service.retrieve_hex_info(hex))

async def setup(bot):
    await bot.add_cog(MiscController(bot))
