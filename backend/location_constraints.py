"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Helper module to manage location constraints and available routes.
This file handles providing information about what locations and routes are available to users.
"""

import json
import os
from itertools import permutations

def get_available_locations(locations_file="jamaica_locations.json"):
    """
    Gets a list of all available locations that can be used in the application.
    
    This function reads our locations database and formats it in a way that's
    easy to display to users, like in a dropdown menu or suggestion list.
    """
    if not os.path.exists(locations_file):
        return []  # Return empty list if file doesn't exist
        
    # Load the locations data
    with open(locations_file, 'r') as f:
        locations = json.load(f)
    
    # Format locations for display
    available_locations = []
    
    # Convert from dictionary to a list of location objects
    for loc_id, loc_data in locations.items():
        available_locations.append({
            "id": loc_id,  # Internal ID used by the system
            "name": loc_data.get("display_name", loc_id.capitalize())  # Human-readable name
        })
        
    # Sort alphabetically by name for better user experience
    return sorted(available_locations, key=lambda x: x["name"])

def get_available_routes(locations_file="jamaica_locations.json"):
    """
    Generates a list of all possible routes between available locations.
    
    This creates all possible combinations of source and destination,
    which can be used to populate route selection interfaces.
    """
    # Get the list of available locations
    available_locations = get_available_locations(locations_file)
    
    # Generate all possible pairs (source-destination combinations)
    all_routes = []
    for source in available_locations:
        for dest in available_locations:
            # Don't create routes from a location to itself
            if source["id"] != dest["id"]:
                all_routes.append({
                    "source": source["id"],
                    "source_name": source["name"],
                    "destination": dest["id"],
                    "destination_name": dest["name"],
                    "display": f"{source['name']} to {dest['name']}"  # Human-readable label
                })
    
    # Sort by display name for easier browsing
    return sorted(all_routes, key=lambda x: x["display"])

def is_valid_location(location_name, locations_file="jamaica_locations.json"):
    """
    Checks if a location name is valid and available in our system.
    
    This helps validate user input when they type in location names,
    and also maps partial or display names to our internal location IDs.
    """
    if not os.path.exists(locations_file):
        return False, None  # Can't validate if file doesn't exist
        
    # Load the locations data
    with open(locations_file, 'r') as f:
        locations = json.load(f)
    
    # Explicitly disallow "kingston" by itself
    # (We have "new_kingston" but not plain "kingston")
    if location_name.lower() == "kingston":
        return False, None
    
    # Try direct match on location ID first (most efficient)
    if location_name in locations:
        return True, location_name
    
    # If no direct match, try to match by display name (case insensitive)
    location_name_lower = location_name.lower()
    for loc_id, loc_data in locations.items():
        if location_name_lower in loc_data.get("display_name", "").lower():
            # Special case: avoid matching "kingston" to "new_kingston"
            if location_name_lower == "kingston" and loc_id == "new_kingston":
                continue
            return True, loc_id
    
    # If we get here, no match was found
    return False, None