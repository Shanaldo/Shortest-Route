"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
OpenRouteService adapter for Jamaica Route Finder.
This file helps us connect to the OpenRouteService API, which is a professional
routing service that we use to validate our own routing algorithms.
"""

import requests
import polyline
import json
import time
import os
from geopy.distance import geodesic
from route_waypoints import find_intermediate_locations

class ORSAdapter:
    """
    This class acts as a bridge between our application and the OpenRouteService API.
    
    OpenRouteService (ORS) is a professional routing service that can calculate routes
    on real road networks. We use it both to visualize our own algorithm's results
    and to compare our routes with a professional solution.
    """
    
    def __init__(self, api_key=None):
        """
        Sets up the adapter with an API key for OpenRouteService.
        
        The API key is required to access the ORS services. We can either provide
        one directly or use one from environment variables.
        """
        # Use provided API key or get from environment variable
        self.api_key = api_key or os.getenv("ORS_API_KEY", "5b3ce3597851110001cf624897760630eca14a6787b79ad182ad9267")
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    def format_coordinates_for_ors(self, coordinates):
        """
        Formats coordinates for the ORS API.
        
        ORS expects coordinates in [longitude, latitude] format, whereas our
        application uses [latitude, longitude], so we need to swap them.
        """
        # Swap lat/lng to lng/lat for ORS API
        return [[coord[1], coord[0]] for coord in coordinates]
    
    def get_route_for_visualization(self, route_points, preference="fastest", avoid_options=None):
        """
        Gets a route from ORS API based on our algorithm's waypoints.
        
        This forces ORS to follow exactly the path calculated by our algorithm,
        which allows us to visualize our route on a real map using ORS data.
        """
        try:
            # Convert our path points to ORS format [lng, lat]
            ors_coordinates = self.format_coordinates_for_ors(route_points)
            
            # Ensure we have the exact start and end points
            start_point = ors_coordinates[0]
            end_point = ors_coordinates[-1]
            
            # If we have too many points, select a subset
            # ORS has limits on how many waypoints we can include
            if len(ors_coordinates) > 25:
                # Always include start point
                sampled_points = [start_point]
                
                # Sample intermediate points (up to 23 more points)
                # We want to keep critical waypoints like towns/cities
                step = max(1, (len(ors_coordinates) - 2) // 23)
                
                for i in range(1, len(ors_coordinates) - 1, step):
                    sampled_points.append(ors_coordinates[i])
                
                # Make sure we don't exceed 24 intermediate points
                if len(sampled_points) > 24:
                    # Keep a more even distribution
                    reduced_points = [sampled_points[0]]  # Keep start
                    reduced_step = len(sampled_points) // 23
                    for i in range(reduced_step, len(sampled_points) - 1, reduced_step):
                        reduced_points.append(sampled_points[i])
                    sampled_points = reduced_points
                
                # Always include end point
                sampled_points.append(end_point)
                ors_coordinates = sampled_points
            
            # Set up request parameters
            # CRITICAL: 'continue_straight'=true forces ORS to follow our waypoints exactly
            params = {
                "coordinates": ors_coordinates,
                "preference": preference,  # 'fastest' or 'shortest'
                "format": "json",
                "instructions": "true",
                "continue_straight": "true",  # Force following waypoints exactly
                "radiuses": [-1] * len(ors_coordinates)  # Use exact waypoints
            }
            
            # Add avoidance options if specified
            avoid_features = []
            if avoid_options:
                if avoid_options.get("tolls", False):
                    avoid_features.append("toll")
                if avoid_options.get("highways", False):
                    avoid_features.append("highways")
                
                if avoid_features:
                    params["options"] = {"avoid_features": avoid_features}
            
            # Make the API request
            response = requests.post(self.base_url, json=params, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the response
            route_data = response.json()
            
            if "routes" in route_data and route_data["routes"]:
                route = route_data["routes"][0]
                segment = route["segments"][0]
                
                # Decode route geometry (polyline format)
                decoded_route = polyline.decode(route["geometry"])
                
                # Create result object with route details
                result = {
                    "route": route["geometry"],  # Encoded polyline
                    "distance": f"{segment['distance'] / 1000:.2f} km",
                    "time": f"{segment['duration'] / 60:.2f} minutes",
                    "decoded_route": decoded_route,  # List of [lat, lng] points
                    "exact_coordinates": {
                        "source": route_points[0],
                        "destination": route_points[-1]
                    }
                }
                
                return result
            else:
                return {"error": "No route found from ORS API"}
                
        except Exception as e:
            return {"error": f"ORS API request failed: {str(e)}"}
    
    def get_direct_route(self, source_coords, dest_coords, source_name, dest_name, preference="fastest", avoid_options=None):
        """
        Gets a direct route from source to destination using ORS's native algorithm.
        
        Unlike get_route_for_visualization, this lets ORS calculate its own optimal
        route between the points without forcing it to follow our waypoints.
        We use this to compare ORS routes with our own algorithm's routes.
        """
        try:
            # Convert coordinates to ORS format [lng, lat]
            ors_source = [source_coords[1], source_coords[0]]
            ors_dest = [dest_coords[1], dest_coords[0]]
            
            # Set up request parameters - just source and destination
            params = {
                "coordinates": [ors_source, ors_dest],  # Just source and destination
                "preference": preference,
                "format": "json",
                "instructions": "true"
            }
            
            # Add avoidance options if specified
            avoid_features = []
            if avoid_options:
                if avoid_options.get("tolls", False):
                    avoid_features.append("toll")
                if avoid_options.get("highways", False):
                    avoid_features.append("highways")
                
                if avoid_features:
                    params["options"] = {"avoid_features": avoid_features}
            
            # Make the API request
            response = requests.post(self.base_url, json=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse the response
            route_data = response.json()
            
            if "routes" in route_data and route_data["routes"]:
                route = route_data["routes"][0]
                segment = route["segments"][0]
                
                # Decode route geometry
                decoded_route = polyline.decode(route["geometry"])
                
                # Create result object with detailed information
                result = {
                    "source": source_name,
                    "destination": dest_name,
                    "route": route["geometry"],  # Encoded polyline
                    "distance": f"{segment['distance'] / 1000:.2f} km",
                    "time": f"{segment['duration'] / 60:.2f} minutes",
                    "preference": preference,
                    "exact_coordinates": {
                        "source": source_coords,
                        "destination": dest_coords
                    }
                }
                
                # Extract route details from step instructions
                detailed_route = [source_name]
                
                # Extract any waypoints or significant locations from instructions
                for step in segment.get("steps", []):
                    if "name" in step and step["name"] and step["name"] not in detailed_route:
                        detailed_route.append(step["name"])
                
                # Make sure destination is the last point
                if dest_name not in detailed_route:
                    detailed_route.append(dest_name)
                elif detailed_route[-1] != dest_name:
                    # Remove destination if it appears earlier and add it at the end
                    detailed_route.remove(dest_name)
                    detailed_route.append(dest_name)
                
                result["detailed_route"] = detailed_route
                
                return result
            else:
                return {"error": "No route found from ORS API"}
                
        except Exception as e:
            return {"error": f"ORS API direct route request failed: {str(e)}"}
    
    def convert_algorithm_path_to_coordinates(self, path, locations):
        """
        Converts a path of location IDs into actual coordinates.
        
        Our algorithm calculates routes as a series of location IDs,
        but for visualization, we need the actual geographic coordinates.
        """
        coordinates = []
        for location_id in path:
            if location_id in locations:
                lat = locations[location_id]["lat"]
                lng = locations[location_id]["lng"]
                coordinates.append([lat, lng])
        return coordinates
    
    def get_route_from_algorithm_result(self, algorithm_result, locations, source_id=None, destination_id=None):
        """
        Converts our algorithm's result into an ORS route for visualization.
        
        This is a convenience function that takes our algorithm's output,
        extracts the path, and gets an ORS route that follows this path
        for visualization on a map.
        """
        if "error" in algorithm_result:
            return {"error": algorithm_result["error"]}
        
        # Convert path to coordinates
        route_points = self.convert_algorithm_path_to_coordinates(
            algorithm_result["path"], locations)
        
        # Find intermediate locations along the route if not already calculated
        if "detailed_route" not in algorithm_result and len(route_points) >= 2:
            intermediate_locations = find_intermediate_locations(
                route_points, locations, source_id, destination_id
            )
            algorithm_result["detailed_route"] = intermediate_locations
        
        # Determine preference based on algorithm
        if "A*" in algorithm_result["algorithm"]:
            preference = "fastest"
        else:
            preference = "shortest"
        
        # Get visualization route
        result = self.get_route_for_visualization(route_points, preference)
        
        # Add detailed route if available
        if "detailed_route" in algorithm_result:
            result["detailed_route"] = algorithm_result["detailed_route"]
        
        return result