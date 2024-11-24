from utilities import local_sheets_utilities as sheet_utils
from utilities import collection_utilities as collection_utils

async def collectmovementunitsinfo(bot, ctx):
    movement_type = await collection_utils.ask_question(ctx, bot, 
                                                  "Movement Type: (Army or Fleet)", str)
    army_fleet_name = await collection_utils.ask_question(ctx, bot, 
                                                    f"Name of {movement_type}: (E.G, 1st Army of Antioch)", str)
    reason = await collection_utils.ask_question(ctx, bot, 
                                                    "Reason for Movement: (Conquest, Raid, Reinforce, Other)", str)
    return movement_type, army_fleet_name, reason

async def collectautofillavoidinfo(movement_type, army_fleet_name):
    """
    Collects enemy holdings to avoid based on the provided army or fleet information.
    """
    units_sheet = sheet_utils.get_sheet_by_name("Armies" if movement_type.lower() == "army" else "Fleets")
    domestic_sheet = sheet_utils.get_sheet_by_name("Domestics")
    wars_sheet = sheet_utils.get_sheet_by_name("Wars")

    # Get house name
    house_name = get_house_name(units_sheet, army_fleet_name)
    if not house_name:
        return None, None
    
    # Get Starting Hex
    start = get_starting_hex(units_sheet, army_fleet_name)
    if not start:
        return None, None

    # Get house religion
    house_religion = get_house_religion(domestic_sheet, house_name)
    if not house_religion:
        return None, None

    # Get house enemies
    house_enemies = get_house_enemies(wars_sheet, house_name, house_religion)

    # Get enemy holdings
    enemy_holdings = get_enemy_holdings(domestic_sheet, house_enemies)
    return start, enemy_holdings if enemy_holdings else []
    

def get_house_name(units_sheet, army_fleet_name):
    """
    Retrieves the house name associated with the given army or fleet.
    """
    for army_fleet in units_sheet:
        if army_fleet[0] and army_fleet[1] == army_fleet_name:
            return army_fleet[0]
    return None

def get_starting_hex(units_sheet, army_fleet_name):
    """
    Retrieves the Hex associated with the given army or fleet.
    """
    for army_fleet in units_sheet:
        if army_fleet[0] and army_fleet[1] == army_fleet_name:
            return army_fleet[2]
    return None


def get_house_religion(domestic_sheet, house_name):
    """
    Retrieves the religion associated with the given house.
    """
    for house in domestic_sheet:
        if house[0] and house[0] == house_name:
            return house[4]
    return None


def get_house_enemies(wars_sheet, house_name, house_religion):
    """
    Retrieves a list of enemies based on wars involving the house.
    """
    enemies = []
    for war in wars_sheet:
        if not war[0]:  # Skip empty rows
            continue

        if war[1] == "Religious":
            if house_religion in war[2]:
                enemies.extend(war[3])
            elif house_religion in war[3]:
                enemies.extend(war[2])

        elif war[1] == "Domestic":
            if house_name in war[2]:
                enemies.extend(war[3])
            elif house_name in war[3]:
                enemies.extend(war[2])

    return list(set(enemies))  # Remove duplicates


def get_enemy_holdings(domestic_sheet, house_enemies):
    """
    Retrieves a list of enemy holdings for the given enemies.
    """
    holdings = []
    for house in domestic_sheet:
        if house[0] in house_enemies:
            holdings.append(house[3])  # Assume column 3 contains holdings
    return holdings

async def collectmovementinfo(bot, ctx, auto_fill_avoid_list):
    goal = await collection_utils.ask_question(ctx, bot, 
                                         "Destination Hex ID or Holding Name: (Hex ID or Holding Name)", str)
    avoid_list = []
    while True:
        await ctx.send(f"Automatically avoiding enemy holding tiles: {', '.join(auto_fill_avoid_list)}")

        avoid = await collection_utils.ask_question(ctx, bot, 
                                                    "Avoid Position: (Hex ID or Holding Name or None)", str)
        if avoid.lower() == "none":
            break

        avoid_list.append(avoid)
        finished = await collection_utils.ask_question(ctx, bot, 
                                                 "Are you finished with Avoid Positions: (Yes or No)", str)
        if finished.lower() == "yes" or finished.lower() == "y":
            break

    return goal, avoid_list.extend(auto_fill_avoid_list)

async def collectarmyfleetcomposition(movement_type, army_fleet_name):
    units_sheet = sheet_utils.get_sheet_by_name("Armies") if movement_type.lower() == "army" else sheet_utils.get_sheet_by_name("Fleets")

    troops = None
    siegecraft = None
    ships = None

    for army_fleet in units_sheet:
        if army_fleet[0] == "":
            return None
        elif army_fleet[1] == army_fleet_name:
            troops = army_fleet[3]
            siegecraft = army_fleet[4]
            if movement_type.lower() != "army":
                ships = army_fleet[5]

    return troops, siegecraft, ships

async def getminutespertile(troops, siegecraft):
    """
    Determines movement speed based on unit type.
    """
    if siegecraft is not None:
        return 90  # Army with siegecraft moves slower

    return getarmyminutespertile(troops)  # Default army speed

def getarmyminutespertile(troops_data):
    troops = {}
    items = troops_data.split(",")
    
    # Parse troops data into a dictionary
    for item in items:
        parts = item.strip().split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            troops[parts[1].strip()] = int(parts[0])

    # Determine minutes per tile based on troop composition
    has_cavalry = False
    has_non_cavalry = False

    for troop_type in troops:
        if "Cavalry" in troop_type:
            has_cavalry = True
        else:
            has_non_cavalry = True

        # Break early if both types are found
        if has_cavalry and has_non_cavalry:
            break

    # Return the appropriate time per tile
    if has_cavalry and not has_non_cavalry:
        return 45  # Only cavalry
    return 60  # Includes non-cavalry troops
