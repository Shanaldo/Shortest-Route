/*
Names: Shanaldo Carty, Rachjae Gayle, Shanice Burrell, Rajaire Thomas
ID#: 2108949, 2100400, 2202903, 2207216
Completion Date: 4/4/2025
*/

import React from 'react';

const RoadConditionsCard = ({ roadSummary, weather }) => {
  // Don't render anything if we don't have road summary data
  if (!roadSummary) return null;
  
  return (
    <div className="road-conditions-card">
      <h3 className="section-title">Route Analysis</h3>
      
      <div className="road-summary-container">
        {/* Road Type Distribution section */}
        {/* This shows what percentage of the route is on different road types */}
        <div className="summary-section">
          <h4>Road Type Distribution</h4>
          <div className="road-types-bar">
            {/* Create colored segments for each road type */}
            {Object.entries(roadSummary.road_types).map(([type, percentage]) => (
              <div key={type} 
                   className={`road-type-segment ${type}`} 
                   style={{width: `${percentage}%`}}
                   title={`${type}: ${percentage}%`}>
                {/* Only show text for segments that are wide enough */}
                {percentage > 10 && `${percentage}%`}
              </div>
            ))}
          </div>
          {/* Legend explaining what each color means */}
          <div className="road-types-legend">
            <div className="legend-item">
              <span className="legend-color highway"></span>Highway
            </div>
            <div className="legend-item">
              <span className="legend-color primary"></span>Primary
            </div>
            <div className="legend-item">
              <span className="legend-color secondary"></span>Secondary
            </div>
            <div className="legend-item">
              <span className="legend-color tertiary"></span>Tertiary
            </div>
          </div>
        </div>
        
        {/* Traffic and Weather section */}
        <div className="summary-section">
          <div className="summary-row">
            {/* Traffic conditions - show current traffic level and expected delay */}
            <div className="traffic-info">
              <h4>Traffic Conditions</h4>
              <p className={`traffic-level ${roadSummary.traffic.level.toLowerCase()}`}>
                {roadSummary.traffic.level} ({roadSummary.traffic.estimated_delay} delay)
              </p>
            </div>
            
            {/* Weather info at the destination (if available) */}
            {weather && (
              <div className="weather-info">
                <h4>Weather at Destination</h4>
                <p>{weather.condition}, {weather.temperature}</p>
                <p>Humidity: {weather.humidity}, Wind: {weather.wind}</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Route Advisories section */}
        {/* Lists specific conditions and warnings for this route */}
        <div className="summary-section">
          <h4>Route Advisories</h4>
          <ul className="advisories-list">
            {/* Display each road condition as a list item */}
            {roadSummary.road_conditions.map((condition, index) => (
              <li key={index}>{condition}</li>
            ))}
            {/* Show what road types are being avoided (if any) */}
            {roadSummary.avoided.length > 0 && roadSummary.avoided[0] !== "None" && (
              <li>Avoiding: {roadSummary.avoided.join(', ')}</li>
            )}
          </ul>
          {/* Show whether route was optimized for time or distance */}
          <p className="preference-note">{roadSummary.preference}</p>
        </div>
      </div>
    </div>
  );
};

export default RoadConditionsCard;