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
        