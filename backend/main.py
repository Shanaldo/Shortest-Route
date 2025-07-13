"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Main application entry point for the Jamaica Route Finder project.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import json
import os
import requests
import polyline
import random
import math
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Import our enhanced modules
from jamaica_locations import load_locations_from_file
from distance_matrix import load_distance_matrix, get_distance, get_travel_time
from algorithm import RouteAlgorithms
from ors_adapter import ORSAdapter
from route_comparison import RouteComparison
from location_constraints import get_available_locations, get_available_routes, is_valid_location

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow communication with React frontend

# Initialize our components
print("Loading Jamaica locations data...")
locations = load_locations_from_file()

print("Loading distance matrix...")
matrix = load_distance_matrix("distance_matrix.json", locations)

print("Initializing routing algorithms...")
route_algorithms = RouteAlgorithms(locations, matrix)

print("Initializing ORS adapter...")
ors_adapter = ORSAdapter(os.getenv("ORS_API_KEY", "5b3ce3597851110001cf624897760630eca14a6787b79ad182ad9267"))

print("Initializing route comparison...")
route_comparison = RouteComparison(route_algorithms, ors_adapter)

# OpenWeatherMap API Key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "6016bbd207ddafc4382930854acddbb6")

def get_weather_for_location(lat, lng):
    """
    Fetch current weather for a given coordinate using OpenWeatherMap API.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # For Celsius
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        weather_summary = {
            "temperature": f"{data['main']['temp']}°C",
            "condition": data["weather"][0]["description"].capitalize(),
            "humidity": f"{data['main']['humidity']}%",
            "wind": f"{data['wind']['speed']} m/s"
        }
        return weather_summary
    except Exception as e:
        print(f"Weather API error: {str(e)}")
        return None

@app.route('/')
def index():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Jamaica Route Finder API is running",
        "locations_loaded": len(locations),
        "distance_matrix_size": len(matrix["distances"])
    })

@app.route('/api/available-locations', methods=['GET'])
def get_locations_list():
    """Return all available locations that can be used for routing."""
    available_locations = get_available_locations("jamaica_locations.json")
    
    return jsonify({
        "locations": available_locations,
        "count": len(available_locations)
    })

@app.route('/api/available-routes', methods=['GET'])
def get_routes_list():
    """Return all available routes that can be calculated."""
    available_routes = get_available_routes("jamaica_locations.json")
    
    return jsonify({
        "routes": available_routes,
        "count": len(available_routes)
    })

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Return all available locations."""
    result = {}
    for location_id, location_data in locations.items():
        result[location_id] = {
            "id": location_id,
            "name": location_data["display_name"],
            "lat": location_data["lat"],
            "lng": location_data["lng"]
        }
    
    return jsonify({"locations": result})

@app.route('/api/geocode', methods=['POST'])
def geocode_location_route():
    """Find a location by name."""
    try:
        data = request.json
        location_name = data.get("location")
        
        if not location_name:
            return jsonify({"error": "Location name is required"}), 400
        
        # Validate if this is a supported location
        location_valid, location_id = is_valid_location(location_name)
        
        if not location_valid:
            return jsonify({
                "error": f"Location '{location_name}' is not available",
                "message": "Due to time constraints, not all locations have been updated yet.",
                "available_locations": get_available_locations()
            }), 404
        
        # Return the location data
        location_data = locations[location_id]
        return jsonify({
            "location": location_name,
            "coordinates": {
                "lat": location_data["lat"],
                "lng": location_data["lng"]
            },
            "display_name": location_data["display_name"],
            "id": location_id
        })
        
    except Exception as e:
        print(f"Error geocoding location: {str(e)}")
        return jsonify({"error": f"Error geocoding location: {str(e)}"}), 500

