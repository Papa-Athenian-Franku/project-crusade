from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.EmbedUtils import EmbedUtils

class MiscService:
    def __init__(self):
        self.local_sheet_utils = LocalSheetUtils()
        self.embed_utils = EmbedUtils()

    def retrieve_prices_info(self):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("References")
        column_headings = sheet_values[0]
        return self.embed_utils.set_info_embed_from_list(column_headings, sheet_values)

    def retrieve_wars_info(self):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Wars")
        column_headings = sheet_values[0]
        return self.embed_utils.set_info_embed_from_list(column_headings, sheet_values)

    def retrieve_hex_info(self, hex):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Map")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[0] == hex:
                return self.embed_utils.set_info_embed_from_list(column_headings, row)