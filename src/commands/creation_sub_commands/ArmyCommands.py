from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import movement_utilities as movement_utils
from utilities import authorisation_utilities as auth_utils
from utilities import collection_utilities as collection_utils
from utilities import army_utilities as army_utils

class ArmyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createarmyfromgarrison(self, ctx):
        """
        Allows a user to create an army from their garrison by specifying the Garrison Name.
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

        # Display available troops and siegecraft to the user
        troop_types = ", ".join(f"{count} {unit}" for unit, count in troops.items())
        siegecraft_types = ", ".join(f"{count} {equipment}" for equipment, count in siegecraft.items())
        await ctx.send(f"**{garrison_name} (House {house_name}) has the following:**\n"
                    f"**Troops:** {troop_types}\n**Siegecraft:** {siegecraft_types}")

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

        # Check if the requested troops are available
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

        # Check if the requested siege equipment is available
        if not army_utils.validate_troop_request(siegecraft, requested_siegecraft):
            await ctx.send(f"**Insufficient siegecraft available in {garrison_name}. Please try again with valid numbers.**")
            return

        # Ask for a name for the new army
        army_name = await collection_utils.ask_question(ctx, self.bot, "Enter a name for your new army:", str)

        # Deduct the requested troops and siegecraft from the garrison
        updated_troops = {unit: troops[unit] - requested_troops.get(unit, 0) for unit in troops}
        updated_siegecraft = {equipment: siegecraft[equipment] - requested_siegecraft.get(equipment, 0) 
                            for equipment in siegecraft}

        # Update the Garrison Sheet
        updated_garrison_data = [headers]
        for row in garrison_data:
            if row[1].strip() == garrison_name.strip():
                row[3] = army_utils.format_troops(updated_troops)  # Update troop count in the row
                row[4] = army_utils.format_troops(updated_siegecraft)  # Update siegecraft count in the row
            updated_garrison_data.append(row)
        sheet_utils.update_sheet_by_name("Garrisons", updated_garrison_data)

        # Add the new army to the Armies sheet
        formatted_requested_troops = army_utils.format_troops(requested_troops)
        formatted_requested_siegecraft = army_utils.format_troops(requested_siegecraft)
        sheet_utils.write_to_row("Armies", [
            house_name, army_name, formatted_requested_troops, formatted_requested_siegecraft, ctx.author.name
        ])

        # Confirm the creation of the army
        await ctx.send(f"**The army '{army_name}' has been created for House {house_name} from {garrison_name} with the "
                    f"following:**\n**Troops:** {formatted_requested_troops}\n**Siegecraft:** {formatted_requested_siegecraft}.**")
        
    @commands.command()
    async def reinforcegarrisonfromarmy(self, ctx):
        """
        Reinforces a garrison by transferring resources from an army and then deleting the army.
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
        army_data = sheet_utils.get_sheet_by_name("Armies")

        # Parse Garrison Data
        headers = garrison_data[0]
        garrison_data = garrison_data[1:]
        garrison_row = next((row for row in garrison_data if row[1].strip() == garrison_name.strip()), None)

        if not garrison_row:
            await ctx.send(f"**No garrison found with the name '{garrison_name}'. Please check the name and try again.**")
            return

        # Ask for the Army Name
        army_name = await collection_utils.ask_question(ctx, self.bot, "Enter the Army Name to transfer from:", str)

        player_id = auth_utils.get_player_id_from_army_fleet_name("Army", army_name)
        if player_id != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False

        # Parse Army Data
        army_row = next((row for row in army_data[1:] if row[1].strip() == army_name.strip()), None)
        if not army_row:
            await ctx.send(f"**No army found with the name '{army_name}'. Please check the name and try again.**")
            return

        # Extract Garrison and Army Details
        garrison_troops = army_utils.parse_troops(garrison_row[3])  # Assuming 4th column for troops
        army_troops = army_utils.parse_troops(army_row[2])  # Assuming 3rd column for troops

        # Merge Troops
        for unit, count in army_troops.items():
            garrison_troops[unit] = garrison_troops.get(unit, 0) + count

        # Update the Garrison Sheet
        updated_garrison_data = [headers]
        for row in garrison_data:
            if row[1].strip() == garrison_name.strip():
                row[3] = army_utils.format_troops(garrison_troops)  # Update troop count
            updated_garrison_data.append(row)
        sheet_utils.update_sheet_by_name("Garrisons", updated_garrison_data)

        # Remove the Army from the Armies Sheet
        updated_army_data = [army_data[0]] + [row for row in army_data[1:] if row[1].strip() != army_name.strip()]
        sheet_utils.update_sheet_by_name("Armies", updated_army_data)

        # Confirm Reinforcement
        await ctx.send(f"**The army '{army_name}' has been successfully reinforced into '{garrison_name}', and the army has been disbanded.**")

    @commands.command()
    async def mergearmies(self, ctx):
        """
        Merges two armies into one if they are in the same hex.
        """
        # Ask for the names of the two armies to merge
        army1_name = await collection_utils.ask_question(ctx, self.bot, 
                                                        "Enter the name of the first army to merge:", str)
        player_id_army_1 = auth_utils.get_player_id_from_army_fleet_name("Army", army1_name)
        army2_name = await collection_utils.ask_question(ctx, self.bot, 
                                                        "Enter the name of the second army to merge:", str)
        player_id_army_2 = auth_utils.get_player_id_from_army_fleet_name("Army", army2_name)
        if player_id_army_1 != ctx.message.author or player_id_army_2 != ctx.message.author:
            ctx.send("**You don't own this ye chancer!**")
            return False
        
        # Retrieve Army data
        army_data = sheet_utils.get_sheet_by_name("Armies")

        # Parse Army Data
        headers = army_data[0]
        army_data = army_data[1:]
        army1_row = next((row for row in army_data if row[1].strip() == army1_name.strip()), None)
        army2_row = next((row for row in army_data if row[1].strip() == army2_name.strip()), None)

        if not army1_row or not army2_row:
            await ctx.send(f"**One or both armies ('{army1_name}', '{army2_name}') could not be found. Please check the names and try again.**")
            return

        # Validate House and Hex
        house_name1, hex1 = army1_row[0], army1_row[2]
        house_name2, hex2 = army2_row[0], army2_row[2]
        if house_name1 != house_name2:
            await ctx.send(f"**Armies must belong to the same house to merge. '{army1_name}' belongs to {house_name1}, "
                        f"but '{army2_name}' belongs to {house_name2}.**")
            return
        if hex1 != hex2:
            await ctx.send(f"**Armies must be in the same hex to merge. '{army1_name}' is in hex {hex1}, but "
                        f"'{army2_name}' is in hex {hex2}.**")
            return

        # Extract and Merge Troops
        troops1 = army_utils.parse_troops(army1_row[3])  # Assuming 4th column holds troop details
        troops2 = army_utils.parse_troops(army2_row[3])
        merged_troops = {unit: troops1.get(unit, 0) + troops2.get(unit, 0) for unit in set(troops1) | set(troops2)}

        # Extract and Merge Siegecraft
        siegecraft1 = army_utils.parse_troops(army1_row[4])  # Assuming 5th column holds siegecraft details
        siegecraft2 = army_utils.parse_troops(army2_row[4])
        merged_siegecraft = {unit: siegecraft1.get(unit, 0) + siegecraft2.get(unit, 0) for unit in set(siegecraft1) | set(siegecraft2)}

        # Ask for the name of the merged army
        merged_army_name = await collection_utils.ask_question(ctx, self.bot, 
                                                            "Enter a name for the merged army:", str)

        # Update the Armies Sheet
        updated_army_data = [headers]
        for row in army_data:
            if row[1].strip() == army1_name.strip():
                row[1] = merged_army_name  # Rename the first army to the merged army
                row[3] = army_utils.format_troops(merged_troops)  # Update troops
                row[4] = army_utils.format_troops(merged_siegecraft)  # Update siegecraft
                updated_army_data.append(row)
            elif row[1].strip() != army2_name.strip():
                updated_army_data.append(row)  # Keep rows not related to the second army

        sheet_utils.update_sheet_by_name("Armies", updated_army_data)

        # Confirm the merge
        await ctx.send(f"**Armies '{army1_name}' and '{army2_name}' have been merged into '{merged_army_name}' "
                    f"in hex {hex1} with the following resources:**\n"
                    f"- Troops: {army_utils.format_troops(merged_troops)}\n"
                    f"- Siegecraft: {army_utils.format_troops(merged_siegecraft)}")


async def setup(bot):
    await bot.add_cog(ArmyCommands(bot))
