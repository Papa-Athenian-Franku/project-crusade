from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils

class Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removeclaim(self, ctx, claim):
        """
        Removes a claim by House Name or Player ID from the Claims sheet.
        """
        # Retrieve the Claims sheet data
        sheet_values = sheet_utils.get_sheet_by_name("Claims")
        if not sheet_values:
            await ctx.send("**The Claims sheet could not be found or is empty.**")
            return

        # Keep track of whether a claim was removed
        claim_removed = False
        updated_rows = [sheet_values[0]]  # Keep the header row

        # Iterate through the sheet to find and remove the claim
        for row in sheet_values[1:]:
            if row[0].strip() == claim.strip() or row[1].strip() == claim.strip():
                claim_removed = True
            else:
                updated_rows.append(row)

        # Check if a claim was found and removed
        if claim_removed:
            # Overwrite the Claims sheet with the updated data
            sheet_utils.update_sheet_by_name("Claims", updated_rows)
            await ctx.send(f"**The claim '{claim}' has been successfully removed.**")
        else:
            await ctx.send(f"**No claim matching '{claim}' was found in the Claims sheet.**")


async def setup(bot):
    await bot.add_cog(Delete(bot))
