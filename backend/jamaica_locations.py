"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Jamaica locations database with coordinates for Kingston metropolitan area.
This file manages the location data used for our routing algorithms.
"""

import json
import os

def initialize_jamaica_locations():
    """
    Creates a dictionary with Jamaican locations and their coordinates.
    
    This function sets up our core database of locations in the Kingston area,
    including their names and exact positions on the map. This serves as the
    foundation for all our route calculations.
    """
    locations = {
        # Liguanea and surrounding areas
        "liguanea": {"lat": 18.019832, "lng": -76.767835, "display_name": "Liguanea"},
        "halfway_tree": {"lat": 18.012079, "lng": -76.797419, "display_name": "Halfway Tree"},
        "barbican": {"lat": 18.030726, "lng": -76.775300, "display_name": "Barbican"},
        "hope_zoo": {"lat": 18.02634, "lng": -76.7451838, "display_name": "Hope Zoo"},
        "mona_heights": {"lat": 18.014116, "lng": -76.753296, "display_name": "Mona Heights"},
        "mona": {"lat": 18.008781, "lng": -76.753514, "display_name": "Mona"},
        "university_hospital": {"lat": 18.009067, "lng": -76.744630, "display_name": "University Hospital"},
        "new_kingston": {"lat": 18.005954, "lng": -76.787620, "display_name": "New Kingston"},
        "cross_roads": {"lat": 17.993840, "lng": -76.788059, "display_name": "Cross Roads"},
        "papine": {"lat": 18.015629, "lng": -76.742468, "display_name": "Papine"},
        
        # Additional important locations
        "spanish_town": {"lat": 17.9991, "lng": -76.9525, "display_name": "Spanish Town"},
        "port_royal": {"lat": 17.9367, "lng": -76.8430, "display_name": "Port Royal"},
        "constant_spring": {"lat": 18.0490, "lng": -76.7935, "display_name": "Constant Spring"},
        "manor_park": {"lat": 18.0520, "lng": -76.7910, "display_name": "Manor Park"},
        "old_harbour": {"lat": 17.938941226820827, "lng": -77.11298737125755, "display_name": "Old Harbour"},
    }
    
    # Save to file for future use
    save_locations_to_file(locations, 'jamaica_locations.json')
    -77.11298737125755
    return locations

def save_locations_to_file(locations, filename='jamaica_locations.json'):
    """
    Saves our location database to a JSON file.
    
    This allows us to easily load the locations again later without
    having to recreate the whole dictionary each time.
    """
    with open(filename, 'w') as f:
        json.dump(locations, f, indent=2)  # indent=2 makes the file human-readable
    print(f"Saved {len(locations)} locations to {filename}")

def load_locations_from_file(filename='jamaica_locations.json'):
    """
    Loads location data from a JSON file, or creates it if the file doesn't exist.
    
    This is usually the main function called by other parts of the application
    when they need access to the location database.
    """
    if os.path.exists(filename):
        # If the file exists, load the data from it
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        # If not, create a fresh set of location data
        return initialize_jamaica_locations()