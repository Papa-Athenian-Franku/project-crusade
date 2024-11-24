from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import movement_utilities as movement_utils
from utilities import authorisation_utilities as auth_utils
from utilities import collection_utilities as collection_utils
from utilities import army_utilities as army_utils

class FleetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createfleetfromgarrison(self, ctx):
        """
        Allows a user to create a fleet from their garrison by specifying the Garrison Name.
        Includes ships, troops, and siegecraft.
        """
        # Ask the user for the Garrison Name
        garrison_name = await collection_utils.ask_question(ctx, self.bot, 
                                                            "Enter the Garrison Name (E.G, Garrison of Antioch):", str)
        player_id = auth_utils.get_player_id_from_garrison_name(garrison_name)
        if player_id != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False

        # Retrieve Garrison data
        garrison_data = sheet_utils.get_sheet_by_name("Garrisons")

        # Parse the Garrison Data
        headers = garrison_data[0]
        garrison_data = garrison_data[1:]
        garrison_row = next((row for row in garrison_data if row[1].strip() == garrison_name.strip()), None)

        if not garrison_row:
            await ctx.send(f"**No garrison found with the name '{garrison_name}'. Please check the name and try again.**")
            return

        # Extract Garrison Details
        house_name = garrison_row[0]
        troops = army_utils.parse_troops(garrison_row[3])  # Assuming the 4th column holds troop details
        siegecraft = army_utils.parse_troops(garrison_row[4])  # Assuming the 5th column holds siegecraft details
        ships = army_utils.parse_troops(garrison_row[5])  # Assuming the 6th column holds ship details

        # Display available resources to the user
        troop_types = ", ".join(f"{count} {unit}" for unit, count in troops.items())
        siegecraft_types = ", ".join(f"{count} {equipment}" for equipment, count in siegecraft.items())
        ship_types = ", ".join(f"{count} {ship}" for ship, count in ships.items())

        await ctx.send(f"**{garrison_name} (House {house_name}) has the following resources:**\n"
                    f"**Troops:** {troop_types}\n**Siegecraft:** {siegecraft_types}\n**Ships:** {ship_types}")

        # Ask the user for the ships to allocate
        ship_request = await collection_utils.ask_question(
            ctx, self.bot,
            "Enter the ships to allocate in the format: <number> <type>, <number> <type> "
            "(E.G, '5 Galleys, 2 Warships'):", str
        )

        # Validate and parse the requested ships
        try:
            requested_ships = army_utils.parse_troops(ship_request)
        except ValueError as e:
            await ctx.send(f"**Invalid ship format: {e}. Please try again.**")
            return

        if not army_utils.validate_troop_request(ships, requested_ships):
            await ctx.send(f"**Insufficient ships available in {garrison_name}. Please try again with valid numbers.**")
            return

        # Ask the user for the troops to allocate
        troop_request = await collection_utils.ask_question(
            ctx, self.bot,
            "Enter the troops to allocate in the format: <number> <type>, <number> <type> "
            "(E.G, '200 Infantry, 100 Archers'):", str
        )

        # Validate and parse the requested troops
        try:
            requested_troops = army_utils.parse_troops(troop_request)
        except ValueError as e:
            await ctx.send(f"**Invalid troop format: {e}. Please try again.**")
            return

        if not army_utils.validate_troop_request(troops, requested_troops):
            await ctx.send(f"**Insufficient troops available in {garrison_name}. Please try again with valid numbers.**")
            return

        # Ask the user for the siege equipment to allocate
        siege_request = await collection_utils.ask_question(
            ctx, self.bot,
            "Enter the siege equipment to allocate in the format: <number> <type>, <number> <type> "
            "(E.G, '2 Rams, 1 Trebuchet'):", str
        )

        # Validate and parse the requested siegecraft
        try:
            requested_siegecraft = army_utils.parse_troops(siege_request)
        except ValueError as e:
            await ctx.send(f"**Invalid siegecraft format: {e}. Please try again.**")
            return

        if not army_utils.validate_troop_request(siegecraft, requested_siegecraft):
            await ctx.send(f"**Insufficient siegecraft available in {garrison_name}. Please try again with valid numbers.**")
            return

        # Ask for a name for the new fleet
        fleet_name = await collection_utils.ask_question(ctx, self.bot, "Enter a name for your new fleet:", str)

        # Deduct the requested resources from the garrison
        updated_troops = {unit: troops[unit] - requested_troops.get(unit, 0) for unit in troops}
        updated_siegecraft = {equipment: siegecraft[equipment] - requested_siegecraft.get(equipment, 0) 
                            for equipment in siegecraft}
        updated_ships = {ship: ships[ship] - requested_ships.get(ship, 0) for ship in ships}

        # Update the Garrison Sheet
        updated_garrison_data = [headers]
        for row in garrison_data:
            if row[1].strip() == garrison_name.strip():
                row[3] = army_utils.format_troops(updated_troops)  # Update troop count in the row
                row[4] = army_utils.format_troops(updated_siegecraft)  # Update siegecraft count in the row
                row[5] = army_utils.format_troops(updated_ships)  # Update ship count in the row
            updated_garrison_data.append(row)
        sheet_utils.update_sheet_by_name("Garrisons", updated_garrison_data)

        # Add the new fleet to the Fleets sheet
        formatted_requested_troops = army_utils.format_troops(requested_troops)
        formatted_requested_siegecraft = army_utils.format_troops(requested_siegecraft)
        formatted_requested_ships = army_utils.format_troops(requested_ships)
        sheet_utils.write_to_row("Fleets", [
            house_name, fleet_name, formatted_requested_ships, formatted_requested_troops, formatted_requested_siegecraft, ctx.author.name
        ])

        # Confirm the creation of the fleet
        await ctx.send(f"**The fleet '{fleet_name}' has been created for House {house_name} from {garrison_name} with the "
                    f"following:**\n**Ships:** {formatted_requested_ships}\n**Troops:** {formatted_requested_troops}\n"
                    f"**Siegecraft:** {formatted_requested_siegecraft}.**")

    @commands.command()
    async def reinforcegarrisonfromfleet(self, ctx):
        """
        Reinforces a garrison by transferring resources from a fleet and then deleting the fleet.
        """
        # Ask the user for the Garrison Name
        garrison_name = await collection_utils.ask_question(ctx, self.bot, 
                                                            "Enter the Garrison Name to reinforce (E.G, Garrison of Antioch):", str)
        
        player_id = auth_utils.get_player_id_from_garrison_name(garrison_name)
        if player_id != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False

        # Retrieve Garrison data
        garrison_data = sheet_utils.get_sheet_by_name("Garrisons")
        fleet_data = sheet_utils.get_sheet_by_name("Fleets")

        # Parse Garrison Data
        headers = garrison_data[0]
        garrison_data = garrison_data[1:]
        garrison_row = next((row for row in garrison_data if row[1].strip() == garrison_name.strip()), None)

        if not garrison_row:
            await ctx.send(f"**No garrison found with the name '{garrison_name}'. Please check the name and try again.**")
            return

        # Ask for the Fleet Name
        fleet_name = await collection_utils.ask_question(ctx, self.bot, "Enter the Fleet Name to transfer from:", str)
        player_id = auth_utils.get_player_id_from_army_fleet_name("Fleet", fleet_name)
        if player_id != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False

        # Parse Fleet Data
        fleet_row = next((row for row in fleet_data[1:] if row[1].strip() == fleet_name.strip()), None)
        if not fleet_row:
            await ctx.send(f"**No fleet found with the name '{fleet_name}'. Please check the name and try again.**")
            return

        # Extract Garrison and Fleet Details
        garrison_troops = army_utils.parse_troops(garrison_row[3])  # Assuming 4th column for troops
        garrison_siegecraft = army_utils.parse_troops(garrison_row[4])  # Assuming 5th column for siegecraft
        garrison_ships = army_utils.parse_troops(garrison_row[5])  # Assuming 6th column for ships

        fleet_troops = army_utils.parse_troops(fleet_row[3])  # Assuming 4th column for troops
        fleet_siegecraft = army_utils.parse_troops(fleet_row[4])  # Assuming 5th column for siegecraft
        fleet_ships = army_utils.parse_troops(fleet_row[2])  # Assuming 3rd column for ships

        # Merge Resources
        for unit, count in fleet_troops.items():
            garrison_troops[unit] = garrison_troops.get(unit, 0) + count
        for equipment, count in fleet_siegecraft.items():
            garrison_siegecraft[equipment] = garrison_siegecraft.get(equipment, 0) + count
        for ship, count in fleet_ships.items():
            garrison_ships[ship] = garrison_ships.get(ship, 0) + count

        # Update the Garrison Sheet
        updated_garrison_data = [headers]
        for row in garrison_data:
            if row[1].strip() == garrison_name.strip():
                row[3] = army_utils.format_troops(garrison_troops)  # Update troop count
                row[4] = army_utils.format_troops(garrison_siegecraft)  # Update siegecraft count
                row[5] = army_utils.format_troops(garrison_ships)  # Update ship count
            updated_garrison_data.append(row)
        sheet_utils.update_sheet_by_name("Garrisons", updated_garrison_data)

        # Remove the Fleet from the Fleets Sheet
        updated_fleet_data = [fleet_data[0]] + [row for row in fleet_data[1:] if row[1].strip() != fleet_name.strip()]
        sheet_utils.update_sheet_by_name("Fleets", updated_fleet_data)

        # Confirm Reinforcement
        await ctx.send(f"**The fleet '{fleet_name}' has been successfully reinforced into '{garrison_name}', and the fleet has been disbanded.**")

    @commands.command()
    async def mergefleets(self, ctx):
        """
        Merges two fleets into one if they are in the same hex.
        """
        # Ask for the names of the two fleets to merge
        fleet1_name = await collection_utils.ask_question(ctx, self.bot, 
                                                        "Enter the name of the first fleet to merge:", str)
        player_id_fleet_1 = auth_utils.get_player_id_from_army_fleet_name("Fleet", fleet1_name)
        fleet2_name = await collection_utils.ask_question(ctx, self.bot, 
                                                        "Enter the name of the second fleet to merge:", str)
        player_id_fleet_2 = auth_utils.get_player_id_from_army_fleet_name("Fleet", fleet2_name)

        if player_id_fleet_1 != ctx.message.author or player_id_fleet_2 != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False

        # Retrieve Fleet data
        fleet_data = sheet_utils.get_sheet_by_name("Fleets")

        # Parse Fleet Data
        headers = fleet_data[0]
        fleet_data = fleet_data[1:]
        fleet1_row = next((row for row in fleet_data if row[1].strip() == fleet1_name.strip()), None)
        fleet2_row = next((row for row in fleet_data if row[1].strip() == fleet2_name.strip()), None)

        if not fleet1_row or not fleet2_row:
            await ctx.send(f"**One or both fleets ('{fleet1_name}', '{fleet2_name}') could not be found. Please check the names and try again.**")
            return

        # Validate House and Hex
        house_name1, hex1 = fleet1_row[0], fleet1_row[2]
        house_name2, hex2 = fleet2_row[0], fleet2_row[2]
        if house_name1 != house_name2:
            await ctx.send(f"**Fleets must belong to the same house to merge. '{fleet1_name}' belongs to {house_name1}, "
                        f"but '{fleet2_name}' belongs to {house_name2}.**")
            return
        if hex1 != hex2:
            await ctx.send(f"**Fleets must be in the same hex to merge. '{fleet1_name}' is in hex {hex1}, but "
                        f"'{fleet2_name}' is in hex {hex2}.**")
            return

        # Extract and Merge Ships, Troops, and Siegecraft
        ships1 = army_utils.parse_troops(fleet1_row[5])  # Assuming 6th column holds ship details
        troops1 = army_utils.parse_troops(fleet1_row[3])  # Assuming 4th column holds troop details
        siegecraft1 = army_utils.parse_troops(fleet1_row[4])  # Assuming 5th column holds siegecraft details

        ships2 = army_utils.parse_troops(fleet2_row[5])
        troops2 = army_utils.parse_troops(fleet2_row[3])
        siegecraft2 = army_utils.parse_troops(fleet2_row[4])

        merged_ships = {unit: ships1.get(unit, 0) + ships2.get(unit, 0) for unit in set(ships1) | set(ships2)}
        merged_troops = {unit: troops1.get(unit, 0) + troops2.get(unit, 0) for unit in set(troops1) | set(troops2)}
        merged_siegecraft = {unit: siegecraft1.get(unit, 0) + siegecraft2.get(unit, 0) for unit in set(siegecraft1) | set(siegecraft2)}

        # Ask for the name of the merged fleet
        merged_fleet_name = await collection_utils.ask_question(ctx, self.bot, 
                                                                "Enter a name for the merged fleet:", str)

        # Update the Fleets Sheet
        updated_fleet_data = [headers]
        for row in fleet_data:
            if row[1].strip() == fleet1_name.strip():
                row[1] = merged_fleet_name  # Rename the first fleet to the merged fleet
                row[3] = army_utils.format_troops(merged_troops)  # Update troops
                row[4] = army_utils.format_troops(merged_siegecraft)  # Update siegecraft
                row[5] = army_utils.format_troops(merged_ships)  # Update ships
                updated_fleet_data.append(row)
            elif row[1].strip() != fleet2_name.strip():
                updated_fleet_data.append(row)  # Keep rows not related to the second fleet

        sheet_utils.update_sheet_by_name("Fleets", updated_fleet_data)

        # Confirm the merge
        await ctx.send(f"**Fleets '{fleet1_name}' and '{fleet2_name}' have been merged into '{merged_fleet_name}' "
                    f"in hex {hex1} with the following resources:**\n"
                    f"- Ships: {army_utils.format_troops(merged_ships)}\n"
                    f"- Troops: {army_utils.format_troops(merged_troops)}\n"
                    f"- Siegecraft: {army_utils.format_troops(merged_siegecraft)}")

async def setup(bot):
    await bot.add_cog(FleetCommands(bot))
