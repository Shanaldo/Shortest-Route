"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Distance and time matrix calculation and storage.
This file helps calculate how far apart locations are and how long it takes to travel between them.
"""

# Import necessary libraries
import json      # Used for saving and loading data in a readable format
import time      # Provides functions for working with time
import os        # Helps interact with the operating system (like checking if files exist)
import math      # Provides mathematical functions
from geopy.distance import geodesic  # A special function that calculates distances on Earth

# Average speeds for different road types in Jamaica (kilometers per hour)
# We use these to estimate travel times based on the type of road
ROAD_SPEEDS = {
    "highway": 100,  # Highway speed - fastest roads like freeways
    "primary": 70,   # Primary road speed - major roads through cities
    "secondary": 50, # Secondary road speed - connecting roads
    "tertiary": 40,  # Tertiary road speed - small roads within communities
    "other": 30      # Other roads speed - narrow or residential streets
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points on Earth using latitude and longitude.
    The geodesic function accounts for the curvature of the Earth.
    
    lat1, lon1: Coordinates of first point (latitude and longitude)
    lat2, lon2: Coordinates of second point (latitude and longitude)
    
    Returns: Distance in kilometers
    """
    # Format the coordinates as tuples (pairs of numbers)
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    # Use the geodesic formula to calculate distance on Earth's surface
    return geodesic(coords_1, coords_2).kilometers

def estimate_travel_time(distance, road_type="secondary"):
    """
    Estimate how long it takes to travel a certain distance based on the road type.
    Different road types have different average speeds.
    
    distance: Distance in kilometers
    road_type: Type of road (highway, primary, secondary, tertiary, other)
    
    Returns: Estimated travel time in minutes
    """
    # If the road type isn't in our list, default to secondary road
    if road_type not in ROAD_SPEEDS:
        road_type = "secondary"  # Default to secondary if unknown road type
        
    # Get the average speed for this road type
    speed = ROAD_SPEEDS[road_type]
    # Calculate time in minutes: time = distance / speed * 60
    # (We divide by speed to get hours, then multiply by 60 to get minutes)
    return (distance / speed) * 60

def classify_road_type(source, destination, locations):
    """
    Determine what kind of road connects two locations.
    Includes proper handling for avoid_highway logic for Spanish Town and Old Harbour.
    """

    # Bi-directional helper
    def is_match(pair_list):
        return any((source == a and destination == b) or (source == b and destination == a) for a, b in pair_list)

    # Highways (to be avoided when user chooses avoid_highways=True)
    highway_routes = [
      
    ]

    # Primary roads (main roads, non-highways)
    primary_routes = [
        ("new_kingston", "halfway_tree"),
        ("new_kingston", "cross_roads"),
        ("new_kingston", "liguanea"),
        ("constant_spring", "halfway_tree"),
        ("manor_park", "constant_spring"),

        # Non-highway connections for Spanish Town & Old Harbour
        ("spanish_town", "cross_roads"),
        ("old_harbour", "cross_roads"),
        ("spanish_town", "halfway_tree"),
        ("old_harbour", "halfway_tree"),
        ("old_harbour", "liguanea"),
        ("spanish_town", "liguanea"),
    ]

    # Tertiary roads for university areas
    university_areas = {"mona", "papine", "university_hospital", "mona_heights", "hope_zoo"}

    # Classification logic
    if is_match(highway_routes):
        return "highway"
    if is_match(primary_routes):
        return "primary"
    if source in university_areas and destination in university_areas:
        return "tertiary"
    
    # Default fallback
    return "primary"


