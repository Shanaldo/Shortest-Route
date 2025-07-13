/*
Names: Shanaldo Carty, Rachjae Gayle, Shanice Burrell, Rajaire Thomas
ID#: 2108949, 2100400, 2202903, 2207216
Completion Date: 4/4/2025
*/

import React, { useEffect } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import polyline from "@mapbox/polyline";

// Fix for Leaflet's icon issue in React
// Leaflet expects icons to be in a specific location, but webpack changes file paths
// This fixes that by explicitly setting the icon URLs
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

// Custom icons for different types of markers on the map
// These make it easier to distinguish between the start, end, and waypoints
const customIcons = {
  start: new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    iconSize: [30, 46],        // Slightly larger for importance
    iconAnchor: [15, 46],      // Bottom center of the icon
    popupAnchor: [0, -46],     // Popup appears above the icon
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    shadowSize: [41, 41],
    className: 'start-marker'  // For custom CSS styling
  }),
  end: new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    iconSize: [30, 46],
    iconAnchor: [15, 46],
    popupAnchor: [0, -46],
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    shadowSize: [41, 41],
    className: 'end-marker'
  }),
  waypoint: new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    iconSize: [20, 33],        // Smaller for less visual clutter
    iconAnchor: [10, 33],
    popupAnchor: [0, -33],
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    shadowSize: [33, 33],
    className: 'waypoint-marker'
  })
};

