from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import movement_utilities as movement_utils
from utilities import authorisation_utilities as auth_utils
from utilities import collection_utilities as collection_utils
from utilities import army_utilities as army_utils

class Creation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def recruit(self, ctx, holding, number: int, troop):
        # Load the References CSV file to check for troop validity
        references = sheet_utils.read_csv("References.csv")  # Load the troop data
        domestics = sheet_utils.read_csv("Domestics.csv")  # Load the treasury data

        # Check if the troop exists in the References CSV file
        troop_data = next((row for row in references if row['Item Name'] == troop), None)
        if not troop_data:
            await ctx.send(f"**Invalid troop type: '{troop}'. Please choose a valid troop from the list in the References file.**")
            return

        # Validate that the number is positive
        if number <= 0:
            await ctx.send("**The number of troops must be a positive integer.**")
            return

        # Calculate total cost and days to train
        cost_per_troop = int(troop_data['Cost'])
        days_to_train = int(troop_data['Days to Train'])
        total_cost = cost_per_troop * number

        # Find the house treasury based on the holding name
        house_data = next((row for row in domestics if row['Holdings'] == holding), None)
        if not house_data:
            await ctx.send(f"**No house found with holding '{holding}'. Please check the holding name and try again.**")
            return

        treasury = int(house_data['Treasury'])
        if total_cost > treasury:
            await ctx.send(f"**Insufficient funds in the treasury of '{house_data['House Name']}'. Recruitment cost is {total_cost}, but only {treasury} is available.**")
            return

        # Deduct the cost from the treasury and update the Domestics sheet
        house_data['Treasury'] = treasury - total_cost
        sheet_utils.update_row("Domestics", house_data)

        # Log the recruitment request in the Reinforcements sheet
        sheet_utils.write_to_row(
            "Reinforcements",
            [str(ctx.message.author), holding, number, troop, days_to_train]
        )

        await ctx.send(f"**Recruitment request logged!**\n"
                    f"**Troop:** {troop}\n"
                    f"**Number:** {number}\n"
                    f"**Holding:** {holding}\n"
                    f"**Days to Train:** {days_to_train}\n"
                    f"**Total Cost:** {total_cost}\n"
                    f"**Remaining Treasury:** {house_data['Treasury']}")

async def setup(bot):
    await bot.add_cog(Creation(bot))
