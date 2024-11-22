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
        while True:
            # Get Movement type, Army or Fleet. Aswell as Army or Fleet Name.
            movement_type, army_fleet_name = await self.collectmovementunitsinfo(ctx)

            # From Army or Fleet Name, find House Name and Enemies.
            # Find Enemies Holdings and add to auto filled avoid list.
            auto_fill_avoid_list = await self.collectautofillavoidinfo(ctx, movement_type, army_fleet_name)
            if auto_fill_avoid_list is None:
                break

            # Prompt user for starting and goal hex. 
            # Aswell as any hexes or holdings to avoid on the way.
            start, goal, avoid_list = await self.collectmovementinfo(ctx, auto_fill_avoid_list)

            # Pathfind.
            path = path_utils.retrieve_movement_path(movement_type, start, goal, avoid_list)

            # Request Army or Fleet Details.
            # Determine Movement speed per tile.
            # TODO: implement this bit...
            troops, siegecraft, ships = await self.collectarmyfleetcomposition(ctx, movement_type, army_fleet_name)
            slowest_troop_time = None
            minutes_per_hex = None

            # Create Movement in Sheets.
            # TODO: implement this bit...
            
            await ctx.send(f"Movement from {start} to {goal} created, using the path: {path}.\nTime per Hex: {None}")
            break

        await ctx.send("Movement Creation Failed. Start again but be less retarded please.")

    async def collectmovementunitsinfo(self, ctx):
        movement_type = collection_utils.ask_question(ctx, self.bot, 
                                                      "Movement Type: (Army or Fleet)", str)
        army_fleet_name = collection_utils.ask_question(ctx, self.bot, 
                                                      f"Name of {movement_type}: (E.G, 1st Army of Antioch)", str)
        return movement_type, army_fleet_name

    async def collectautofillavoidinfo(self, ctx, movement_type, army_fleet_name):
        units_sheet = sheet_utils.get_sheet_by_name("Armies") if movement_type.lower() == "army" else sheet_utils.get_sheet_by_name("Fleets")
        domestic_sheet = sheet_utils.get_sheet_by_name("Domestics")
        wars_sheet = sheet_utils.get_sheet_by_name("Wars")

        house_name = None
        house_religion = None
        house_enemies = []
        enemy_holdings = None

        # Get House Name
        for army_fleet in units_sheet:
            if army_fleet[0] == "":
                return None
            elif army_fleet[1] == army_fleet_name:
                house_name = army_fleet[0]

        # Get House Religion
        for house in domestic_sheet:
            if house[0] == "":
                return None
            elif house[0] == house_name:
                house_religion = house[4]

        # Get House Wars and Enemies.
        for war in wars_sheet:
            if war[0] == "":
                return [] # They can be at peace and still move troops.
            
            if war[1] == "Religious":
                if house_religion in war[2]:
                    house_enemies.extend(war[3])
                elif house_religion in war[3]:
                    house_enemies.extend(war[2])

            elif war[1] == "Domestic":
                if house_name in war[2]:
                    house_enemies.extend(war[3])
                elif house_name in war[3]:
                    house_enemies.extend(war[2]) 

        # Get Enemies Holdings.
        for house in domestic_sheet:
             if house[0] == "":
                return []
             elif house[0] == house_name:
                enemy_holdings.extend(house[3])

        # Return Enemy Holding Names.
        return enemy_holdings

    async def collectmovementinfo(self, ctx, auto_fill_avoid_list):
        start = collection_utils.ask_question(ctx, self.bot, 
                                                      "Start Position: (Hex ID or Holding Name)", str)
        goal = collection_utils.ask_question(ctx, self.bot, 
                                                      "End Position: (Hex ID or Holding Name)", str)
        avoid_list = []
        while True:
            await ctx.send(f"Automatically avoiding enemy holding tiles: {auto_fill_avoid_list}")
            avoid_list.append(collection_utils.ask_question(ctx, self.bot, 
                                                      "Avoid Position: (Hex ID or Holding Name)", str))
            finished = collection_utils.ask_question(ctx, self.bot, 
                                                      "Are you finished with Avoid Positions: (Yes or No)", str)
            if finished.lower() == "yes" or finished.lower() == "y":
                break

        return start, goal, avoid_list.extend(auto_fill_avoid_list)
    
    async def collectarmyfleetcomposition(self, ctx, movement_type, army_fleet_name):
        units_sheet = sheet_utils.get_sheet_by_name("Armies") if movement_type.lower() == "army" else sheet_utils.get_sheet_by_name("Fleets")

        troops = None
        siegecraft = None
        ships = None

        for army_fleet in units_sheet:
            if army_fleet[0] == "":
                return None
            elif army_fleet[1] == army_fleet_name:
                troops = army_fleet[3]
                siegecraft = army_fleet[4]
                if movement_type.lower() != "army":
                    ships = army_fleet[5]

        return troops, siegecraft, ships

async def setup(bot):
    await bot.add_cog(Creation(bot))
