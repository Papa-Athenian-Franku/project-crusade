from utilities import local_sheets_utilities as sheet_utils

def get_player_id_from_army_fleet_name(movement_type, army_fleet_name):
    # Find row of data['name'] from sheet data['movement_type'] (Army or Fleet). 
    army_fleet_sheet = sheet_utils.get_sheet_by_name("Armies") if movement_type.lower() == "army" else sheet_utils.get_sheet_by_name("Fleets")
    # Then find the House Name associated to army name in sheet data.
    house_name = None
    for row in army_fleet_sheet:
        if row[0] == "":
            return False
        if row[1] == army_fleet_name:
            house_name = row[0]
    # Find Player ID from sheet Claims 
    claims_sheet = sheet_utils.get_sheet_by_name("Claims")
    for row in claims_sheet:
        if row[0] == "":
            return False
        if row[0] == house_name:
            return row[1]
        
    return False

def get_player_id_from_garrison_name(garrison):
    garrisons_sheet = sheet_utils.get_sheet_by_name("Garrisons")
    # Then find the House Name associated to army name in sheet data.
    house_name = None
    for row in garrisons_sheet:
        if row[0] == "":
            return False
        if row[1] == garrison:
            house_name = row[0]
    # Find Player ID from sheet Claims 
    claims_sheet = sheet_utils.get_sheet_by_name("Claims")
    for row in claims_sheet:
        if row[0] == "":
            return False
        if row[0] == house_name:
            return row[1]
        
    return False


def get_player_id_from_house_name(house):
    claims_sheet = sheet_utils.get_sheet_by_name("Claims")
    for row in claims_sheet:
        if row[0] == "":
            return False
        if row[0] == house:
            return row[1]
        
    return False

def get_player_id_from_holding_name(holding):
    domestics_sheet = sheet_utils.get_sheet_by_name("Domestics")
    claims_sheet = sheet_utils.get_sheet_by_name("Claims")
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