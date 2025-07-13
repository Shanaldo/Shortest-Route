"""
Names: Shanaldo Carty,
Completion Date: 08/7/2025
"""

"""
Geocoding service for Jamaica Route Finder project.
This file handles converting place names to map coordinates and vice versa.
"""

import requests  # For making HTTP requests
from time import sleep  # For adding delays between API calls

class GeocodingService:
    """
    This class handles converting between place names and map coordinates.
    
    It uses OpenStreetMap's Nominatim service to look up locations by name
    and find addresses for coordinates. This is basically the same service
    that powers the search function on many maps.
    """
    
    def __init__(self):
        """
        Sets up the geocoding service with the necessary configuration.
        """
        # Base URL for the Nominatim service
        self.base_url = "https://nominatim.openstreetmap.org"
        # Headers to send with our requests
        # Nominatim requires a user agent, so we identify our application
        self.headers = {
            "User-Agent": "JamaicaRouteFinder/1.0",  # Required by Nominatim's terms of service
            "Accept-Language": "en-US,en;q=0.9"      # Prefer English results
        }
    
    def geocode(self, place_name, country_filter="Jamaica"):
        """
        Converts a place name to coordinates (latitude and longitude).
        
        This is used when a user enters a location name and we need to
        figure out where on the map it is.
        """
        # Add a delay to avoid hitting rate limits
        # Nominatim asks users to wait between requests
        sleep(1)
        
        # Set up the search request
        search_url = f"{self.base_url}/search"
        params = {
            "q": place_name,                # The place we're looking for
            "format": "json",               # Get results in JSON format
            "limit": 1,                     # We only want the top result
            "country": country_filter,      # Limit to Jamaica
            "addressdetails": 1             # Include full address details
        }
        
        try:
            # Make the request to the Nominatim API
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()  # This will raise an exception if the request fails
            
            results = response.json()
            
            # If we got results, extract and return the location info
            if results and len(results) > 0:
                location = results[0]
                return {
                    "lat": float(location["lat"]),  # Latitude
                    "lng": float(location["lon"]),  # Longitude
                    "display_name": location["display_name"],  # Full address
                    "place_id": location["place_id"],  # Unique ID for this place
                    "address": location.get("address", {}),  # Address components
                    "importance": location.get("importance", 0)  # How important/prominent this place is
                }
            return None  # No results found
            
        except Exception as e:
            # If anything goes wrong, log it and return None
            print(f"Geocoding error: {str(e)}")
            return None
    
    def reverse_geocode(self, lat, lng):
        """
        Converts coordinates to a place name and address.
        
        This is used when we have a point on the map and need to figure
        out what address or location it corresponds to.
        """
        # Add a delay to avoid hitting rate limits
        sleep(1)
        
        # Set up the reverse geocoding request
        reverse_url = f"{self.base_url}/reverse"
        params = {
            "lat": lat,              # Latitude
            "lon": lng,              # Longitude
            "format": "json",        # Get results in JSON format
            "addressdetails": 1      # Include full address details
        }
        
        try:
            # Make the request to the Nominatim API
            response = requests.get(reverse_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            # If we didn't get an error, return the address info
            if "error" not in result:
                return {
                    "display_name": result.get("display_name"),  # Full address
                    "address": result.get("address", {}),        # Address components
                    "place_id": result.get("place_id")           # Unique ID for this place
                }
            return None
            
        except Exception as e:
            # If anything goes wrong, log it and return None
            print(f"Reverse geocoding error: {str(e)}")
            return None
