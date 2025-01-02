from discord.ext import commands
from services.MovementService import MovementService
from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.AuthorisationUtils import AuthorisationUtils
from utils.misc.CollectionUtils import CollectionUtils

class MovementController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.movement_service = MovementService()
        self.local_sheet_utils = LocalSheetUtils()
        self.auth = AuthorisationUtils()
        self.collection_utils = CollectionUtils()
        
    @commands.command()
    async def movement(self, ctx):
        constructed_embed = await self.movement_service.create_new_movement()
        if constructed_embed is not None:
            await ctx.send(
                "**Successful Movement Creation, TY Pookie :)**",
                embed=constructed_embed)
        else:
            await ctx.send("Movement Creation Failed. Start again but be less retarded please.")

    @commands.command()
    async def mymovements(self, ctx):
        movements = await self.movement_service.retrieve_user_movements(str(ctx.message.author))
        if not movements:
            await ctx.author.send("**You have no ongoing movements.**")
        else:
            await ctx.author.send(f"**All Player Movements:**\n{movements}")

    @commands.command()
    async def getmovement(self, ctx):
        movement = await self.movement_service.retrieve_specified_movement(ctx)
        if not movement:
            await ctx.send("**Failed to Retrieve Movement.**")
        else:
            await ctx.message.author.send(
                    "**Your movement details :)**",
                    embed=movement
                )

async def setup(bot):
    await bot.add_cog(MovementController(bot))