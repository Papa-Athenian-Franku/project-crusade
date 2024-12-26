from discord.ext import commands
from utils.sheets.LocalSheetUtils import LocalSheetUtils

class HoldingController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.local_sheet_utils = LocalSheetUtils()

    @commands.command()
    async def holding(self, ctx, holding):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Holdings")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == holding:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

async def setup(bot):
    await bot.add_cog(HoldingController(bot))