def parse_troops(troop_string):
    """
    Parses a troop string like '500 Infantry, 200 Cavalry' into a dictionary.
    """
    troops = {}
    for troop in troop_string.split(","):
        try:
            count, unit = troop.strip().split(" ", 1)
            troops[unit.strip()] = int(count.strip())
        except ValueError:
            raise ValueError(f"Invalid troop format: '{troop.strip()}'. Expected format: '<number> <type>'.")
    return troops

def format_troops(troops):
    """
    Formats a troop dictionary into a string like '500 Infantry, 200 Cavalry'.
    """
    return ", ".join(f"{count} {unit}" for unit, count in troops.items() if count > 0)

def validate_troop_request(available_troops, requested_troops):
    """
    Validates if the requested troops can be allocated from the available troops.
    """
    for unit, count in requested_troops.items():
        if count > available_troops.get(unit, 0):
            return False
    return True
