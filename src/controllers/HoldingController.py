from discord.ext import commands

class HoldingController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def placeholder():
        pass

async def setup(bot):
    await bot.add_cog(HoldingController(bot))