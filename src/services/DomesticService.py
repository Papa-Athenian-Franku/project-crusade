from utils.misc.AuthorisationUtils import AuthorisationUtils
from utils.sheets.LocalSheetUtils import LocalSheetUtils
from utils.misc.EmbedUtils import EmbedUtils

class DomesticService:
    def __init__(self):
        self.authorisation_utils = AuthorisationUtils()
        self.local_sheet_utils = LocalSheetUtils()
        self.embed_utils = EmbedUtils()

    def get_domestic_info(self, author, house):
        player_id = self.authorisation_utils.get_player_id_from_house_name(house)
        if player_id != author:
            return None
        else:
            sheet_values = self.local_sheet_utils.get_sheet_by_name("Domestics")
            column_headings = sheet_values[0]
            for row in sheet_values:
                if row[0] == house:
                    return self.embed_utils.set_info_embed_from_list(column_headings, row)