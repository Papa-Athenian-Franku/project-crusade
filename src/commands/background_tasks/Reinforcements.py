import settings
from discord.ext import commands, tasks
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import authorisation_utilities as auth_utils

class Reinforcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.map = path_utils.retrieve_digital_map()
        self.completed_reinforcements = []
        self.update_reinforcements.start()  # Start the background task

    @tasks.loop(hours=24)  # This task runs daily
    async def update_reinforcements(self):
        # Load sheets
        reinforcements = sheet_utils.read_csv("Reinforcements.csv")  # List of dictionaries
        garrisons = sheet_utils.read_csv("Garrisons.csv")
        holdings = sheet_utils.read_csv("Holdings.csv")

        updated_reinforcements = []
        for reinforcement in reinforcements:
            # Decrement days remaining
            reinforcement["Days Remaining"] = int(reinforcement["Days Remaining"]) - 1

            if reinforcement["Days Remaining"] <= 0:
                # Reinforcement is complete
                self.completed_reinforcements.append(reinforcement)
                await self.complete_reinforcement(reinforcement, garrisons, holdings)
            else:
                updated_reinforcements.append(reinforcement)

        # Save the updated Reinforcements sheet
        sheet_utils.write_csv("Reinforcements.csv", updated_reinforcements)

    async def complete_reinforcement(self, reinforcement, garrisons, holdings):
        holding_name = reinforcement["Holding Name"]
        troop_count = int(reinforcement["Troop Count"])
        troop_name = reinforcement["Troop Name"]

        # Find the related holding and garrison
        holding = next((h for h in holdings if h["Name"] == holding_name), None)
        garrison = next((g for g in garrisons if g["Holding Name"] == holding_name), None)

        if not holding or not garrison:
            return  # If holding or garrison is missing, skip processing

        # Check garrison limits
        max_garrison = int(holding["Max Garrison"])
        current_garrison_count = sum(
            int(count) for troop in garrison["Troops"].split(", ") for count in troop.split(" ") if count.isdigit()
        )
        army_fleet_type, new_army_fleet = None, None
        if current_garrison_count + troop_count > max_garrison:
            # Create a new army if max garrison is exceeded
            army_fleet_type, new_army_fleet = await self.createarmy_fleet(holding_name, troop_name, troop_count)
        else:
            # Add the reinforcement to the garrison
            garrison["Troops"] += f", {troop_count} {troop_name}"
            sheet_utils.update_row("Garrisons.csv", garrison)

        # Notify the user via DM
        user_id = auth_utils.get_player_id_from_holding(holding_name)
        user = await self.bot.fetch_user(user_id)
        if user:
            if army_fleet_type == None and new_army_fleet == None:
                await user.send(
                    f"**Your reinforcement of {troop_count} {troop_name}(s) for {holding_name} is complete, pookie!**"
                )
            else:
                await user.send(
                f"**Your recruiment is finished pookie :)
                \nThough, you exceeded Maximum Garrison.
                \nSo a new {army_fleet_type} was created in the same hex.**",
                embed=embed_utils.set_info_embed_from_list(
                    [
                        "Embed Title",
                        "House Name",
                        f"{army_fleet_type} Name", 
                        "Hex", 
                        "Troops",
                        "Siegecraft",
                        "Ships"
                    ],
                    [
                        f"Recruitment created new {army_fleet_type}: {new_army_fleet}", 
                        new_army_fleet["House Name"],
                        new_army_fleet[f"{army_fleet_type} Name"],
                        new_army_fleet["Hex"], 
                        new_army_fleet["Troops"],
                        new_army_fleet["Siegecraft"],
                        new_army_fleet["Ships"]
                    ]
                )
            )

    async def createarmy_fleet(self, holding_name, troop_name, troop_count):
        """
        Create a new army or fleet entry depending on the reinforcement type.
        """
        # Load the Holdings and Domestics sheets
        holdings = sheet_utils.read_csv("Holdings.csv")
        domestics = sheet_utils.read_csv("Domestics.csv")
        holding = next((h for h in holdings if h["Name"] == holding_name), None)

        if not holding:
            print(f"Holding {holding_name} not found.")
            return

        # Find the house name from the Domestics sheet
        house_name = next((d["House Name"] for d in domestics if d["Holdings"] == holding_name), "Unknown House")
        if house_name == "Unknown House":
            print(f"House not found for holding {holding_name}.")
            return

        # Get the hex location from the map
        hex_location = await self.search_map_for_hex(holding_name)
        if hex_location == "Unknown Hex":
            print(f"Hex location not found for holding {holding_name}.")
            return

        if "Ship" in troop_name:  # Check if reinforcement involves ships
            # Create Fleet Entry
            fleets = sheet_utils.read_csv("Fleets.csv")
            fleet_name = f"{len(fleets) + 1} Fleet of {house_name}"
            new_fleet = {
                "House Name": house_name,
                "Fleet Name": fleet_name,
                "Hex": hex_location,
                "Troops": "-",  # No troops unless specified
                "Siegecraft": "-",  # No siege unless specified
                "Ships": f"{troop_count} {troop_name}"
            }
            fleets.append(new_fleet)
            sheet_utils.write_csv("Fleets.csv", fleets)
            print(f"Fleet '{fleet_name}' created with {troop_count} {troop_name} at {hex_location}.")
            return "Fleet", new_fleet
        else:
            # Create Army Entry
            armies = sheet_utils.read_csv("Armies.csv")
            army_name = f"{len(armies) + 1} Army of {house_name}"
            new_army = {
                "House Name": house_name,
                "Army Name": army_name,
                "Hex": hex_location,
                "Troops": f"{troop_count} {troop_name}",
                "Siegecraft": "-",  # Default, add siege units if needed
                "Ships": "-"
            }
            armies.append(new_army)
            sheet_utils.write_csv("Armies.csv", armies)
            print(f"Army '{army_name}' created with {troop_count} {troop_name} at {hex_location}.")
            return "Army", new_army


    async def search_map_for_hex(self, holding_name):
        """
        Search the map data for the hex location of a given holding.
        """
        # Assume the map is a pre-loaded attribute (list of dictionaries)
        for row in self.map:
            if row["Holding Name"] == holding_name:
                return row["Hex"]
        return "Unknown Hex"

async def setup(bot):
    await bot.add_cog(Reinforcements(bot))