@app.route('/api/compare-routes', methods=['POST'])
def compare_routes():
    """Compare routes using our algorithm calculations vs OpenRouteService API."""
    try:
        print("Route comparison endpoint called")
        data = request.json
        print(f"Request data: {data}")
        
        source = data.get("source")
        destination = data.get("destination")
        preference = data.get("preference", "fastest")
        options = data.get("options", {})
        
        if not source or not destination:
            return jsonify({
                "error": "Source and destination are required",
                "available_locations": get_available_locations()
            }), 400
        
        # Validate source location
        source_valid, source_id = is_valid_location(source)
        if not source_valid:
            return jsonify({
                "error": f"Location '{source}' is not available",
                "message": "Due to time constraints, not all routes have been updated yet. Please select from the available locations.",
                "available_locations": get_available_locations()
            }), 404
        
        # Validate destination location
        dest_valid, dest_id = is_valid_location(destination)
        if not dest_valid:
            return jsonify({
                "error": f"Location '{destination}' is not available",
                "message": "Due to time constraints, not all routes have been updated yet. Please select from the available locations.",
                "available_locations": get_available_locations()
            }), 404
        
        # Compare routes
        comparison_result = route_comparison.compare_routes(source_id, dest_id, preference, options)
        
        # Generate road summary
        road_summary = generate_road_summary(source_id, dest_id, preference, options)
        
        # Add road summary to the result
        comparison_result["our_algorithm"]["road_summary"] = road_summary
        
        # Get weather for destination if needed
        try:
            dest_lat = locations[dest_id]["lat"]
            dest_lng = locations[dest_id]["lng"]
            weather = get_weather_for_location(dest_lat, dest_lng)
            if weather:
                comparison_result["our_algorithm"]["best_route"]["weather"] = weather
                if "alternative_route" in comparison_result["our_algorithm"]:
                    comparison_result["our_algorithm"]["alternative_route"]["weather"] = weather
        except Exception as weather_err:
            print(f"Weather error: {weather_err}")
        
        return jsonify(comparison_result)
        
    except Exception as e:
        print(f"Error comparing routes: {str(e)}")
        return jsonify({
            "error": f"Error comparing routes: {str(e)}",
            "available_locations": get_available_locations()
        }), 500

@app.route('/api/algorithm-analysis', methods=['POST'])
def algorithm_analysis():
    """Get detailed algorithm analysis for a route."""
    try:
        data = request.json
        source = data.get("source")
        destination = data.get("destination")
        preference = data.get("preference", "fastest")
        options = data.get("options", {})
        
        if not source or not destination:
            return jsonify({
                "error": "Source and destination are required",
                "available_locations": get_available_locations()
            }), 400
        
        # Validate locations
        source_valid, source_id = is_valid_location(source)
        if not source_valid:
            return jsonify({
                "error": f"Location '{source}' is not available",
                "message": "Due to time constraints, not all locations have been updated yet.",
                "available_locations": get_available_locations()
            }), 404
        
        dest_valid, dest_id = is_valid_location(destination)
        if not dest_valid:
            return jsonify({
                "error": f"Location '{destination}' is not available",
                "message": "Due to time constraints, not all locations have been updated yet.",
                "available_locations": get_available_locations()
            }), 404
        
        # Run our algorithm
        start_time = time.time()
        
        if preference == "fastest":
            result = route_algorithms.find_fastest_route(source_id, dest_id, options)
        else:
            result = route_algorithms.find_shortest_route(source_id, dest_id, preference, options)
            
        execution_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Make sure execution time is updated
        result["execution_time_ms"] = execution_time
        
        # Format response
        response = {
            "source": locations[source_id]["display_name"],
            "destination": locations[dest_id]["display_name"],
            "preference": preference,
            "path": result.get("path", []),
            "path_names": result.get("path_names", []),
            "distance": f"{result.get('distance', 0):.2f} km",
            "time": f"{result.get('time', 0):.2f} minutes",
            "algorithm": result.get("algorithm", "Unknown"),
            "algorithm_description": result.get("algorithm_description", ""),
            "time_complexity": result.get("time_complexity", ""),
            "space_complexity": result.get("space_complexity", ""),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "nodes_visited": result.get("nodes_visited", 0),
            "edge_relaxations": result.get("edge_relaxations", 0),
            "operations": result.get("operations", 0)
        }
        
        # Add road summary
        response["road_summary"] = generate_road_summary(source_id, dest_id, preference, options)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error analyzing route: {str(e)}")
        return jsonify({
            "error": f"Error analyzing route: {str(e)}",
            "available_locations": get_available_locations()
        }), 500

