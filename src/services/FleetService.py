from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.EmbedUtils import EmbedUtils

class FleetService:
    def __init__(self):
        self.local_sheet_utils = LocalSheetUtils()
        self.embed_utils = EmbedUtils()

    def retrieve_fleet(self, fleet):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Fleets")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == fleet:
                return self.embed_utils.set_info_embed_from_list(column_headings, row)