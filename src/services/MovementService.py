from utils.MovementUtils import MovementUtils
from utils.misc.AuthorisationUtils import AuthorisationUtils
from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.EmbedUtils import EmbedUtils
from utils.pathfinding.PathfindingUtils import PathFindingUtils

class MovementService:
    def __init__(self):
        self.movement_utils = MovementUtils()
        self.authorisation_utils = AuthorisationUtils()
        self.local_sheet_utils = LocalSheetUtils()
        self.embed_utils = EmbedUtils()
        self.pathfinding_utils = PathFindingUtils()

    async def create_new_movement(self, ctx):
        successful_write = False
        while True:
            # Get Movement type, Army or Fleet, and Army or Fleet Name.
            movement_type, army_fleet_name, reason = await self.movement_utils.collectmovementunitsinfo(self.bot, ctx)
            if movement_type.lower() != "army" and movement_type.lower() != "fleet":
                break

            army_fleet_player_id = self.authorisation_utils.get_player_id_from_army_fleet_name(movement_type, army_fleet_name)
            if army_fleet_player_id != ctx.message.author:
                ctx.send("**You are not the associated claim dumb dumb!**")
                break

            # Get autofill avoid info based on Army/Fleet Name and Movement type.
            start, auto_fill_avoid_list = await self.movement_utils.collectautofillavoidinfo(movement_type, army_fleet_name)
            if auto_fill_avoid_list is None or start is None:
                break

            # Prompt user for destination, as well as any hexes to avoid.
            goal, avoid_list = await self.movement_utils.collectmovementinfo(self.bot, ctx, auto_fill_avoid_list)

            # Pathfind.
            path = self.pathfinding_utils.retrieve_movement_path(movement_type, start, goal, avoid_list)

            # Get Army/Fleet composition and determine movement speed per tile.
            troops, siegecraft, ships = await self.movement_utils.collectarmyfleetcomposition(movement_type, army_fleet_name)

             # Determine minutes per tile based on composition.
            if ships:
                minutes_per_tile = 45
            else:
                minutes_per_tile = await self.movement_utils.getminutespertile(troops, siegecraft)

            # Create Movement in Sheets.
            successful_write = self.local_sheet_utils.write_to_row("Movements", [movement_type, army_fleet_name, reason, path, path[0], minutes_per_tile, 0])
            break

        if successful_write:
            return self.embed_utils.set_info_embed_from_list(
                        [
                            "Embed Title",
                            "Reason",
                            "Starting Hex ID", 
                            "Destination Hex ID", 
                            "Path of Hex IDs",
                            "Minutes Per Hex", 
                            "Estimated Time to Completion"
                        ],
                        [
                            f"Movement from {start} to {goal}.",
                            reason,
                            start,
                            goal, 
                            path,
                            minutes_per_tile, 
                            minutes_per_tile * len(path)
                        ]
                    )
        else:
            return None
        
    def retrieve_user_movements(self, id):
        movements = self.local_sheet_utils.get_sheet_by_name("Movements")  # Read the Movements sheet
        ongoing_movements = []

        # Check each movement entry for the player's ID
        for row in movements:
            army_fleet_name = row[1]
            path = row[3]
            current_hex = row[4]
            associated_player_id = self.auth.get_player_id_from_army_fleet_name(row[0].title(), army_fleet_name)

            if associated_player_id == id:
                # Append formatted movement details to the list
                ongoing_movements.append(f"**{army_fleet_name}:** Path: {path}, Current Hex: {current_hex}")

        if not ongoing_movements:
            return False
        else:
            return ongoing_movements
        
    async def retrieve_specified_movement(self, ctx):
        movements = self.local_sheet_utils.get_sheet_by_name("Movements")
        if not movements:
            return False
        
        # Ask for the Army or Fleet name
        army_fleet_name = await self.collection_utils.ask_question(
            ctx, self.bot,
            "Army or Fleet Name: (E.G., 1st Army of House O'Neill)", str
        )
        
        # Find the movement entry for the given name
        movement_details = next((row for row in movements if row[1] == army_fleet_name), None)

        if not movement_details:
            return False

        # Get the Movement Type and associated Player ID
        movement_type = movement_details[0].title()  # E.g., "Army" or "Fleet"
        associated_player_id = self.auth.get_player_id_from_army_fleet_name(movement_type, army_fleet_name)

        # Check if the player is authorized
        player_id = ctx.message.author
        if associated_player_id != str(player_id):
            return False

        # Format the movement details into an embed
        return self.embed_utils.set_info_embed_from_list(
            [
                "Embed Title",
                "Reason",
                "Starting Hex ID", 
                "Destination", 
                "Path of Hex IDs",
                "Minutes Per Hex", 
                "Minutes Since Last Hex"
            ],
            [
                f"Movement from {movement_details[3][0]} to {movement_details[3][-1]}.", 
                movement_details[2],
                movement_details[3][0],
                movement_details[3][-1], 
                movement_details[3],
                movement_details[5],
                movement_details[6]
            ]
        )