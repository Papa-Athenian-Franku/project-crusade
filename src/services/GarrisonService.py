from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.EmbedUtils import EmbedUtils

class GarrisonService:
    def __init__(self):
        self.local_sheet_utils = LocalSheetUtils()
        self.embed_utils = EmbedUtils()

    def retrieve_garrison(self, garrison):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Garrisons")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == garrison or row[2] == garrison:
                return self.embed_utils.set_info_embed_from_list(column_headings, row)