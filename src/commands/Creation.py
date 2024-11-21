from discord.ext import commands
from utilities import sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import collection_utilities as collection_utils

class Creation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createmovement(self, ctx):
        movement_type = collection_utils.ask_question(ctx, self.bot, 
                                                      "Movement Type: (Army or Fleet)", str)
        start = collection_utils.ask_question(ctx, self.bot, 
                                                      "Start Position: (Hex ID or Holding Name)", str)
        goal = collection_utils.ask_question(ctx, self.bot, 
                                                      "End Position: (Hex ID or Holding Name)", str)
        avoid_list = []
        while True:
            avoid_list.append(collection_utils.ask_question(ctx, self.bot, 
                                                      "Avoid Position: (Hex ID or Holding Name)", str))
            finished = collection_utils.ask_question(ctx, self.bot, 
                                                      "Are you finished with Avoid Positions: (Yes or No)", str)
            if finished.lower() == "yes" or finished.lower() == "y":
                break
        path = path_utils.retrieve_movement_path(movement_type, start, goal, avoid_list)
        
        await ctx.send()

async def setup(bot):
    await bot.add_cog(Creation(bot))
