"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Route waypoints module for identifying intermediate locations along a route.
This file helps identify which known locations a route passes through or near.
"""

import geopy.distance
import numpy as np

def find_intermediate_locations(route_coordinates, all_locations, source_id=None, destination_id=None, threshold_km=0.5):
    """
    Finds known locations that are along or near a route path.
    
    When we calculate a route, we get a series of coordinates. This function
    figures out which known places (towns, landmarks, etc.) the route passes
    through or near, so we can tell the user something like "Your route goes
    through Halfway Tree and Cross Roads."
    
    Args:
        route_coordinates: List of [lat, lng] pairs that define the route
        all_locations: Dictionary of all known locations and their coordinates
        source_id: ID of the starting location
        destination_id: ID of the ending location
        threshold_km: How close a location needs to be to the route to be included (in km)
        
    Returns:
        A list of location names along the route, in order from start to finish
    """
    # Make sure we have a valid route
    if not route_coordinates or len(route_coordinates) < 2:
        return []
    
    # Get the names of the start and end points if provided
    source_name = None
    destination_name = None
    
    if source_id and source_id in all_locations:
        source_name = all_locations[source_id].get("display_name", source_id)
    
    if destination_id and destination_id in all_locations:
        destination_name = all_locations[destination_id].get("display_name", destination_id)
    
    # Calculate the total route distance to track progress
    total_route_distance = 0
    for i in range(len(route_coordinates) - 1):
        point1 = (route_coordinates[i][0], route_coordinates[i][1])
        point2 = (route_coordinates[i+1][0], route_coordinates[i+1][1])
        segment_distance = geopy.distance.geodesic(point1, point2).kilometers
        total_route_distance += segment_distance
    
    # Find locations that are close to any part of the route
    waypoints = []
    
    # For each known location, check if it's near the route
    for loc_id, loc_data in all_locations.items():
        loc_lat = loc_data["lat"]
        loc_lng = loc_data["lng"]
        loc_point = (loc_lat, loc_lng)
        
        min_distance = float('inf')  # Start with infinity
        progress = 0.0  # Track progress along the route (0 to 1)
        current_distance = 0.0
        
        # Check each segment of the route
        for i in range(len(route_coordinates) - 1):
            segment_start = (route_coordinates[i][0], route_coordinates[i][1])
            segment_end = (route_coordinates[i+1][0], route_coordinates[i+1][1])
            
            # Calculate the length of this segment
            segment_distance = geopy.distance.geodesic(segment_start, segment_end).kilometers
            
            # Calculate how far this location is from this segment
            distance_to_segment = point_to_line_distance(loc_point, segment_start, segment_end)
            
            # Update the minimum distance if this is closer
            if distance_to_segment < min_distance:
                min_distance = distance_to_segment
                # Calculate how far along the route this point is (as a percentage)
                progress = (current_distance + find_closest_point_progress(loc_point, segment_start, segment_end) * segment_distance) / total_route_distance
            
            current_distance += segment_distance
        
        # If the location is close enough to the route, add it as a waypoint
        if min_distance <= threshold_km:
            waypoints.append({
                "id": loc_id,
                "name": loc_data.get("display_name", loc_id),
                "distance": min_distance,
                "progress": progress  # How far along the route (0 = start, 1 = end)
            })
    
    # Sort waypoints by their position along the route (from start to finish)
    waypoints.sort(key=lambda x: x["progress"])
    
    # Extract just the location names
    waypoint_names = [wp["name"] for wp in waypoints]
    
    # Create the final list of waypoints, ensuring start and end are correct
    final_waypoints = []
    
    # Add source as first point if provided
    if source_name:
        final_waypoints.append(source_name)
    elif waypoint_names:
        # If no source_name provided, use first waypoint
        final_waypoints.append(waypoint_names[0])
    
    # Add intermediate points (excluding start and end)
    for name in waypoint_names:
        # Skip if it's identical to source or destination
        if (source_name and name == source_name) or (destination_name and name == destination_name):
            continue
            
        # Only add if not already in the list (avoid duplicates)
        if name not in final_waypoints:
            final_waypoints.append(name)
    
    # Ensure destination is the last point
    if destination_name and (not final_waypoints or final_waypoints[-1] != destination_name):
        # Remove destination if it appears earlier in the list
        if destination_name in final_waypoints:
            final_waypoints.remove(destination_name)
        # Add destination at the end
        final_waypoints.append(destination_name)
    
    return final_waypoints

def point_to_line_distance(point, line_start, line_end):
    """
    Calculates the shortest distance from a point to a line segment.
    
    This helps determine how close a location is to a segment of the route.
    All inputs are (lat, lng) tuples.
    
    Returns the distance in kilometers
    """
    # Convert to numpy arrays for vector calculations
    p = np.array([point[0], point[1]])
    v = np.array([line_start[0], line_start[1]])
    w = np.array([line_end[0], line_end[1]])
    
    # Calculate the line segment vector
    segment = w - v
    segment_length_squared = np.sum(segment * segment)
    
    # Handle zero-length segment (if start and end are the same)
    if segment_length_squared == 0:
        return geopy.distance.geodesic(point, line_start).kilometers
    
    # Project the point onto the line segment
    # This gives us the closest point on the line
    t = max(0, min(1, np.sum((p - v) * segment) / segment_length_squared))
    projection = v + t * segment
    
    # Calculate the distance from the point to the projection
    return geopy.distance.geodesic(point, (projection[0], projection[1])).kilometers

def find_closest_point_progress(point, segment_start, segment_end):
    """
    Finds how far along a segment the closest point to a given point is.
    
    Returns a value from 0 to 1, where:
    - 0 means the closest point is at the start of the segment
    - 1 means the closest point is at the end of the segment
    - 0.5 means the closest point is halfway along the segment
    """
    # Convert to numpy arrays
    p = np.array([point[0], point[1]])
    v = np.array([segment_start[0], segment_start[1]])
    w = np.array([segment_end[0], segment_end[1]])
    
    # Calculate the line segment vector
    segment = w - v
    segment_length_squared = np.sum(segment * segment)
    
    # Handle zero-length segment
    if segment_length_squared == 0:
        return 0
    
    # Calculate the projection value (t)
    t = max(0, min(1, np.sum((p - v) * segment) / segment_length_squared))
    return t