// Component to automatically fit the map to show all route coordinates
// This ensures the entire route is visible without manual zooming/panning
const FitBounds = ({ coordinates }) => {
  const map = useMap();

  useEffect(() => {
    if (coordinates && coordinates.length > 0) {
      // Create a bounds object that encompasses all coordinates
      const bounds = L.latLngBounds(coordinates);
      // Fit the map to these bounds with some padding
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coordinates, map]);

  return null;  // This component doesn't render anything visible
};

// Helper function to select waypoints at regular intervals along the route
// This avoids cluttering the map with too many markers
const getWaypoints = (coordinates, count = 4) => {
  const waypoints = [];

  if (!coordinates || coordinates.length <= 2) return [];

  // Calculate how many points to skip between each waypoint
  const step = Math.floor(coordinates.length / (count + 1));

  // Place waypoints at regular intervals along the route
  for (let i = 1; i <= count; i++) {
    const index = i * step;
    if (index < coordinates.length - 1) {
      waypoints.push({
        position: coordinates[index],
        description: `Waypoint ${i}`
      });
    }
  }

  return waypoints;
};

// The main MapView component
const MapView = ({ routesData }) => {
  // Default center point in Jamaica if no route data is available
  const defaultCenter = [18.1096, -77.2975]; // Center of Jamaica

  // Handle the case when no route data is provided
  if (!routesData || routesData.length === 0) {
    return (
      <div className="map-container">
        <MapContainer center={defaultCenter} zoom={8} className="leaflet-container">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
        </MapContainer>
      </div>
    );
  }

  // Extract the best and alternative routes from the data
  const bestRoute = routesData[0];
  const alternativeRoute = routesData.length > 1 ? routesData[1] : null;

  // Make sure we have valid route data
  if (!bestRoute.route) {
    console.error("Best route is missing valid polyline data.");
    return (
      <div className="map-container">
        <MapContainer center={defaultCenter} zoom={8} className="leaflet-container">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <div className="map-error-message">
            Route geometry data is missing
          </div>
        </MapContainer>
      </div>
    );
  }

  // Decode the polyline data (the encoded route path)
  let bestRouteCoords, altRouteCoords;
  try {
    // OpenRouteService returns coordinates in encoded polyline format
    // We need to decode this into actual coordinates
    bestRouteCoords = polyline.decode(bestRoute.route);
    
    if (alternativeRoute && alternativeRoute.route) {
      altRouteCoords = polyline.decode(alternativeRoute.route);
    }
  } catch (error) {
    console.error("Error decoding polyline data:", error);
    return (
      <div className="map-container">
        <MapContainer center={defaultCenter} zoom={8} className="leaflet-container">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <div className="map-error-message">
            Error decoding route data
          </div>
        </MapContainer>
      </div>
    );
  }

  // Get coordinates for the start and end markers
  // Use exact coordinates from geocoding if available, otherwise use the route ends
  let startCoords, endCoords;
  
  if (bestRoute.exact_coordinates && bestRoute.exact_coordinates.source) {
    startCoords = bestRoute.exact_coordinates.source;
  } else {
    startCoords = bestRouteCoords[0];
  }
  
  if (bestRoute.exact_coordinates && bestRoute.exact_coordinates.destination) {
    endCoords = bestRoute.exact_coordinates.destination;
  } else {
    endCoords = bestRouteCoords[bestRouteCoords.length - 1];
  }

  // Generate waypoints to show along the routes
  const waypoints = [
    ...getWaypoints(bestRouteCoords, 2),
    ...(altRouteCoords ? getWaypoints(altRouteCoords, 2) : [])
  ];

  return (
    <div className="map-container">
      <MapContainer center={startCoords} zoom={10} className="leaflet-container">
        {/* Component to auto-fit the map to show the entire route */}
        <FitBounds coordinates={[...bestRouteCoords, ...(altRouteCoords || [])]} />
        
        {/* Base map layer - OpenStreetMap tiles */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Display the best route as a blue line */}
        <Polyline 
          positions={bestRouteCoords} 
          pathOptions={{ 
            color: 'blue', 
            weight: 5,       // Line thickness
            opacity: 0.9     // Slightly transparent
          }}
        >
          <Popup>
            <strong>Best Route</strong><br />
            Distance: {bestRoute.distance}<br />
            Time: {bestRoute.time}<br />
            Preference: {bestRoute.preference}
          </Popup>
        </Polyline>

        {/* Display the alternative route as a dashed green line if available */}
        {altRouteCoords && altRouteCoords.length > 0 && (
          <Polyline 
            positions={altRouteCoords} 
            pathOptions={{ 
              color: 'green', 
              weight: 4,         // Slightly thinner than the main route
              opacity: 0.8,
              dashArray: '10, 5' // Dashed line pattern
            }}
          >
            <Popup>
              <strong>Alternative Route</strong><br />
              Distance: {alternativeRoute.distance}<br />
              Time: {alternativeRoute.time}<br />
              Preference: {alternativeRoute.preference}
              {alternativeRoute.comparison && (
                <>
                  <br />
                  <span>Difference: {alternativeRoute.comparison.distance_diff} distance, {alternativeRoute.comparison.time_diff} time</span>
                </>
              )}
            </Popup>
          </Polyline>
        )}

        {/* Start marker */}
        <Marker position={startCoords} icon={customIcons.start}>
          <Popup>
            <strong>Start:</strong> {bestRoute.source || bestRoute.original_source}<br/>
            {bestRoute.mapped_source && bestRoute.mapped_source !== bestRoute.source && (
              <span>Mapped to: {bestRoute.mapped_source}</span>
            )}
          </Popup>
        </Marker>

        {/* End marker */}
        <Marker position={endCoords} icon={customIcons.end}>
          <Popup>
            <strong>End:</strong> {bestRoute.destination || bestRoute.original_destination}<br/>
            {bestRoute.mapped_destination && bestRoute.mapped_destination !== bestRoute.destination && (
              <span>Mapped to: {bestRoute.mapped_destination}</span>
            )}
          </Popup>
        </Marker>

        {/* Waypoint markers along the route */}
        {waypoints.map((waypoint, index) => (
          <Marker 
            key={index} 
            position={waypoint.position} 
            icon={customIcons.waypoint}
          >
            <Popup>{waypoint.description}</Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map legend to explain the different line colors and markers */}
      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: "blue" }}></div>
          <span>Best Route</span>
        </div>
        
        {altRouteCoords && (
          <div className="legend-item">
            <div 
              className="legend-color" 
              style={{ 
                backgroundColor: "green",
                borderTop: "1px dashed white",
                borderBottom: "1px dashed white"
              }}
            ></div>
            <span>Alternative Route</span>
          </div>
        )}
        
        <div className="legend-item">
          <div className="legend-color">🔵</div>
          <span>Waypoints</span>
        </div>
      </div>
    </div>
  );
};

export default MapView;