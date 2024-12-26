from utils.sheets.LocalSheetUtils import LocalSheetUtils

class AuthorisationUtils:
    def __init__(self):
        self.local_sheet_utils = LocalSheetUtils()

    def get_player_id_from_army_fleet_name(self, movement_type, army_fleet_name):
        # Find row of data['name'] from sheet data['movement_type'] (Army or Fleet). 
        army_fleet_sheet = self.local_sheet_utils.get_sheet_by_name("Armies") if movement_type.lower() == "army" else self.local_sheet_utils.get_sheet_by_name("Fleets")
        # Then find the House Name associated to army name in sheet data.
        house_name = None
        for row in army_fleet_sheet:
            if row[0] == "":
                return False
            if row[1] == army_fleet_name:
                house_name = row[0]
        # Find Player ID from sheet Claims 
        claims_sheet = self.local_sheet_utils.get_sheet_by_name("Claims")
        for row in claims_sheet:
            if row[0] == "":
                return False
            if row[0] == house_name:
                return row[1]
            
        return False

    def get_player_id_from_garrison_name(self, garrison):
        garrisons_sheet = self.local_sheet_utils.get_sheet_by_name("Garrisons")
        # Then find the House Name associated to army name in sheet data.
        house_name = None
        for row in garrisons_sheet:
            if row[0] == "":
                return False
            if row[1] == garrison:
                house_name = row[0]
        # Find Player ID from sheet Claims 
        claims_sheet = self.local_sheet_utils.get_sheet_by_name("Claims")
        for row in claims_sheet:
            if row[0] == "":
                return False
            if row[0] == house_name:
                return row[1]
            
        return False


    def get_player_id_from_house_name(self, house):
        claims_sheet = self.local_sheet_utils.get_sheet_by_name("Claims")
        for row in claims_sheet:
            if row[0] == "":
                return False
            if row[0] == house:
                return row[1]
            
        return False

    def get_player_id_from_holding_name(self, holding):
        domestics_sheet = self.local_sheet_utils.get_sheet_by_name("Domestics")
        claims_sheet = self.local_sheet_utils.get_sheet_by_name("Claims")
        house_name = None
        for row in domestics_sheet:
            if row[0] == "":
                return False
            if holding in row[3]:
                house_name = row[0]
        for row in claims_sheet:
            if row[0] == "":
                return False
            if row[0] == house_name:
                return row[1]
            
        return False