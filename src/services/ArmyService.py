from utils.misc.EmbedUtils import EmbedUtils

class ArmyService:
    def __init__(self):
        self.embed_utils = EmbedUtils()

    def retrieve_army(self, army):
        sheet_values = self.local_sheet_utils.get_sheet_by_name("Armies")
        column_headings = sheet_values[0]
        for row in sheet_values:
            if row[1] == army:
                return self.embed_utils.set_info_embed_from_list(column_headings, row)