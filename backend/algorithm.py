"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Enhanced routing algorithms for the Jamaica Route Finder project.
This file contains the algorithms that find the best routes between locations in Jamaica.
"""

import heapq          # For priority queues
import time as timer  # For measuring algorithm execution time
import math
from collections import defaultdict, deque

class RouteAlgorithms:
    """
    This class handles all the route-finding logic for our application.
    It contains implementations of Dijkstra's algorithm and A* search to find
    optimal routes between locations.
    """
    
    def __init__(self, locations_data, distance_matrix):
        """
        Sets up the route algorithms with location data and distance information.
        
        locations_data: Contains all the locations and their coordinates
        distance_matrix: Pre-calculated distances and travel times
        """
        # Store the locations and distances for later use
        self.locations = locations_data
        self.matrix = distance_matrix
        self.distances = distance_matrix["distances"]
        self.times = distance_matrix["times"]
    
    def get_adjacent_locations(self, location_id):
        """
        Gets all locations that can be reached directly from the given location.
        In our model, we're assuming all locations are directly connected to each other.
        
        location_id: The location we want to find connections from
        
        Returns a list of connected location IDs
        """
        # Simply return all the locations that have a distance from this one
        return list(self.distances[location_id].keys())
    
    def dijkstra_algorithm(self, source, destination, optimize_for="distance", avoid_options=None):
        def run_dijkstra(avoid_highways=True):
            # Initialization
            start_time = timer.time()
            nodes_visited = 0
            edge_relaxations = 0

            # Choose weight matrix based on optimization preference
            weight_matrix = self.distances if optimize_for == "distance" else self.times
            # Initialize distances to infinity for all locations
            distances = {loc: float('infinity') for loc in self.locations}
            distances[source] = 0
            # Priority queue with start node
            priority_queue = [(0, source)]
            # Track previous node for path reconstruction
            previous = {loc: None for loc in self.locations}

            # Handle avoidance options
            avoided_types = []
            if avoid_options:
                if avoid_options.get("tolls", False):
                    avoided_types.append("toll")
                if avoid_options.get("highways", False) and avoid_highways:
                    avoided_types.append("highway")

            highways_used = False  # Track if highways are used

            #Main Dijkstra loop
            while priority_queue:
                current_distance, current_node = heapq.heappop(priority_queue)
                nodes_visited += 1
                
                # If reached destination, break the loop
                if current_node == destination:
                    break
                
                # Skip if we've found a better path already
                if current_distance > distances[current_node]:
                    continue

                # Check all neighboring locations
                for neighbor in self.get_adjacent_locations(current_node):
                    # Check if raod type should be avoided
                    road_type = self.classify_road_type(current_node, neighbor)
                    if road_type in avoided_types:
                        continue

                    if road_type == "highway":
                        highways_used = True  # Mark if a highway is used

                    # Calculate new distance
                    weight = weight_matrix[current_node][neighbor]
                    distance = current_distance + weight
                    edge_relaxations += 1

                    # If found shorter path, update
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))

            # Reconstruct path
            path = []
            current = destination
            while current:
                path.append(current)
                current = previous[current]
            path.reverse()

            # Validate path (must include source and destination)
            if len(path) < 2 or path[0] != source or path[-1] != destination:
                return None

            # Cakcukate metrics
            total_distance = sum(self.distances[path[i]][path[i+1]] for i in range(len(path) - 1))
            total_time = sum(self.times[path[i]][path[i+1]] for i in range(len(path) - 1))
            execution_time = (timer.time() - start_time) * 1000

            # Return detailed result
            return {
                "path": path,
                "path_names": [self.locations[loc]["display_name"] for loc in path],
                "distance": round(total_distance, 2),
                "time": round(total_time, 2),
                "algorithm": "Dijkstra's Algorithm",
                "algorithm_description": "Uses Dijkstra's shortest path algorithm with pre-calculated distances/times",
                "time_complexity": "O((V+E)log V)",
                "space_complexity": "O(V)",
                "execution_time_ms": execution_time,
                "nodes_visited": nodes_visited,
                "edge_relaxations": edge_relaxations,
                "operations": len(path) - 1,
                "highways_used": highways_used  # Add flag to indicate highway usage
            }

        # First attempt: try to avoid highways
        result = run_dijkstra(avoid_highways=True)

        # Flag to indicate if highways were used despite avoidance
        used_highway_despite_avoidance = False

        # Fallback: allow highways if no path found and user asked to avoid them
        if result is None and avoid_options and avoid_options.get("highways", False):
            result = run_dijkstra(avoid_highways=False)
            if result and result.get("highways_used", False):
                used_highway_despite_avoidance = True

        # If no valid path found
        if result is None:
            return {
                "error": "No valid path found",
                "algorithm": "Dijkstra's Algorithm",
                "execution_time_ms": 0,
                "nodes_visited": 0,
                "edge_relaxations": 0
            }

        # Add flag indicating highways were used despite the request to avoid them
        if used_highway_despite_avoidance:
            result["used_highway_despite_avoidance"] = True

        return result

    def a_star_algorithm(self, source, destination, optimize_for="time", avoid_options=None):
        def run_a_star(avoid_highways=True):
            # Start timing
            start_time = timer.time()

            nodes_visited = 0
            edge_relaxations = 0
            
            # Choose weight matrix
            weight_matrix = self.distances if optimize_for == "distance" else self.times
            
            # Handle avoidance options
            avoided_types = []
            if avoid_options:
                if avoid_options.get("tolls", False):
                    avoided_types.append("toll")
                if avoid_options.get("highways", False) and avoid_highways:
                    avoided_types.append("highway")
                    
            # Get destination coordinates for heuristic         
            dest_coords = (self.locations[destination]["lat"], self.locations[destination]["lng"])
            
            #Intialize open set for A*
            open_set = []
            heapq.heappush(open_set, (0, source))
            came_from = {}

            # g_score tracks actual distance from start
            g_score = {loc: float('infinity') for loc in self.locations}
            g_score[source] = 0

            # f_score is g_score + heuristic estimate
            f_score = {loc: float('infinity') for loc in self.locations}
            source_coords = (self.locations[source]["lat"], self.locations[source]["lng"])
            f_score[source] = self.heuristic(source_coords, dest_coords, optimize_for)

            open_set_hash = {source} # For O(1) lookups

            highways_used = False  # Track if highways are used

            # Main A* loop
            while open_set:
                # Get node with lowest f_score
                current_f, current = heapq.heappop(open_set)
                open_set_hash.remove(current)
                nodes_visited += 1

                # If reached destination, reconstruct pat
                if current == destination:
                    # Reconstruct path
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.append(source)
                    path.reverse()

                    # Calculate metrics
                    total_distance = sum(self.distances[path[i]][path[i+1]] for i in range(len(path)-1))
                    total_time = sum(self.times[path[i]][path[i+1]] for i in range(len(path)-1))
                    execution_time = (timer.time() - start_time) * 1000

                    return {
                        "path": path,
                        "path_names": [self.locations[loc]["display_name"] for loc in path],
                        "distance": round(total_distance, 2),
                        "time": round(total_time, 2),
                        "algorithm": "A* Search Algorithm",
                        "algorithm_description": "Uses A* search with geographic heuristic to find optimal routes",
                        "time_complexity": "O(E) with a good heuristic",
                        "space_complexity": "O(V)",
                        "execution_time_ms": execution_time,
                        "nodes_visited": nodes_visited,
                        "edge_relaxations": edge_relaxations,
                        "operations": len(path) - 1,
                        "highways_used": highways_used  # Track if highways are used
                    }
                
                # Check neighbors
                for neighbor in self.get_adjacent_locations(current):
                    # Check if road type should be avoided
                    road_type = self.classify_road_type(current, neighbor)
                    if road_type in avoided_types:
                        continue

                    if road_type == "highway":
                        highways_used = True  # Mark if a highway is used

                    # Calculate tentative g_score
                    weight = weight_matrix[current][neighbor]
                    tentative_g = g_score[current] + weight
                    edge_relaxations += 1

                    # If better path found
                    if tentative_g < g_score[neighbor]:
                        # Update path
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g

                        # Calculate f_score with heuristic
                        neighbor_coords = (self.locations[neighbor]["lat"], self.locations[neighbor]["lng"])
                        h = self.heuristic(neighbor_coords, dest_coords, optimize_for)
                        f_score[neighbor] = tentative_g + h

                        # Add to open set if not already there
                        if neighbor not in open_set_hash:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
                            open_set_hash.add(neighbor)

            return None  # No valid path found

        # First attempt: try to respect highway avoidance
        result = run_a_star(avoid_highways=True)

        # Flag to indicate if a highway was used despite avoidance
        used_highway_despite_avoidance = False

        # If that fails and user selected avoid highways, fallback and warn via summary later
        if result is None and avoid_options and avoid_options.get("highways", False):
            result = run_a_star(avoid_highways=False)
            if result and result.get("highways_used", False):
                used_highway_despite_avoidance = True

        # If no route at all
        if result is None:
            return {
                "error": "No valid path found",
                "algorithm": "A* Search Algorithm",
                "execution_time_ms": 0,
                "nodes_visited": 0,
                "edge_relaxations": 0
            }

        # Add flag indicating highways were used despite the request to avoid them
        if used_highway_despite_avoidance:
            result["used_highway_despite_avoidance"] = True

        return result


    
    def heuristic(self, current_coords, dest_coords, optimize_for="time"):
        """
        Calculates an estimate of the remaining cost to reach the destination.
        For A* to work well, this estimate should never exceed the actual cost.
        
        current_coords: Coordinates of current location
        dest_coords: Coordinates of destination
        optimize_for: Whether to estimate distance or time
        
        Returns estimated distance or time to destination
        """
        from geopy.distance import geodesic
        
        # Calculate straight-line distance between the points
        distance = geodesic(current_coords, dest_coords).kilometers
        
        if optimize_for == "distance":
            # For distance, just return the straight-line distance
            # (This works because no path can be shorter than a straight line)
            return distance
        else:  # optimize_for == "time"
            # For time, convert distance to time using an average speed
            # Assume 60 km/h average speed (1 km per minute)
            return (distance / 60) * 60  # Convert to minutes
    
    def classify_road_type(self, source, destination):
        """
        Figures out what kind of road connects two locations.
        This helps estimate travel times and handle road type preferences.
        
        source: Starting location ID
        destination: Ending location ID
        
        Returns the road type (highway, primary, secondary, tertiary)
        """
        # Known highways in Jamaica
        highways = [
            ("new_kingston", "spanish_town"),
            ("halfway_tree", "spanish_town"),
            ("cross_roads", "spanish_town"),
            ("spanish_town", "port_royal"),
            ("liguanea", "spanish_town"),
            ("papine", "spanish_town"),
            ("university_hospital", "spanish_town"),
            ("mona", "spanish_town"),
            ("mona_heights", "spanish_town"),
            ("hope_zoo", "spanish_town"),
            ("barbican", "spanish_town"),
            ("constant_spring", "spanish_town"),
            ("manor_park", "spanish_town"), 
            ("new_kingston", "old_harbour"),
            ("halfway_tree", "old_harbour"),
            ("cross_roads", "old_harbour"),
            ("old_harbour", "port_royal"),
            ("liguanea", "old_harbour"),
            ("papine", "old_harbour"),
            ("university_hospital", "old_harbour"),
            ("mona", "old_harbour"),
            ("mona_heights", "old_harbour"),
            ("hope_zoo", "old_harbour"),
            ("barbican", "old_harbour"),
            ("constant_spring", "old_harbour"),
            ("manor_park", "old_harbour"),  
        ]
        
        # Known primary roads
        primary_roads = [
            ("new_kingston", "halfway_tree"),
            ("new_kingston", "cross_roads"),
            ("new_kingston", "liguanea"),
            ("constant_spring", "halfway_tree"),
            ("manor_park", "constant_spring"),
            ("halfway_tree", "cross_roads"),
            ("liguanea", "hope_zoo"),
            ("liguanea", "papine"),
            ("liguanea", "mona"),
            ("hope_zoo", "papine"),
            ("mona", "papine"),
            ("papine", "university_hospital"),
            
        ]
        
        # Check if this is a known highway
        for start, end in highways:
            if (source == start and destination == end) or (source == end and destination == start):
                return "highway"
        
        # Check if this is a known primary road
        for start, end in primary_roads:
            if (source == start and destination == end) or (source == end and destination == start):
                return "primary"
        
        # University areas have smaller roads
        university_areas = ["mona", "papine", "university_hospital", "mona_heights", "hope_zoo"]
        if source in university_areas and destination in university_areas:
            return "tertiary"
        
        # Default to secondary roads for other connections
        return "primary"
        
        
    def find_shortest_route(self, source, destination, optimize_for="distance", avoid_options=None):
        """
        Convenience method to find the shortest route by distance.
        
        source: Starting point
        destination: Ending point
        optimize_for: Whether to find shortest distance or fastest time
        avoid_options: Options to avoid certain road types
        
        Returns the route details
        """
        return self.dijkstra_algorithm(source, destination, optimize_for, avoid_options)
    
    def find_fastest_route(self, source, destination, avoid_options=None):
        """
        Convenience method to find the fastest route by time.
        
        source: Starting point
        destination: Ending point
        avoid_options: Options to avoid certain road types
        
        Returns the route details
        """
        return self.a_star_algorithm(source, destination, "time", avoid_options)