from discord.ext import commands
from services.MovementService import MovementService

class MovementController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def movement(self, ctx):
        constructed_embed = await MovementService.create_new_movement()
        if constructed_embed is not None:
            await ctx.send(
                "**Successful Movement Creation, TY Pookie :)**",
                embed=constructed_embed)
        else:
            await ctx.send("Movement Creation Failed. Start again but be less retarded please.")

async def setup(bot):
    await bot.add_cog(MovementController(bot))