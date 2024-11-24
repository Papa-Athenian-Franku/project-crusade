import settings
from discord.ext import commands, tasks
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import pathfinding_utilities as path_utils
from utilities import authorisation_utilities as auth_utils

class Movements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.map = path_utils.retrieve_digital_map()
        self.movements = {}  # Dictionary to store movements in memory
        self.load_movements()  # Load movements when the bot starts
        self.update_movements.start()  # Start the background task

    def load_movements(self):
        sheet_values = sheet_utils.get_sheet_by_name("Movements")
        if not sheet_values:
            print("Error: Could not retrieve data for 'Movements'.")
            return
        
        for row in sheet_values[1:]:
            movement_type, name, reason, path, current_hex, minutes_per_hex, minutes_since_last_hex = row
            path = path.split(",")  # Convert path string to list
            self.movements[name] = {
                'movement_type': movement_type,
                'name': name,
                'reason': reason,
                'path': path,
                'current_hex': current_hex,
                'minutes_per_hex': int(minutes_per_hex),
                'minutes_since_last_hex': int(minutes_since_last_hex)
            }

    @tasks.loop(minutes=1)  # This will run every minute
    async def update_movements(self):
        updated_data = []
        
        for name, movement in self.movements.items():
            path = movement['path']
            current_hex = movement['current_hex']
            minutes_per_hex = movement['minutes_per_hex']
            minutes_since_last_hex = movement['minutes_since_last_hex']
            
            # Update Minutes Since Last Hex
            minutes_since_last_hex += 1  # Increment by 1 minute
            
            # Check if it's time to move to the next hex
            if minutes_since_last_hex >= minutes_per_hex:
                # Update Current Hex to the next one in the path
                current_hex_index = path.index(current_hex)
                
                if current_hex_index < len(path) - 1:
                    # Move to the next hex
                    current_hex = path[current_hex_index + 1]
                    minutes_since_last_hex = 0  # Reset minutes since last hex
                else:
                    # If it's the last hex, trigger complete movement
                    await self.complete_movement(movement['name'])  # Call the complete movement function
                    current_hex = path[-1]  # Ensure the last hex is set
                
            # Update the movement in memory
            self.movements[name].update({
                'current_hex': current_hex,
                'minutes_since_last_hex': minutes_since_last_hex
            })

            # Append the updated data to write it back to the sheet
            updated_data.append([
                movement['movement_type'],
                movement['name'],
                movement['reason'],
                ",".join(path),
                current_hex,
                minutes_per_hex,
                minutes_since_last_hex
            ])
        
        # Write the updated data back to the sheet
        sheet_utils.update_sheet_by_name("Movements", [sheet_utils.get_sheet_by_name("Movements")[0]] + updated_data)

    async def complete_movement(self, name):
        data = self.movements[name]
        destination = await self.search_map_for_destination(data['current_hex'])
        channel = self.bot.get_channel(settings.MOVEMENTS_CHANNEL) #  Gets channel from settings.py
        await channel.send(f"- The {data['name']} arrives at {destination}.\nThey intend to: {data['reason']}")
        
        # Send player embed dm of movement info.
        user = self.bot.fetch_user(auth_utils.get_player_id_from_army_fleet_name(data['movement_type'], data['name']))
        await user.send(
                "**Your movement is finished pookie :)**",
                embed=embed_utils.set_info_embed_from_list(
                    [
                        "Embed Title",
                        "Reason",
                        "Starting Hex ID", 
                        "Destination", 
                        "Path of Hex IDs",
                        "Minutes Per Hex", 
                        "Estimated Time to Completion"
                    ],
                    [
                        f"Movement from {data['path'][0]} to {destination}.", 
                        data['reason'],
                        data['path'][0],
                        destination, 
                        data['path'],
                        data['minutes_per_hex']
                    ]
                )
            )

        # Remove the movement from memory
        if name in self.movements:
            del self.movements[name]
        
        # Remove the movement from the sheet (Overwrite the entire sheet minus the completed movement)
        sheet_values = sheet_utils.get_sheet_by_name("Movements")
        updated_rows = [sheet_values[0]]  # Keep the header row
        
        for row in sheet_values[1:]:
            if row[1] != name:  # Don't add the completed movement
                updated_rows.append(row)
        
        # Overwrite the sheet without the completed movement
        sheet_utils.update_sheet_by_name("Movements", updated_rows)
    
    async def search_map_for_destination(self, destination):
        # Iterate through each row in the map data
        for row in self.map:
            if row["Hex"] == destination:
                # Check if a Holding Name exists for the current hex
                if row.get("Holding Name"):  # Ensure the key exists in the dictionary
                    return row["Holding Name"]
        
        # If no Holding Name is found, return the hex ID
        return destination

async def setup(bot):
    await bot.add_cog(Movements(bot))
