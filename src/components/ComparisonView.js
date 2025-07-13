/*
Names: Shanaldo Carty
Completion Date: 5/7/2025
*/

import React from 'react';
import MapView from './MapView';

const ComparisonView = ({ routeResults }) => {
  // Don't render anything if no route results are provided
  if (!routeResults) {
    return null;
  }

  // Extract the results from our algorithm and from OpenRouteService
  const { our_algorithm, openrouteservice } = routeResults;

  // Helper function to create a visual route path with arrows
  // This displays the sequence of locations the route passes through
  const renderRoutePath = (route) => {
    if (!route) return null;
    
    // Use detailed_route if available, otherwise use route_towns
    // detailed_route includes intermediate points along the way
    const routePoints = route.detailed_route || route.route_towns;
    
    if (!routePoints || routePoints.length === 0) return null;
    
    return (
      <div className="visual-route-path">
        {routePoints.map((point, index) => (
          <React.Fragment key={index}>
            {/* Each location point with a marker */}
            <div className={`route-point ${index === 0 ? 'start-point' : index === routePoints.length - 1 ? 'end-point' : 'intermediate-point'}`}>
              <div className="point-marker"></div>
              <div className="point-name">{point}</div>
            </div>
            {/* Add an arrow between points (except after the last point) */}
            {index < routePoints.length - 1 && (
              <div className="route-arrow">→</div>
            )}
          </React.Fragment>
        ))}
      </div>
    );
  };

  return (
    <div className="comparison-container">
      <h2 className="comparison-title">Route Comparison</h2>
      
      {/* AI-Based Road Conditions Card */}
      {/* Shows road types, traffic, weather, and advisories */}
      {our_algorithm && our_algorithm.road_summary && (
        <div className="road-conditions-card">
          <h3 className="section-title">Route Analysis</h3>
          
          <div className="road-summary-container">
            {/* Road Type Distribution */}
            <div className="summary-section">
              <h4>Road Type Distribution</h4>
              <div className="road-types-bar">
                {/* Create color-coded bar segments for each road type */}
                {Object.entries(our_algorithm.road_summary.road_types).map(([type, percentage]) => (
                  <div key={type} 
                       className={`road-type-segment ${type}`} 
                       style={{width: `${percentage}%`}}
                       title={`${type}: ${percentage}%`}>
                    {percentage > 10 && `${percentage}%`}
                  </div>
                ))}
              </div>
              {/* Legend explaining the colors */}
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
            
            {/* Traffic & Weather */}
            <div className="summary-section">
              <div className="summary-row">
                <div className="traffic-info">
                  <h4>Traffic Conditions</h4>
                  <p className={`traffic-level ${our_algorithm.road_summary.traffic.level.toLowerCase()}`}>
                    {our_algorithm.road_summary.traffic.level} ({our_algorithm.road_summary.traffic.estimated_delay} delay)
                  </p>
                </div>
                
                {/* Weather information (if available) */}
                {our_algorithm.best_route && our_algorithm.best_route.weather && (
                  <div className="weather-info">
                    <h4>Weather at Destination</h4>
                    <p>{our_algorithm.best_route.weather.condition}, {our_algorithm.best_route.weather.temperature}</p>
                    <p>Humidity: {our_algorithm.best_route.weather.humidity}, Wind: {our_algorithm.best_route.weather.wind}</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Route Advisories */}
            <div className="summary-section">
              <h4>Route Advisories</h4>
              <ul className="advisories-list">
                {/* Display each road condition as a list item */}
                {our_algorithm.road_summary.road_conditions.map((condition, index) => (
                  <li key={index}>{condition}</li>
                ))}
                {/* Show what road types are being avoided (if any) */}
                {our_algorithm.road_summary.avoided.length > 0 && our_algorithm.road_summary.avoided[0] !== "None" && (
                  <li>Avoiding: {our_algorithm.road_summary.avoided.join(', ')}</li>
                )}
              </ul>
              <p className="preference-note">{our_algorithm.road_summary.preference}</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="comparison-view">
        {/* Our Algorithm Section */}
        <div className="algorithm-section">
          <h3 className="section-title">Our Algorithm Results</h3>
          
          {our_algorithm && our_algorithm.best_route ? (
            <>
              {/* Display the best route calculated by our algorithm */}
              <div className="route-card">
                <h4 className="route-title">Best Route ({our_algorithm.best_route.preference})</h4>
                
                {/* Basic route information */}
                <div className="route-detail">
                  <span className="route-detail-label">From:</span>
                  <span>{our_algorithm.best_route.source}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">To:</span>
                  <span>{our_algorithm.best_route.destination}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">Distance:</span>
                  <span>{our_algorithm.best_route.distance}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">Time:</span>
                  <span>{our_algorithm.best_route.time}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">Algorithm:</span>
                  <span>{our_algorithm.best_route.algorithm}</span>
                </div>
                
                {/* Visual representation of the route */}
                <div className="route-path">
                  <h5>Route Path:</h5>
                  {renderRoutePath(our_algorithm.best_route)}
                </div>
              </div>
              
              {/* Alternative route (if available) */}
              {our_algorithm.alternative_route && (
                <div className="route-card alternative">
                  <h4 className="route-title">Alternative Route ({our_algorithm.alternative_route.preference})</h4>
                  
                  <div className="route-detail">
                    <span className="route-detail-label">Distance:</span>
                    <span>{our_algorithm.alternative_route.distance}</span>
                  </div>
                  
                  <div className="route-detail">
                    <span className="route-detail-label">Time:</span>
                    <span>{our_algorithm.alternative_route.time}</span>
                  </div>
                  
                  <div className="route-path">
                    <h5>Route Path:</h5>
                    {renderRoutePath(our_algorithm.alternative_route)}
                  </div>

                  {/* Show how alternative route compares to best route */}
                  {our_algorithm.alternative_route.comparison && (
                    <div className="route-comparison">
                      <div className="comparison-note">
                        <p>Compared to best route:</p>
                        <p>Distance difference: {our_algorithm.alternative_route.comparison.distance_diff}</p>
                        <p>Time difference: {our_algorithm.alternative_route.comparison.time_diff}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <p className="no-results">No routes found with our algorithm</p>
          )}
        </div>
        
        {/* OpenRouteService API Section */}
        <div className="api-section">
          <h3 className="section-title">OpenRouteService API Results</h3>
          
          {openrouteservice && openrouteservice.best_route ? (
            <>
              {/* Best ORS route */}
              <div className="route-card">
                <h4 className="route-title">Best Route ({openrouteservice.best_route.preference})</h4>
                
                <div className="route-detail">
                  <span className="route-detail-label">From:</span>
                  <span>{openrouteservice.best_route.source}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">To:</span>
                  <span>{openrouteservice.best_route.destination}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">Distance:</span>
                  <span>{openrouteservice.best_route.distance}</span>
                </div>
                
                <div className="route-detail">
                  <span className="route-detail-label">Time:</span>
                  <span>{openrouteservice.best_route.time}</span>
                </div>
                
                {/* Show detailed route if available */}
                {openrouteservice.best_route.detailed_route && (
                  <div className="route-path">
                    <h5>Route Path:</h5>
                    {renderRoutePath(openrouteservice.best_route)}
                  </div>
                )}
              </div>
              
              {/* Alternative ORS route (if available) */}
              {openrouteservice.alternative_route && (
                <div className="route-card alternative">
                  <h4 className="route-title">Alternative Route ({openrouteservice.alternative_route.preference})</h4>
                  
                  <div className="route-detail">
                    <span className="route-detail-label">Distance:</span>
                    <span>{openrouteservice.alternative_route.distance}</span>
                  </div>
                  
                  <div className="route-detail">
                    <span className="route-detail-label">Time:</span>
                    <span>{openrouteservice.alternative_route.time}</span>
                  </div>
                  
                  {openrouteservice.alternative_route.detailed_route && (
                    <div className="route-path">
                      <h5>Route Path:</h5>
                      {renderRoutePath(openrouteservice.alternative_route)}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <p className="no-results">No routes found with OpenRouteService API</p>
          )}
        </div>
      </div>
      
      {/* Map for visualizing the routes */}
      {openrouteservice && openrouteservice.visualization && openrouteservice.visualization.best_route && openrouteservice.visualization.best_route.route && (
        <div className="map-section">
          <h3 className="section-title">Route Visualization</h3>
          <div className="map-container">
            <MapView 
              routesData={[
                openrouteservice.visualization.best_route,
                openrouteservice.visualization.alternative_route
              ].filter(Boolean)} 
            />
          </div>
          <div className="map-note">
            <p><em>Map shows the routes calculated by your algorithm, visualized through OpenRouteService API.</em></p>
          </div>
        </div>
      )}
      
      {/* Algorithm Performance section - Moved below the map for better visual flow */}
      {our_algorithm && our_algorithm.best_route && (
        <div className="algorithm-performance">
          <h3 className="section-title">Algorithm Performance</h3>
          <div className="performance-metrics">
            <div className="metric">
              <span className="metric-label">Execution Time:</span>
              <span className="metric-value">{our_algorithm.best_route.execution_time_ms.toFixed(2)} ms</span>
            </div>
            <div className="metric">
              <span className="metric-label">Nodes Visited:</span>
              <span className="metric-value">{our_algorithm.best_route.nodes_visited}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Edge Relaxations:</span>
              <span className="metric-value">{our_algorithm.best_route.edge_relaxations}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Operations:</span>
              <span className="metric-value">{our_algorithm.best_route.operations}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Styles for the comparison view */}
      <style jsx>{`
        .comparison-container {
          background-color: white;
          padding: 24px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          margin-top: 30px;
        }
        
        .comparison-title {
          text-align: center;
          margin-bottom: 24px;
          color: #4285f4;
        }
        
        .road-conditions-card {
          background-color: #f8f9fa;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 30px;
          border: 1px solid #e1e4e8;
        }
        
        .section-title {
          margin-top: 0;
          padding-bottom: 10px;
          border-bottom: 2px solid #eee;
          margin-bottom: 16px;
          color: #202124;
        }
        
        .summary-section {
          margin-bottom: 24px;
        }
        
        .summary-section h4 {
          margin-bottom: 12px;
          color: #4285f4;
        }
        
        .road-types-bar {
          display: flex;
          height: 30px;
          border-radius: 4px;
          overflow: hidden;
          margin-top: 8px;
          margin-bottom: 8px;
        }
        
        .road-type-segment {
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 12px;
          font-weight: 500;
        }
        
        .road-type-segment.highway {
          background-color: #4285f4;
        }
        
        .road-type-segment.primary {
          background-color: #34a853;
        }
        
        .road-type-segment.secondary {
          background-color: #fbbc05;
          color: #333;
        }
        
        .road-type-segment.tertiary {
          background-color: #ea4335;
        }
        
        .road-types-legend {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 8px;
        }
        
        .legend-item {
          display: flex;
          align-items: center;
          margin-right: 12px;
        }
        
        .legend-color {
          width: 16px;
          height: 16px;
          margin-right: 6px;
          border-radius: 2px;
        }
        
        .legend-color.highway {
          background-color: #4285f4;
        }
        
        .legend-color.primary {
          background-color: #34a853;
        }
        
        .legend-color.secondary {
          background-color: #fbbc05;
        }
        
        .legend-color.tertiary {
          background-color: #ea4335;
        }
        
        .summary-row {
          display: flex;
          flex-wrap: wrap;
          gap: 24px;
        }
        
        .traffic-info, .weather-info {
          flex: 1;
          min-width: 200px;
        }
        
        .traffic-level {
          display: inline-block;
          padding: 6px 12px;
          border-radius: 4px;
          font-weight: 500;
        }
        
        .traffic-level.light {
          background-color: #e6f4ea;
          color: #137333;
        }
        
        .traffic-level.moderate {
          background-color: #fef7e0;
          color: #ea8600;
        }
        
        .traffic-level.heavy {
          background-color: #fce8e6;
          color: #c5221f;
        }
        
        .advisories-list {
          padding-left: 24px;
          margin-top: 10px;
        }
        
        .advisories-list li {
          margin-bottom: 8px;
        }
        
        .preference-note {
          font-style: italic;
          margin-top: 16px;
          color: #5f6368;
        }
        
        .comparison-view {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
          .comparison-view {
            grid-template-columns: 1fr;
          }
        }
        
        .route-card {
          background-color: #f8f9fa;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 20px;
          border: 1px solid #e1e4e8;
        }
        
        .route-card.alternative {
          background-color: #f0f4f8;
          border-left: 3px solid #4285f4;
        }
        
        .route-title {
          margin-top: 0;
          margin-bottom: 16px;
          color: #4285f4;
        }
        
        .route-detail {
          margin-bottom: 10px;
          line-height: 1.5;
        }
        
        .route-detail-label {
          font-weight: 500;
          margin-right: 8px;
          color: #5f6368;
        }
        
        .route-path {
          margin-top: 16px;
        }
        
        .route-path h5 {
          margin-bottom: 12px;
          color: #5f6368;
        }
        
        .visual-route-path {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          padding: 12px;
          background-color: #fff;
          border-radius: 4px;
          border: 1px solid #e1e4e8;
        }
        
        .route-point {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 0 4px;
        }
        
        .point-marker {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-bottom: 4px;
        }
        
        .start-point .point-marker {
          background-color: #34a853;
        }
        
        .end-point .point-marker {
          background-color: #ea4335;
        }
        
        .intermediate-point .point-marker {
          background-color: #4285f4;
        }
        
        .point-name {
          font-size: 12px;
          max-width: 120px;
          text-align: center;
          word-break: break-word;
        }
        
        .route-arrow {
          margin: 0 4px;
          color: #4285f4;
        }
        
        .algorithm-performance {
          background-color: #f8f9fa;
          border-radius: 8px;
          padding: 16px;
          margin-top: 20px;
          border: 1px solid #e1e4e8;
        }
        
        .algorithm-performance h4 {
          margin-top: 0;
          margin-bottom: 12px;
          color: #4285f4;
        }
        
        .performance-metrics {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        
        .metric {
          padding: 8px;
          background-color: #fff;
          border-radius: 4px;
          border: 1px solid #e1e4e8;
        }
        
        .metric-label {
          font-weight: 500;
          color: #5f6368;
          margin-right: 8px;
        }
        
        .route-comparison {
          margin-top: 12px;
          padding: 10px;
          background-color: #fff;
          border-radius: 4px;
          border: 1px solid #e1e4e8;
        }
        
        .comparison-note {
          font-size: 0.9em;
          color: #5f6368;
        }
        
        .comparison-note p {
          margin: 4px 0;
        }
        
        .map-container {
          height: 400px;
          border-radius: 8px;
          overflow: hidden;
          border: 1px solid #e1e4e8;
        }
        
        .map-note {
          text-align: center;
          margin-top: 10px;
          color: #5f6368;
          font-size: 0.9em;
        }
        
        .no-results {
          padding: 40px 0;
          text-align: center;
          color: #5f6368;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default ComparisonView;