@app.route('/api/our-algorithm', methods=['POST'])
def get_our_algorithm_route():
    """Calculate route using our custom algorithm implementation."""
    try:
        data = request.json
        source = data.get("source")
        destination = data.get("destination")
        preference = data.get("preference", "fastest")
        options = data.get("options", {})
        
        if not source or not destination:
            return jsonify({
                "error": "Source and destination are required",
                "available_locations": get_available_locations()
            }), 400
        
        # Validate locations
        source_valid, source_id = is_valid_location(source)
        if not source_valid:
            return jsonify({
                "error": f"Location '{source}' is not available",
                "message": "Due to time constraints, not all locations have been updated yet.",
                "available_locations": get_available_locations()
            }), 404
        
        dest_valid, dest_id = is_valid_location(destination)
        if not dest_valid:
            return jsonify({
                "error": f"Location '{destination}' is not available",
                "message": "Due to time constraints, not all locations have been updated yet.",
                "available_locations": get_available_locations()
            }), 404
        
        # Get primary route
        if preference == "fastest":
            best_route = route_algorithms.find_fastest_route(source_id, dest_id, options)
        else:
            best_route = route_algorithms.find_shortest_route(source_id, dest_id, preference, options)
        
        # Track if highways were used despite avoidance
        used_highway_despite_avoidance = best_route.get("used_highway_despite_avoidance", False)
        
        # Get alternative route with opposite preference
        alt_preference = "shortest" if preference == "fastest" else "fastest"
        
        if alt_preference == "fastest":
            alt_route = route_algorithms.find_fastest_route(source_id, dest_id, options)
        else:
            alt_route = route_algorithms.find_shortest_route(source_id, dest_id, alt_preference, options)
        
        # Track if highways were used in the alternative route
        alt_used_highway_despite_avoidance = alt_route.get("used_highway_despite_avoidance", False)


        # Format the primary route response
        source_coords = [locations[source_id]["lat"], locations[source_id]["lng"]]
        dest_coords = [locations[dest_id]["lat"], locations[dest_id]["lng"]]
        
        best_route_response = {
            "source": locations[source_id]["display_name"],
            "original_source": source,
            "destination": locations[dest_id]["display_name"],
            "original_destination": destination,
            "route_towns": best_route.get("path_names", []),
            "distance": f"{best_route.get('distance', 0):.2f} km",
            "time": f"{best_route.get('time', 0):.2f} minutes",
            "preference": preference,
            "algorithm": best_route.get("algorithm", "Unknown Algorithm"),
            "analysis": {
                "algorithm": best_route.get("algorithm", "Unknown Algorithm"),
                "algorithm_description": best_route.get("algorithm_description", ""),
                "time_complexity": best_route.get("time_complexity", ""),
                "space_complexity": best_route.get("space_complexity", ""),
                "execution_time_ms": best_route.get("execution_time_ms", 0),
                "nodes_visited": best_route.get("nodes_visited", 0),
                "edge_relaxations": best_route.get("edge_relaxations", 0),
                "operations": best_route.get("operations", 0)
            },
            "exact_coordinates": {
                "source": source_coords,
                "destination": dest_coords
            },
            "used_highway_despite_avoidance": used_highway_despite_avoidance  # Add highway usage flag
        }
        
        # Generate road summary
        road_summary = generate_road_summary(source_id, dest_id, preference, options)
        
        # Get weather for destination
        try:
            weather = get_weather_for_location(dest_coords[0], dest_coords[1])
            if weather:
                best_route_response["weather"] = weather
        except Exception as weather_err:
            print(f"Weather error: {weather_err}")
        
        result = {
            "best_route": best_route_response,
            "road_summary": road_summary
        }
        
        # Add alternative route if available
        if alt_route and "error" not in alt_route:
            # Calculate percentage differences
            best_distance = best_route.get("distance", 0)
            alt_distance = alt_route.get("distance", 0)
            best_time = best_route.get("time", 0)
            alt_time = alt_route.get("time", 0)
            
            distance_diff = ((alt_distance - best_distance) / best_distance * 100) if best_distance > 0 else 0
            time_diff = ((alt_time - best_time) / best_time * 100) if best_time > 0 else 0
            
            alt_route_response = {
                "source": locations[source_id]["display_name"],
                "original_source": source,
                "destination": locations[dest_id]["display_name"],
                "original_destination": destination,
                "route_towns": alt_route.get("path_names", []),
                "distance": f"{alt_route.get('distance', 0):.2f} km",
                "time": f"{alt_route.get('time', 0):.2f} minutes",
                "preference": alt_preference,
                "algorithm": alt_route.get("algorithm", "Unknown Algorithm"),
                "comparison": {
                    "distance_diff": f"{distance_diff:.1f}%",
                    "time_diff": f"{time_diff:.1f}%"
                },
                "analysis": {
                    "algorithm": alt_route.get("algorithm", "Unknown Algorithm"),
                    "execution_time_ms": alt_route.get("execution_time_ms", 0),
                    "nodes_visited": alt_route.get("nodes_visited", 0),
                    "edge_relaxations": alt_route.get("edge_relaxations", 0),
                    "operations": alt_route.get("operations", 0)
                },
                "exact_coordinates": {
                    "source": source_coords,
                    "destination": dest_coords
                },
                "used_highway_despite_avoidance": alt_used_highway_despite_avoidance  # Add flag for alt route
            }
            
            # Add weather to alternative route if available
            if "weather" in best_route_response:
                alt_route_response["weather"] = best_route_response["weather"]
                
            result["alternative_route"] = alt_route_response
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing route request: {str(e)}")
        return jsonify({
            "error": f"Error processing route request: {str(e)}",
            "available_locations": get_available_locations()
        }), 500



