from discord.ext import commands
from utilities import local_sheets_utilities as sheet_utils
from utilities import embed_utilities as embed_utils
from utilities import authorisation_utilities as auth_utils

class Retrieval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def domesticinfo(self, ctx, house):
        player_id = auth_utils.get_player_id_from_house_name(house)
        if player_id != ctx.message.author:
            ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            sheet_values = sheet_utils.get_sheet_by_name("Domestics")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[0] == house:
                    await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

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
            ctx.send("**You are not the associated claim dumb dumb!**")
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
            ctx.send("**You are not the associated claim dumb dumb!**")
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
            ctx.send("**You are not the associated claim dumb dumb!**")
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
    async def claims(self, ctx):
        sheet_values = sheet_utils.get_sheet_by_name("Claims")
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

async def setup(bot):
    await bot.add_cog(Retrieval(bot))
