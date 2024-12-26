from discord.ext import commands
from utils.sheets.LocalSheetUtils import LocalSheetUtils

class MiscController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.local_sheet_utils = LocalSheetUtils()

    @commands.command()
    async def prices(self, ctx):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("References")
        column_headings = sheet_values[0]
        await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, sheet_values))

    @commands.command()
    async def wars(self, ctx):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Wars")
        column_headings = sheet_values[0]
        await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, sheet_values))

    @commands.command()
    async def hex(self, ctx, hex):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Map")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == hex:
                await ctx.send(embed=embed_utils.set_info_embed_from_list(column_headings, row))

async def setup(bot):
    await bot.add_cog(MiscController(bot))
