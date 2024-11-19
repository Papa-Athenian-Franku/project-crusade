import json
import math
from utilities import sheets_utilities as sheet_utils
from heapq import heappop, heappush

def retrieve_digital_map():
    sheet_values = sheet_utils.get_sheet_by_name("Map")

    # Extract the column headings from the first row
    column_headings = sheet_values[0]
    sheet_values = sheet_values[1:]  # Remove the headings from the data
    
    # Convert rows into a list of dictionaries
    map_data = []
    for row in sheet_values:
        row_dict = {column_headings[i]: row[i] for i in range(len(column_headings))}
        map_data.append(row_dict)

    return map_data  # No need to return as JSON unless required

# Heuristic function: straight-line distance between two hexes
def heuristic(hex1, hex2):
    x1, y1 = hex_to_coordinates(hex1)
    x2, y2 = hex_to_coordinates(hex2)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# A* Pathfinding Algorithm
def a_star(movement_type, start, goal, hexes):
    hex_map = {hex['Hex']: hex for hex in hexes}
    
    open_set = []
    heappush(open_set, (0, start))  # (priority, hex)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        _, current = heappop(open_set)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        neighbors = get_neighbors(movement_type, current, hex_map)
        for neighbor in neighbors:
            terrain_cost = terrain_movement_cost(movement_type, hex_map[neighbor])
            tentative_g_score = g_score[current] + terrain_cost
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))
    
    return None  # No path found

# Reconstruct the path from the came_from dictionary
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

# Determine movement cost based on terrain, with special rules for Mountains
def terrain_movement_cost(movement_type, hex_data):
    terrain = hex_data['Terrain']
    has_road = hex_data.get('Road', False)
    has_holding = hex_data.get('Holding', False)

    if movement_type == "army":
        if terrain == "Mountains":
            # Mountain is passable if it has either a Road or a Holding
            return 3 if has_road or has_holding else float('inf')
        if terrain == "Sea":
            return float('inf')  # Sea is impassable for army
        # Cost for other terrains
        terrain_costs = {"Hills": 2, "Swamp": 4, "Desert": 3}
        return terrain_costs.get(terrain, 1)  # Default cost for other terrains

    if movement_type == "fleet" and terrain == "Sea":
        return 1
    return float('inf')  # Non-sea is impassable by ship

# Get the neighbors of a hex, taking into account terrain passability
def get_neighbors(movement_type, hex_id, hex_map):
    col, row = hex_id[0], int(hex_id[1:])
    neighbors = []
    
    # Direction offsets for odd and even columns
    odd_offsets = [(-1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]
    even_offsets = [(-1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (1, 0)]
    
    # Determine if the column is odd or even
    column_index = ord(col) - ord('A')
    offsets = odd_offsets if column_index % 2 != 0 else even_offsets
    
    # Check all possible neighbors
    for dx, dy in offsets:
        neighbor_col = chr(ord(col) + dx)
        neighbor_row = row + dy
        neighbor_id = f"{neighbor_col}{neighbor_row}"
        
        # Check if the neighbor exists and is not impassable (based on its properties)
        if neighbor_id in hex_map:
            neighbor_data = hex_map[neighbor_id]
            if terrain_movement_cost(movement_type, neighbor_data) != float('inf'):  # Ensure it's not impassable
                neighbors.append(neighbor_id)
    
    return neighbors

# Convert hex IDs to numerical coordinates for distance calculations
def hex_to_coordinates(hex_id):
    col, row = hex_id[0], int(hex_id[1:])
    column_index = ord(col) - ord('A')
    return column_index, row

def retrieve_movement_path(movement_type, start, goal):
    hexes = retrieve_digital_map()

    # If start or goal is a Holding name, resolve it to a hex ID using the Holding key
    start_hex = None
    goal_hex = None

    for hex_data in hexes:
        if hex_data.get('Holding Name') == start:
            start_hex = hex_data['Hex']  # Get the hex ID from the Holding
        if hex_data.get('Holding Name') == goal:
            goal_hex = hex_data['Hex']  # Get the hex ID from the Holding

    if not start_hex or not goal_hex:
        print("Invalid start or goal Holding name.")
        return None

    # Use the resolved hex IDs for the a_star function
    path = a_star(movement_type, start_hex, goal_hex, hexes)
    
    if path:
        print("Path found:", path)
    else:
        print("No path found.")
    
    return path

