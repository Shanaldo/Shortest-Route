"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Route comparison utility for Jamaica Route Finder.
This file helps compare the routes calculated by our algorithms with those from OpenRouteService,
which is a professional routing service.
"""

import time
import json
import geopy.distance
import numpy as np
from tabulate import tabulate
from route_waypoints import find_intermediate_locations

class RouteComparison:
    """
    This class compares routes from different algorithms to see how they perform.
    
    By comparing our custom algorithms with professional routing services,
    we can validate our approach and provide users with confidence in the routes.
    """
    
    def __init__(self, algorithms, ors_adapter):
        """
        Sets up the comparison tool with our algorithms and an ORS adapter.
        
        algorithms: Instance of RouteAlgorithms with our custom algorithms
        ors_adapter: Instance of ORSAdapter to access OpenRouteService
        """
        self.algorithms = algorithms
        self.ors_adapter = ors_adapter
        self.locations = algorithms.locations
    
    def compare_routes(self, source, destination, preference="fastest", avoid_options=None):
        """
        Compares routes from our algorithm and OpenRouteService.
        
        This is the main function that runs both routing methods and compiles
        detailed comparison information for display to the user.
        
        source: Starting location ID
        destination: Ending location ID
        preference: 'fastest' or 'shortest'
        avoid_options: Dictionary of options to avoid (like highways or tolls)
        """
        # Start timing for performance measurement
        start_time = time.time()
        
        # Run our algorithm for the best route
        if preference == "fastest":
            our_result = self.algorithms.find_fastest_route(source, destination, avoid_options)
        else:
            our_result = self.algorithms.find_shortest_route(source, destination, preference, avoid_options)
            
        our_execution_time = (time.time() - start_time) * 1000  # in milliseconds
        
        # Get alternative route that's genuinely different
        # This gives users options if they don't like the primary route
        alt_result = self.find_alternative_route(source, destination, preference, avoid_options)
        
        # Convert algorithm paths to coordinates for visualization
        best_route_points = []
        for loc_id in our_result["path"]:
            if loc_id in self.locations:
                lat = self.locations[loc_id]["lat"]
                lng = self.locations[loc_id]["lng"]
                best_route_points.append([lat, lng])
        
        alt_route_points = []
        for loc_id in alt_result["path"]:
            if loc_id in self.locations:
                lat = self.locations[loc_id]["lat"]
                lng = self.locations[loc_id]["lng"]
                alt_route_points.append([lat, lng])
        
        # Find intermediate locations along both routes
        # This adds names of locations the routes pass through
        if len(best_route_points) >= 2:
            intermediate_locations = find_intermediate_locations(
                best_route_points, 
                self.locations,
                source_id=source,
                destination_id=destination
            )
            our_result["detailed_route"] = intermediate_locations
        
        if len(alt_route_points) >= 2:
            alt_intermediate_locations = find_intermediate_locations(
                alt_route_points, 
                self.locations,
                source_id=source,
                destination_id=destination
            )
            alt_result["detailed_route"] = alt_intermediate_locations
        
        # Get source and destination coordinates and names
        source_coords = [self.locations[source]["lat"], self.locations[source]["lng"]]
        dest_coords = [self.locations[destination]["lat"], self.locations[destination]["lng"]]
        source_name = self.locations[source]["display_name"]
        dest_name = self.locations[destination]["display_name"]
        
        # 1. Get ORS visualization of our algorithm's path (for map display)
        # This follows our exact path but uses ORS data for visualization
        best_ors_visual = self.ors_adapter.get_route_for_visualization(best_route_points, preference, avoid_options)
        alt_ors_visual = self.ors_adapter.get_route_for_visualization(alt_route_points, "shortest" if preference == "fastest" else "fastest", avoid_options)
        
        # 2. Get direct ORS routes using their native algorithm
        # This is what a professional service would calculate
        best_ors_direct = self.ors_adapter.get_direct_route(
            source_coords, 
            dest_coords,
            source_name,
            dest_name,
            preference, 
            avoid_options
        )
        
        alt_ors_direct = self.ors_adapter.get_direct_route(
            source_coords, 
            dest_coords,
            source_name,
            dest_name,
            "shortest" if preference == "fastest" else "fastest", 
            avoid_options
        )
        
        # Add detailed routes to ORS results for visualization
        if "detailed_route" in our_result:
            best_ors_visual["detailed_route"] = our_result["detailed_route"]
        
        if "detailed_route" in alt_result:
            alt_ors_visual["detailed_route"] = alt_result["detailed_route"]
        
        # Calculate comparison metrics for alternative route
        # Shows how much longer/shorter the alternative is
        alt_distance = alt_result.get("distance", 0)
        best_distance = our_result.get("distance", 0)
        alt_time = alt_result.get("time", 0)
        best_time = our_result.get("time", 0)
        
        distance_diff = ((alt_distance - best_distance) / best_distance * 100) if best_distance > 0 else 0
        time_diff = ((alt_time - best_time) / best_time * 100) if best_time > 0 else 0
        
        # Format the response with all the comparison data
        comparison = {
            "our_algorithm": {
                "best_route": {
                    "source": source_name,
                    "destination": dest_name,
                    "route_towns": our_result.get("path_names", []),
                    "detailed_route": our_result.get("detailed_route", []),
                    "distance": f"{our_result.get('distance', 0):.2f} km",
                    "time": f"{our_result.get('time', 0):.2f} minutes",
                    "preference": preference,
                    "algorithm": our_result.get("algorithm", "Unknown"),
                    "execution_time_ms": our_execution_time,
                    "nodes_visited": our_result.get("nodes_visited", 0),
                    "edge_relaxations": our_result.get("edge_relaxations", 0),
                    "operations": our_result.get("operations", 0),
                    "exact_coordinates": {
                        "source": source_coords,
                        "destination": dest_coords
                    }
                },
                "alternative_route": {
                    "source": source_name,
                    "destination": dest_name,
                    "route_towns": alt_result.get("path_names", []),
                    "detailed_route": alt_result.get("detailed_route", []),
                    "distance": f"{alt_result.get('distance', 0):.2f} km",
                    "time": f"{alt_result.get('time', 0):.2f} minutes",
                    "preference": "shortest" if preference == "fastest" else "fastest",
                    "algorithm": alt_result.get("algorithm", "Unknown"),
                    "comparison": {
                        "distance_diff": f"{distance_diff:.1f}%",
                        "time_diff": f"{time_diff:.1f}%"
                    },
                    "exact_coordinates": {
                        "source": source_coords,
                        "destination": dest_coords
                    }
                }
            },
            "openrouteservice": {
                "best_route": best_ors_direct,
                "alternative_route": alt_ors_direct,
                # Include visualization data for map display
                "visualization": {
                    "best_route": best_ors_visual,
                    "alternative_route": alt_ors_visual
                }
            }
        }
        
        return comparison
    
    def find_alternative_route(self, source, destination, original_preference, original_avoid_options=None):
        """
        Finds a genuinely different alternative route that's still reasonably efficient.
        
        Instead of just providing two similar routes, this tries to find a meaningfully
        different route that users might prefer for various reasons.
        """
        # Handle special cases for routes involving Spanish Town
        if source == "spanish_town" or destination == "spanish_town":
            # Determine which end is Spanish Town and which is the other location
            spanish_town_end = "spanish_town"
            other_end = destination if source == "spanish_town" else source
            
            # Generate a reasonable alternative based on the specific route
            return self.generate_spanish_town_alternative(spanish_town_end, other_end, original_preference, original_avoid_options)
        
        # Handle special cases for routes involving Old Harbour
        if source == "old_harbour" or destination == "old_harbour":
            # Determine which end is Old Harbour and which is the other location
            old_harbour_end = "old_harbour"
            other_end = destination if source == "old_harbour" else source
            
            # Generate a reasonable alternative based on the specific route
            return self.generate_old_harbour_alternative(old_harbour_end, other_end, original_preference, original_avoid_options)
        
        # Regular algorithm for non-Spanish Town and non-Old Harbour routes
        
        # Get the original route first
        if original_preference == "fastest":
            original_route = self.algorithms.find_fastest_route(source, destination, original_avoid_options)
        else:
            original_route = self.algorithms.find_shortest_route(source, destination, original_preference, original_avoid_options)
        
        # Get the original path nodes
        original_path = set(original_route["path"])
        
        # Strategy 1: Use opposite preference with modified constraints
        # If the original was fastest, try shortest, and vice versa
        alt_preference = "shortest" if original_preference == "fastest" else "fastest"
        avoid_options = original_avoid_options.copy() if original_avoid_options else {}
        
        # Modify constraints to encourage a different route
        # For example, if original doesn't avoid highways, make alternative avoid them
        if not avoid_options.get("highways", False):
            avoid_options["highways"] = True
        
        # Try the opposite preference with modified constraints
        if alt_preference == "fastest":
            alt_result = self.algorithms.find_fastest_route(source, destination, avoid_options)
        else:
            alt_result = self.algorithms.find_shortest_route(source, destination, alt_preference, avoid_options)
        
        # Check if the paths are different enough
        alt_path = set(alt_result["path"])
        overlap = len(original_path.intersection(alt_path)) / len(original_path) * 100
        
        # If still too similar, try a path through an intermediate point
        if overlap > 60:  # If paths share more than 60% of locations
            # Find a key location that's not on the original path to route through
            waypoint = self.find_suitable_waypoint(source, destination, original_path)
            
            if waypoint:
                # Make sure the waypoint is in a reasonable direction
                source_coords = (self.locations[source]["lat"], self.locations[source]["lng"])
                dest_coords = (self.locations[destination]["lat"], self.locations[destination]["lng"]) 
                waypoint_coords = (self.locations[waypoint]["lat"], self.locations[waypoint]["lng"])
                
                # Check if waypoint is not taking us too far out of the way
                direct_distance = geopy.distance.geodesic(source_coords, dest_coords).kilometers
                via_waypoint_distance = (
                    geopy.distance.geodesic(source_coords, waypoint_coords).kilometers +
                    geopy.distance.geodesic(waypoint_coords, dest_coords).kilometers
                )
                
                # Only use waypoint if the detour is not more than 50% longer than direct route
                if via_waypoint_distance <= direct_distance * 1.5:
                    print(f"Using {waypoint} as intermediate waypoint")
                    # Route through this waypoint
                    # First segment: source to waypoint
                    first_segment = None
                    if alt_preference == "fastest":
                        first_segment = self.algorithms.find_fastest_route(source, waypoint, avoid_options)
                    else:
                        first_segment = self.algorithms.find_shortest_route(source, waypoint, alt_preference, avoid_options)
                    
                    # Second segment: waypoint to destination
                    second_segment = None
                    if alt_preference == "fastest":
                        second_segment = self.algorithms.find_fastest_route(waypoint, destination, avoid_options)
                    else:
                        second_segment = self.algorithms.find_shortest_route(waypoint, destination, alt_preference, avoid_options)
                    
                    # Combine the segments if both succeeded
                    if "error" not in first_segment and "error" not in second_segment:
                        alt_result = self.combine_route_segments(first_segment, second_segment)
        
        return alt_result
    
    def generate_spanish_town_alternative(self, spanish_town_end, other_end, preference, avoid_options=None):
        """
        Generates a sensible alternative route for trips to/from Spanish Town.
        
        Routes involving Spanish Town need special handling because it's a major hub
        with specific road patterns.
        """
        # Define possible intermediate points for different locations
        # These are good waypoints to route through for each destination
        intermediate_points = {
            "halfway_tree": ["cross_roads", "constant_spring", "new_kingston"],
            "new_kingston": ["cross_roads", "liguanea", "halfway_tree"],
            "liguanea": ["papine", "barbican", "hope_zoo"],
            "cross_roads": ["halfway_tree", "new_kingston", "port_royal"],
            "papine": ["liguanea", "mona", "hope_zoo"],
            "university_hospital": ["papine", "mona", "liguanea"],
            "mona": ["papine", "liguanea", "mona_heights"],
            "mona_heights": ["papine", "mona", "hope_zoo"],
            "barbican": ["liguanea", "constant_spring", "manor_park"],
            "constant_spring": ["barbican", "halfway_tree", "manor_park"],
            "manor_park": ["constant_spring", "barbican"],
            "port_royal": ["cross_roads", "new_kin,gston"],
            "old_harbour": ["spanish_town"],
            "hope_zoo": ["papine", "mona", "liguanea"],
        }
        
        # Pick the first available intermediate point for this location
        waypoints = intermediate_points.get(other_end, ["cross_roads"])
        
        # Try each possible waypoint
        for waypoint in waypoints:
            # Determine direction based on which end is Spanish Town
            if spanish_town_end == "spanish_town":
                # Route: other_end -> waypoint -> spanish_town
                first_segment = self.algorithms.find_shortest_route(other_end, waypoint, "distance", avoid_options)
                second_segment = self.algorithms.find_shortest_route(waypoint, "spanish_town", "distance", avoid_options)
            else:
                # Route: spanish_town -> waypoint -> other_end
                first_segment = self.algorithms.find_shortest_route("spanish_town", waypoint, "distance", avoid_options)
                second_segment = self.algorithms.find_shortest_route(waypoint, other_end, "distance", avoid_options)
            
            # Combine the segments if both succeeded
            if "error" not in first_segment and "error" not in second_segment:
                return self.combine_route_segments(first_segment, second_segment)
        
        # If no waypoint works, fall back to opposite preference
        alt_preference = "shortest" if preference == "fastest" else "fastest"
        if alt_preference == "fastest":
            if spanish_town_end == "spanish_town":
                return self.algorithms.find_fastest_route(other_end, "spanish_town", avoid_options)
            else:
                return self.algorithms.find_fastest_route("spanish_town", other_end, avoid_options)
        else:
            if spanish_town_end == "spanish_town":
                return self.algorithms.find_shortest_route(other_end, "spanish_town", alt_preference, avoid_options)
            else:
                return self.algorithms.find_shortest_route("spanish_town", other_end, alt_preference, avoid_options)
    
    
    def generate_old_harbour_alternative(self, old_harbour_end, other_end, preference, avoid_options=None):
        """
        Generates a sensible alternative route for trips to/from Old Harbour.
        
        Routes involving Old Harbour need special handling because it's a key location
        with specific road patterns and limited direct connections.
        """
        # Define possible intermediate points for different locations
        # These are good waypoints to route through for each destination
        intermediate_points = {
            "halfway_tree": ["cross_roads", "constant_spring", "new_kingston"],
            "new_kingston": ["cross_roads", "liguanea", "halfway_tree"],
            "liguanea": ["papine", "barbican", "hope_zoo"],
            "cross_roads": ["halfway_tree", "new_kingston", "port_royal"],
            "papine": ["liguanea", "mona", "hope_zoo"],
            "university_hospital": ["papine", "mona", "liguanea"],
            "mona": ["papine", "liguanea", "mona_heights"],
            "mona_heights": ["papine", "mona", "hope_zoo"],
            "barbican": ["liguanea", "constant_spring", "manor_park"],
            "constant_spring": ["barbican", "halfway_tree", "manor_park"],
            "manor_park": ["constant_spring", "barbican"],
            "port_royal": ["cross_roads", "new_kingston"],
            "old_harbour": ["spanish_town"]
        }
        
        # Pick the first available intermediate point for this location
        waypoints = intermediate_points.get(other_end, ["halfway_tree"])
        
        # Try each possible waypoint
        for waypoint in waypoints:
            # Determine direction based on which end is Old Harbour
            if old_harbour_end == "old_harbour":
                # Route: other_end -> waypoint -> old_harbour
                first_segment = self.algorithms.find_shortest_route(other_end, waypoint, "distance", avoid_options)
                second_segment = self.algorithms.find_shortest_route(waypoint, "old_harbour", "distance", avoid_options)
            else:
                # Route: old_harbour -> waypoint -> other_end
                first_segment = self.algorithms.find_shortest_route("old_harbour", waypoint, "distance", avoid_options)
                second_segment = self.algorithms.find_shortest_route(waypoint, other_end, "distance", avoid_options)
            
            # Combine the segments if both succeeded
            if "error" not in first_segment and "error" not in second_segment:
                return self.combine_route_segments(first_segment, second_segment)
        
        # If no waypoint works, fall back to opposite preference
        alt_preference = "shortest" if preference == "fastest" else "fastest"
        if alt_preference == "fastest":
            if old_harbour_end == "old_harbour":
                return self.algorithms.find_fastest_route(other_end, "old_harbour", avoid_options)
            else:
                return self.algorithms.find_fastest_route("old_harbour", other_end, avoid_options)
        else:
            if old_harbour_end == "old_harbour":
                return self.algorithms.find_shortest_route(other_end, "old_harbour", alt_preference, avoid_options)
            else:
                return self.algorithms.find_shortest_route("old_harbour", other_end, alt_preference, avoid_options)

    
    def find_suitable_waypoint(self, source, destination, original_path):
        """
        Finds a location that's not on the original path but makes a reasonable detour.
        
        This helps us create alternate routes that pass through different areas
        while still being reasonably efficient.
        """
        # Convert to set for quicker lookups
        original_path_set = set(original_path)
        
        # Get source and destination coordinates
        source_coords = (self.locations[source]["lat"], self.locations[source]["lng"])
        dest_coords = (self.locations[destination]["lat"], self.locations[destination]["lng"])
        
        # Calculate the direct distance from source to destination
        direct_distance = geopy.distance.geodesic(source_coords, dest_coords).kilometers
        
        # Find a location that's not on the path but still a reasonable detour
        candidates = []
        
        for loc_id, loc_data in self.locations.items():
            # Skip if it's the source, destination, or on the original path
            if loc_id == source or loc_id == destination or loc_id in original_path_set:
                continue
            
            # Special case: for Halfway Tree to Spanish Town, let's blacklist New Kingston
            if ((source == "halfway_tree" and destination == "spanish_town") or 
                (source == "spanish_town" and destination == "halfway_tree")) and loc_id == "new_kingston":
                continue
                
            # Get coordinates
            loc_coords = (loc_data["lat"], loc_data["lng"])
            
            # Calculate distances
            distance_from_source = geopy.distance.geodesic(source_coords, loc_coords).kilometers
            distance_from_dest = geopy.distance.geodesic(loc_coords, dest_coords).kilometers
            
            # Skip if too close to source or destination
            # (No point in having a waypoint right next to start or end)
            if distance_from_source < 1.0 or distance_from_dest < 1.0:
                continue
            
            # Calculate how far off the direct path this point is
            detour_distance = distance_from_source + distance_from_dest
            detour_factor = detour_distance / direct_distance if direct_distance > 0 else float('inf')
            
            # Distance from straight line between source and destination
            perpendicular_distance = self.point_to_line_distance(
                loc_coords, source_coords, dest_coords
            )
            
            # Consider points that aren't too far off the direct path
            # but are still different enough to create an alternative route
            if detour_factor < 1.4 and perpendicular_distance < 10:
                candidates.append((loc_id, perpendicular_distance, detour_factor))
        
        # Sort by a balance of perpendicular distance and detour factor
        # We want points that are different enough but not creating huge detours
        candidates.sort(key=lambda x: x[1] * 0.5 + x[2] * 5)
        
        # Return the best candidate, if any
        if candidates:
            return candidates[0][0]
        
        # If no suitable waypoint found, return None
        return None
    
    def find_all_suitable_waypoints(self, source, destination, original_path, max_count=3):
        """
        Finds multiple locations that are not on the original path and make reasonable detours.
        Returns up to max_count waypoints sorted by suitability.
        
        This extends find_suitable_waypoint to return multiple options.
        """
        # Convert to set for quicker lookups
        original_path_set = set(original_path)
        
        # Get source and destination coordinates
        source_coords = (self.locations[source]["lat"], self.locations[source]["lng"])
        dest_coords = (self.locations[destination]["lat"], self.locations[destination]["lng"])
        
        # Calculate the direct heading from source to destination
        direct_distance = geopy.distance.geodesic(source_coords, dest_coords).kilometers
        
        # Find locations that are not on the path but still reasonable detours
        candidates = []
        
        for loc_id, loc_data in self.locations.items():
            # Skip if it's the source, destination, or on the original path
            if loc_id == source or loc_id == destination or loc_id in original_path_set:
                continue
            
            # Special case: for Halfway Tree to Spanish Town, let's blacklist New Kingston
            if (source == "halfway_tree" and destination == "spanish_town" or 
                source == "spanish_town" and destination == "halfway_tree") and loc_id == "new_kingston":
                continue
                
            # Get coordinates
            loc_coords = (loc_data["lat"], loc_data["lng"])
            
            # Calculate distances
            distance_from_source = geopy.distance.geodesic(source_coords, loc_coords).kilometers
            distance_from_dest = geopy.distance.geodesic(loc_coords, dest_coords).kilometers
            
            # Skip if too close to source or destination
            if distance_from_source < 1.0 or distance_from_dest < 1.0:
                continue
            
            # Calculate how far off the direct path this point is
            detour_distance = distance_from_source + distance_from_dest
            detour_factor = detour_distance / direct_distance if direct_distance > 0 else float('inf')
            
            # Distance from straight line between source and destination
            perpendicular_distance = self.point_to_line_distance(
                loc_coords, source_coords, dest_coords
            )
            
            # Consider points that aren't too far off the direct path
            # but are still different enough to create an alternative route
            if detour_factor < 1.4 and perpendicular_distance < 10:
                candidates.append((loc_id, perpendicular_distance, detour_factor))
        
        # Sort by a balance of perpendicular distance and detour factor
        # We want points that are different enough but not creating huge detours
        candidates.sort(key=lambda x: x[1] * 0.5 + x[2] * 5)
        
        # Return the top candidates
        return [c[0] for c in candidates[:max_count]]
    
    def combine_route_segments(self, first_segment, second_segment):
        """
        Combines two route segments into a single route.
        
        This is used when creating routes that go through intermediate waypoints.
        It joins the routes together and calculates the combined statistics.
        """
        # Path: concatenate paths but remove duplicate middle point
        combined_path = first_segment["path"][:-1] + second_segment["path"]
        
        # Path names: same approach
        combined_path_names = first_segment["path_names"][:-1] + second_segment["path_names"]
        
        # Distance and time: add them up
        combined_distance = first_segment["distance"] + second_segment["distance"]
        combined_time = first_segment["time"] + second_segment["time"]
        
        # Use the algorithm name from the first segment
        algorithm = first_segment["algorithm"]
        algorithm_description = first_segment["algorithm_description"]
        
        # Sum up the metrics
        nodes_visited = first_segment["nodes_visited"] + second_segment["nodes_visited"]
        edge_relaxations = first_segment["edge_relaxations"] + second_segment["edge_relaxations"]
        operations = first_segment["operations"] + second_segment["operations"]
        
        # Create the combined result
        combined_result = {
            "path": combined_path,
            "path_names": combined_path_names,
            "distance": combined_distance,
            "time": combined_time,
            "algorithm": algorithm,
            "algorithm_description": algorithm_description,
            "nodes_visited": nodes_visited,
            "edge_relaxations": edge_relaxations,
            "operations": operations
        }
        
        return combined_result
    
    def point_to_line_distance(self, point, line_start, line_end):
        """
        Calculates the distance from a point to a line defined by two points.
        
        This geometric calculation helps determine how far a location is from
        the straight-line path between source and destination.
        """
        from numpy import array, sum, sqrt
        
        # Convert to arrays for vector calculations
        point = array([point[0], point[1]])
        line_start = array([line_start[0], line_start[1]])
        line_end = array([line_end[0], line_end[1]])
        
        # Line vector (from start to end)
        line_vec = line_end - line_start
        
        # Vector from line start to point
        point_vec = point - line_start
        
        # Calculate projection
        line_len = sum(line_vec * line_vec)
        if line_len == 0:  # Line is actually a point
            return geopy.distance.geodesic(point, line_start).kilometers
        
        # Calculate projection distance along line
        # This is the position along the line closest to our point
        proj = sum(point_vec * line_vec) / line_len
        
        # Clip projection to line segment
        if proj < 0:
            closest = line_start
        elif proj > 1:
            closest = line_end
        else:
            closest = line_start + proj * line_vec
        
        # Convert back to geographic coordinates and calculate distance
        closest_coords = (closest[0], closest[1])
        point_coords = (point[0], point[1])
        
        return geopy.distance.geodesic(point_coords, closest_coords).kilometers