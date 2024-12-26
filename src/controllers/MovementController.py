from discord.ext import commands
from services.MovementService import MovementService
from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.AuthorisationUtils import AuthorisationUtils
from utils.misc.CollectionUtils import CollectionUtils

class MovementController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.movement_service = MovementService()
        self.local_sheet_utils = LocalSheetUtils()
        self.auth = AuthorisationUtils()
        self.collection_utils = CollectionUtils()
        
    @commands.command()
    async def movement(self, ctx):
        constructed_embed = await self.movement_service.create_new_movement()
        if constructed_embed is not None:
            await ctx.send(
                "**Successful Movement Creation, TY Pookie :)**",
                embed=constructed_embed)
        else:
            await ctx.send("Movement Creation Failed. Start again but be less retarded please.")

    @commands.command()
    async def mymovements(self, ctx):
        """
        Show all ongoing movements for the player issuing the command.
        """
        player_id = ctx.message.author  # Get the player's ID from the context
        movements = self.local_sheet_utils.get_sheet_by_name("Movements")  # Read the Movements sheet
        ongoing_movements = []

        # Check each movement entry for the player's ID
        for row in movements:
            army_fleet_name = row[1]
            path = row[3]
            current_hex = row[4]
            associated_player_id = self.auth.get_player_id_from_army_fleet_name(row[0].title(), army_fleet_name)

            if associated_player_id == str(player_id):
                # Append formatted movement details to the list
                ongoing_movements.append(f"**{army_fleet_name}:** Path: {path}, Current Hex: {current_hex}")

        # If no movements, notify the player
        if not ongoing_movements:
            await ctx.author.send("**You have no ongoing movements.**")
        else:
            # Send the list of movements to the player's DMs
            movement_message = "**All Player Movements:**\n" + "\n".join(ongoing_movements)
            await ctx.author.send(movement_message)

    @commands.command()
    async def movement(self, ctx):
        """
        Retrieve detailed movement information for a specific army or fleet.
        """
        movements = self.local_sheet_utils.get_sheet_by_name("Movements")
        if not movements:
            await ctx.author.send("**There are no movements currently.**")
            return
        
        # Ask for the Army or Fleet name
        army_fleet_name = await self.collection_utils.ask_question(
            ctx, self.bot,
            "Army or Fleet Name: (E.G., 1st Army of House O'Neill)", str
        )
        
        # Find the movement entry for the given name
        movement_details = next((row for row in movements if row[1] == army_fleet_name), None)

        if not movement_details:
            await ctx.author.send(f"**No movement details found for {army_fleet_name}.**")
            return

        # Get the Movement Type and associated Player ID
        movement_type = movement_details[0].title()  # E.g., "Army" or "Fleet"
        associated_player_id = self.auth.get_player_id_from_army_fleet_name(movement_type, army_fleet_name)

        # Check if the player is authorized
        player_id = ctx.message.author
        if associated_player_id != str(player_id):
            await ctx.send("**You are not the associated claim dumb dumb!**")
            return

        # Format the movement details into an embed
        await ctx.message.author.send(
                "**Your movement details :)**",
                embed=embed_utils.set_info_embed_from_list(
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
            )

async def setup(bot):
    await bot.add_cog(MovementController(bot))