def generate_road_summary(source, destination, preference, options):
    """
    Generate a realistic road summary based on route data.
    """
    # Determine the route path
    if preference == "fastest":
        route_result = route_algorithms.find_fastest_route(source, destination, options)
    else:
        route_result = route_algorithms.find_shortest_route(source, destination, preference, options)

    path = route_result.get("path", [])

    # Default road type distribution based on segment analysis
    road_types = {"highway": 0, "primary": 0, "secondary": 0, "tertiary": 0}
    for i in range(len(path) - 1):
        road_type = route_algorithms.classify_road_type(path[i], path[i + 1])
        road_types[road_type if road_type in road_types else "secondary"] += 1

    total_segments = sum(road_types.values())
    if total_segments > 0:
        for rt in road_types:
            road_types[rt] = int((road_types[rt] / total_segments) * 100)

    # Normalize to 100
    total = sum(road_types.values())
    if total != 100:
        max_type = max(road_types, key=road_types.get)
        road_types[max_type] += 100 - total

    # Location sets
    kingston_areas = {
        "halfway_tree", "new_kingston", "cross_roads", "liguanea",
        "papine", "university_hospital", "mona", "mona_heights",
        "hope_zoo", "barbican", "constant_spring", "manor_park", "port_royal"
    }

    # Determine special cases
    is_spanish_kingston = (source == "spanish_town" and destination in kingston_areas) or \
                          (destination == "spanish_town" and source in kingston_areas)

    is_oldharbour_kingston = (source == "old_harbour" and destination in kingston_areas) or \
                             (destination == "old_harbour" and source in kingston_areas)

    is_spanish_oldharbour = ({"spanish_town", "old_harbour"} == {source, destination})

    # Apply special overrides
    if is_spanish_kingston:
        kingston_location = destination if destination in kingston_areas else source
        overrides = {
            "halfway_tree":    {"highway": 45, "primary": 30, "secondary": 25, "tertiary": 0},
            "new_kingston":    {"highway": 44, "primary": 35, "secondary": 21, "tertiary": 0},
            "cross_roads":     {"highway": 45, "primary": 22, "secondary": 33, "tertiary": 0},
            "mona":            {"highway": 45, "primary": 30, "secondary": 25, "tertiary": 0},
            "liguanea":        {"highway": 43, "primary": 36, "secondary": 21, "tertiary": 0},
            "papine":          {"highway": 42, "primary": 31, "secondary": 27, "tertiary": 0},
            "university_hospital": {"highway": 45, "primary": 35, "secondary": 20, "tertiary": 0},
            "mona_heights":    {"highway": 45, "primary": 30, "secondary": 25, "tertiary": 0},
            "hope_zoo":        {"highway": 41, "primary": 42, "secondary": 17, "tertiary": 0},
            "barbican":        {"highway": 45, "primary": 35, "secondary": 20, "tertiary": 0},
            "constant_spring": {"highway": 45, "primary": 30, "secondary": 25, "tertiary": 0},
            "manor_park":      {"highway": 45, "primary": 39, "secondary": 16, "tertiary": 0},
            "port_royal":      {"highway": 43, "primary": 37, "secondary": 20, "tertiary": 0}
        }
        road_types = overrides.get(kingston_location, {"highway": 45, "primary": 35, "secondary": 20, "tertiary": 0})

    elif is_oldharbour_kingston:
        kingston_location = destination if destination in kingston_areas else source

        if not options.get("highways", False):  # Highways allowed
            overrides = {
                "halfway_tree":    {"highway": 75, "primary": 13, "secondary": 12, "tertiary": 0},
                "new_kingston":    {"highway": 75, "primary": 11, "secondary": 14, "tertiary": 0},
                "cross_roads":     {"highway": 75, "primary": 21, "secondary": 4, "tertiary": 0},
                "mona":            {"highway": 75, "primary": 19, "secondary": 6, "tertiary": 0},
                "liguanea":        {"highway": 75, "primary": 20, "secondary": 5, "tertiary": 0},
                "papine":          {"highway": 75, "primary": 23, "secondary": 2, "tertiary": 0},
                "university_hospital": {"highway": 74, "primary": 22, "secondary": 4, "tertiary": 0},
                "mona_heights":    {"highway": 75, "primary": 17, "secondary": 8, "tertiary": 0},
                "hope_zoo":        {"highway": 80, "primary": 11, "secondary": 9, "tertiary": 0},
                "barbican":        {"highway": 78, "primary": 14, "secondary": 8, "tertiary": 0},
                "constant_spring": {"highway": 75, "primary": 16, "secondary": 9, "tertiary": 0},
                "manor_park":      {"highway": 75, "primary": 39, "secondary": 16, "tertiary": 0},
                "port_royal":      {"highway": 68, "primary": 20, "secondary": 12, "tertiary": 0}
            }
            road_types = overrides.get(kingston_location, {"highway": 75, "primary": 15, "secondary": 10, "tertiary": 0})

        else:  # Highways avoided, but still allow minimal highway usage
            forced_min_highway = 28
            overrides_avoid_highway = {
                "halfway_tree":        {"highway": 28, "primary": 52, "secondary": 20, "tertiary": 0},
                "new_kingston":        {"highway": 27, "primary": 53, "secondary": 20, "tertiary": 0},
                "cross_roads":         {"highway": 26, "primary": 54, "secondary": 20, "tertiary": 0},
                "mona":                {"highway": 25, "primary": 55, "secondary": 20, "tertiary": 0},
                "liguanea":            {"highway": 24, "primary": 56, "secondary": 20, "tertiary": 0},
                "papine":              {"highway": 23, "primary": 57, "secondary": 20, "tertiary": 0},
                "university_hospital": {"highway": 25, "primary": 54, "secondary": 21, "tertiary": 0},
                "mona_heights":        {"highway": 25, "primary": 53, "secondary": 22, "tertiary": 0},
                "hope_zoo":            {"highway": 24, "primary": 56, "secondary": 20, "tertiary": 0},
                "barbican":            {"highway": 25, "primary": 55, "secondary": 20, "tertiary": 0},
                "constant_spring":     {"highway": 26, "primary": 54, "secondary": 20, "tertiary": 0},
                "manor_park":          {"highway": 25, "primary": 53, "secondary": 22, "tertiary": 0},
                "port_royal":          {"highway": 26, "primary": 52, "secondary": 22, "tertiary": 0}
            }
            road_types = overrides_avoid_highway.get(kingston_location, {"highway": 25, "primary": 55, "secondary": 20, "tertiary": 0})


            # Normalize to 100
            total = sum(road_types.values())
            if total != 100:
                max_type = max(road_types, key=road_types.get)
                road_types[max_type] += 100 - total

    elif is_spanish_oldharbour:
        if options.get("highways", False):  # Highways avoided
            road_types = {"highway": 0, "primary": 100, "secondary": 0, "tertiary": 0}
        else:
            road_types = {"highway": 80, "primary": 15, "secondary": 5, "tertiary": 0}

    # Traffic estimation
    current_hour = time.localtime().tm_hour
    day_of_week = time.strftime("%A")
    is_weekday = day_of_week not in ["Saturday", "Sunday"]
    is_morning_rush = is_weekday and 7 <= current_hour <= 9
    is_evening_rush = is_weekday and 16 <= current_hour <= 18

    if is_morning_rush or is_evening_rush:
        traffic_level = "Heavy"
        estimated_delay = "30.0%"
    elif (is_weekday and (9 < current_hour < 16 or 18 < current_hour < 21)) or \
         (not is_weekday and 10 <= current_hour <= 18):
        traffic_level = "Moderate"
        estimated_delay = "15.0%"
    else:
        traffic_level = "Light"
        estimated_delay = "5.0%"

    # Road conditions
    road_conditions = [
        "Speed bumps in residential areas",
        "Some sections have potholes",
        "Pedestrian crossings near urban areas"
    ]
    if any(loc in path for loc in ["university_hospital", "mona", "papine", "mona_heights"]):
        road_conditions.append("University traffic and pedestrian crossings")
    if any(loc in path for loc in ["new_kingston", "halfway_tree", "cross_roads"]):
        road_conditions.append("Urban congestion during peak hours")
    if "spanish_town" in [source, destination]:
        road_conditions.append("Highway tolls may apply on some sections")

    # Avoided features
    avoided = []
    if options.get("tolls", False): avoided.append("toll roads")
    if options.get("highways", False): avoided.append("highways")
    if options.get("hillyRoads", False): avoided.append("hilly roads")
    if options.get("innerCity", False): avoided.append("inner-city roads")

    return {
        "road_types": road_types,
        "traffic": {
            "level": traffic_level,
            "factor": 1.0 + (float(estimated_delay.rstrip('%')) / 100),
            "estimated_delay": estimated_delay
        },
        "road_conditions": road_conditions[:3],
        "avoided": avoided if avoided else ["None"],
        "preference": f"Optimized for {'time' if preference == 'fastest' else 'distance'}"
    }



if __name__ == "__main__":
    # Default port is 5000, can be overridden by environment variable
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    print(f"Starting server on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port)