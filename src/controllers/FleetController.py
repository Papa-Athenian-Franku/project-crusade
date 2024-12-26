from discord.ext import commands

class FleetController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # Accepts Fleet Name
    @commands.command()
    async def fleet(self, ctx, fleet):
        player_id = auth_utils.get_player_id_from_army_fleet_name("Fleet", fleet)
        if player_id != ctx.message.author:
            await ctx.send("**You are not the associated claim dumb dumb!**")
        else:
            sheet_values = sheet_utils.get_sheet_by_name("Fleets")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[1] == fleet:
                    await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

async def setup(bot):
    await bot.add_cog(FleetController(bot))