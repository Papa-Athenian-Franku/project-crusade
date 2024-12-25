from discord.ext import commands
from services.ClaimService import ClaimService
from utils.misc import CollectionUtils

class ClaimController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.claim_service = ClaimService()

    @commands.command()
    async def claim(self, ctx):
        # Ask the user for their house name
        house = await CollectionUtils.ask_question(
            ctx, self.bot,
            "Give your House Name as: House Whatever (e.g., House O'Neill)", str
        )

        # Validate the house name format
        if not house.strip().startswith("House "):
            await ctx.send("**Incorrect House Name format! Please try again using the format: 'House Whatever'.**")
            return

        # Check for duplicate claims
        is_duplicate, error_message = self.claim_service.is_duplicate_claim(house, ctx.message.author.id)
        if is_duplicate:
            await ctx.send(f"**{error_message}**")
            return

        # Create and confirm the claim
        await ctx.send(f"**{self.claim_service.create_claim(house, ctx.message.author.id)}**")

    @commands.command()
    async def claims(self, ctx):
        claims = self.claim_service.get_claims()
        if claims and len(claims) > 1:
            for claim in claims[1:]:  # Skip the header row
                await ctx.send(f"**Player: {claim[1]}\nClaimed: {claim[0]}**")
        else:
            await ctx.send("**No Claims.**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def declaim(self, ctx, claim):
        message = self.claim_service.delete_claim(claim)
        await ctx.send(f"**{message}**")

async def setup(bot):
    await bot.add_cog(ClaimController(bot))
