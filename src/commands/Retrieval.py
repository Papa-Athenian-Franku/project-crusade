from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import authorisation_utilities as auth_utils
from utilities import collection_utilities as collection_utils

class Retrieval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def holdinginfo(self, ctx, holding):
        sheet_values = sheet_utils.get_sheet_by_name("Holdings")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == holding:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Either Garrison Name or Holding Name
    @commands.command()
    async def garrisoninfo(self, ctx, garrison):
        player_id = auth_utils.get_player_id_from_garrison_name(garrison)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            sheet_values = sheet_utils.get_sheet_by_name("Garrisons")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[1] == garrison or row[2] == garrison:
                    await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Army Name
    @commands.command()
    async def armyinfo(self, ctx, army):
        player_id = auth_utils.get_player_id_from_army_fleet_name("Army", army)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            sheet_values = sheet_utils.get_sheet_by_name("Armies")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[1] == army:
                    await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    # Accepts Fleet Name
    @commands.command()
    async def fleetinfo(self, ctx, fleet):
        player_id = auth_utils.get_player_id_from_army_fleet_name("Fleet", fleet)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            sheet_values = sheet_utils.get_sheet_by_name("Fleets")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[1] == fleet:
                    await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    @commands.command()
    async def prices(self, ctx):
        sheet_values = sheet_utils.get_sheet_by_name("References")
        column_headings = sheet_values[0]
        await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, sheet_values))

    @commands.command()
    async def wars(self, ctx):
        sheet_values = sheet_utils.get_sheet_by_name("Wars")
        column_headings = sheet_values[0]
        await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, sheet_values))

    @commands.command()
    async def hexinfo(self, ctx, hex):
        sheet_values = sheet_utils.get_sheet_by_name("Map")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == hex:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

    @commands.command()
    async def retrievemovements(self, ctx):
        """
        Show all ongoing movements for the player issuing the command.
        """
        player_id = ctx.message.author  # Get the player's ID from the context
        movements = sheet_utils.get_sheet_by_name("Movements")  # Read the Movements sheet
        ongoing_movements = []

        # Check each movement entry for the player's ID
        for row in movements:
            army_fleet_name = row[1]
            path = row[3]
            current_hex = row[4]
            associated_player_id = auth_utils.get_player_id_from_army_fleet_name(row[0].title(), army_fleet_name)

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
    async def retrievemovement(self, ctx):
        """
        Retrieve detailed movement information for a specific army or fleet.
        """
        movements = sheet_utils.get_sheet_by_name("Movements")
        if not movements:
            await ctx.author.send("**There are no movements currently.**")
            return
        
        # Ask for the Army or Fleet name
        army_fleet_name = await collection_utils.ask_question(
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
        associated_player_id = auth_utils.get_player_id_from_army_fleet_name(movement_type, army_fleet_name)

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
    await bot.add_cog(Retrieval(bot))