def generate_distance_matrix(locations_data, output_file="distance_matrix.json"):
    """
    Generate and save a matrix (table) of distances and travel times between all locations.
    This creates a lookup table we can use later instead of recalculating each time.
    
    locations_data: Dictionary of locations with coordinates
    output_file: File to save the matrix to
    
    Returns: Dictionary with distance and time matrices
    """
    # Initialize empty dictionaries to store our results
    matrix = {"distances": {}, "times": {}}
    
    # Calculate distances and times between all pairs of locations
    # This is a nested loop that checks every possible pair
    for source_id, source in locations_data.items():
        # Create empty dictionaries for this source location
        matrix["distances"][source_id] = {}
        matrix["times"][source_id] = {}
        
        # For each destination location
        for dest_id, dest in locations_data.items():
            # Skip calculating distance to itself
            if source_id != dest_id:
                # Calculate distance between the two locations
                distance = calculate_distance(
                    source["lat"], source["lng"], 
                    dest["lat"], dest["lng"]
                )
                # Round to 2 decimal places and store in the matrix
                matrix["distances"][source_id][dest_id] = round(distance, 2)
                
                # Determine road type and estimate travel time
                road_type = classify_road_type(source_id, dest_id, locations_data)
                travel_time = estimate_travel_time(distance, road_type)
                # Round to 2 decimal places and store in the matrix
                matrix["times"][source_id][dest_id] = round(travel_time, 2)
    
    # Save to file for later use
    with open(output_file, 'w') as f:
        json.dump(matrix, f, indent=2)  # indent=2 makes the file human-readable
    
    # Print some information about what we did
    print(f"Generated distance and time matrix for {len(locations_data)} locations")
    print(f"Saved to {output_file}")
    
    return matrix

def load_distance_matrix(filename="distance_matrix.json", locations_data=None):
    """
    Load the distance and time matrix from a file, or generate it if the file doesn't exist.
    This saves time by using pre-calculated values when possible.
    
    filename: File to load the matrix from
    locations_data: Dictionary of locations with coordinates (needed if generating a new matrix)
    
    Returns: Dictionary with distance and time matrices
    """
    # Check if the matrix file already exists
    if os.path.exists(filename):
        # If it exists, load it from the file
        with open(filename, 'r') as f:
            matrix = json.load(f)
        print(f"Loaded distance and time matrix from {filename}")
        return matrix
    else:
        # If it doesn't exist, generate a new one
        if locations_data is None:
            # We need the locations data to generate a new matrix
            raise ValueError("Locations data must be provided to generate matrix")
        return generate_distance_matrix(locations_data, filename)

def get_distance(source, destination, matrix=None, locations_data=None):
    """
    Get the distance between two locations.
    This function checks our pre-calculated matrix first for efficiency.
    
    source: Source location ID
    destination: Destination location ID
    matrix: Distance matrix (if provided, otherwise will load from file)
    locations_data: Dictionary of locations (needed if recalculating)
    
    Returns: Distance in kilometers
    """
    # If no matrix was provided, load it
    if matrix is None:
        matrix = load_distance_matrix("distance_matrix.json", locations_data)
    
    # Try to get distance from the matrix
    try:
        return matrix["distances"][source][destination]
    except KeyError:
        # If the location wasn't in our matrix, calculate it directly
        # This might happen if we added new locations after creating the matrix
        if locations_data is None:
            raise ValueError("Locations data required to calculate distance")
        
        # Get the coordinates
        source_coords = locations_data[source]
        dest_coords = locations_data[destination]
        # Calculate the distance directly
        return calculate_distance(
            source_coords["lat"], source_coords["lng"],
            dest_coords["lat"], dest_coords["lng"]
        )

def get_travel_time(source, destination, matrix=None, locations_data=None):
    """
    Get the travel time between two locations.
    This function checks our pre-calculated matrix first for efficiency.
    
    source: Source location ID
    destination: Destination location ID
    matrix: Time matrix (if provided, otherwise will load from file)
    locations_data: Dictionary of locations (needed if recalculating)
    
    Returns: Travel time in minutes
    """
    # If no matrix was provided, load it
    if matrix is None:
        matrix = load_distance_matrix("distance_matrix.json", locations_data)
    
    # Try to get time from the matrix
    try:
        return matrix["times"][source][destination]
    except KeyError:
        # If the location wasn't in our matrix, calculate it directly
        if locations_data is None:
            raise ValueError("Locations data required to calculate travel time")
        
        # Get the coordinates
        source_coords = locations_data[source]
        dest_coords = locations_data[destination]
        # Calculate the distance
        distance = calculate_distance(
            source_coords["lat"], source_coords["lng"],
            dest_coords["lat"], dest_coords["lng"]
        )
        # Determine road type
        road_type = classify_road_type(source, destination, locations_data)
        # Estimate the travel time
        return estimate_travel_time(distance, road_type)