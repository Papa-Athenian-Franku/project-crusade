from discord.ext import commands
from utilities import sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import collection_utilities as collection_utils
from utilities import movement_utilities as movement_utils

class Creation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createmovement(self, ctx):
        successful_write = False
        while True:
            # Get Movement type, Army or Fleet, and Army or Fleet Name.
            movement_type, army_fleet_name = await movement_utils.collectmovementunitsinfo(self.bot, ctx)
            if movement_type.lower() != "army" and movement_type.lower() != "fleet":
                break

            # Get autofill avoid info based on Army/Fleet Name and Movement type.
            start, auto_fill_avoid_list = await movement_utils.collectautofillavoidinfo(movement_type, army_fleet_name)
            if auto_fill_avoid_list is None or start is None:
                break

            # Prompt user for destination, as well as any hexes to avoid.
            goal, avoid_list = await movement_utils.collectmovementinfo(self.bot, ctx, auto_fill_avoid_list)

            # Pathfind.
            path = path_utils.retrieve_movement_path(movement_type, start, goal, avoid_list)

            # Get Army/Fleet composition and determine movement speed per tile.
            troops, siegecraft, ships = await movement_utils.collectarmyfleetcomposition(movement_type, army_fleet_name)

             # Determine minutes per tile based on composition.
            if ships:
                minutes_per_tile = 45
            else:
                minutes_per_tile = await movement_utils.getminutespertile(troops, siegecraft)

            # Create Movement in Sheets.
            successful_write = sheet_utils.write_to_row("Movements", [movement_type, army_fleet_name, path, path[0], minutes_per_tile, 0])
            break
        
        if successful_write:
            await ctx.send(
                "**Successful Movement Creation, TY Pookie :)**",
                embed=embed_utils.set_info_embed_from_list(
                    [
                        "Embed Title",
                        "Starting Hex ID", 
                        "Destination Hex ID", 
                        "Path of Hex IDs",
                        "Minutes Per Hex", 
                        "Estimated Time to Completion"
                    ],
                    [
                        f"Movement from {start} to {goal}.", 
                        start,
                        goal, 
                        path,
                        minutes_per_tile, 
                        minutes_per_tile * len(path)
                    ]
                )
            )
        else:
            await ctx.send("Movement Creation Failed. Start again but be less retarded please.")

async def setup(bot):
    await bot.add_cog(Creation(bot))
