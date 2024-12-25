from discord.ext import commands

class GarrisonController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def placeholder():
        pass

async def setup(bot):
    await bot.add_cog(GarrisonController(bot))