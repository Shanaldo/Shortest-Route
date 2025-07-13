/*
Names: Shanaldo Carty
Completion Date: 5/7/2025
*/

import React, { useState, useEffect } from 'react';

const RouteErrorMessage = ({ error, availableLocations = [] }) => {
  // State to track whether to show the available routes modal
  const [showAvailableRoutes, setShowAvailableRoutes] = useState(false);
  // State to store the list of available locations
  const [locations, setLocations] = useState(availableLocations);
  // State to track if we're loading location data
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // If locations are provided as props, use them
    if (availableLocations && availableLocations.length > 0) {
      setLocations(availableLocations);
    }
    // If locations need to be fetched when modal opens and we don't have any yet
    else if (showAvailableRoutes && locations.length === 0) {
      // Start loading state
      setLoading(true);
      // Fetch available locations from the API
      fetch('/api/available-locations')
        .then(response => response.json())
        .then(data => {
          // Update state with the locations data
          setLocations(data.locations || []);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load available locations', err);
          setLoading(false);
        });
    }
  }, [showAvailableRoutes, availableLocations, locations.length]);
  
  // If there's no error, don't render anything
  if (!error) return null;
  
  // Check if error contains location constraint message
  // This helps us provide a more helpful response for location-related errors
  const isLocationConstraintError = error.includes("not available") || 
    error.includes("Could not find location") ||
    error.includes("Could not geocode location");
  
  return (
    <div className="error-container">
      <div className="error-content">
        {/* Error icon */}
        <div className="error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="36" height="36">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
        </div>
        
        {/* Error message */}
        <div className="error-message">
          <h3>Route Not Available</h3>
          <p>{error}</p>
          
          {/* For location errors, offer to show available locations */}
          {isLocationConstraintError && (
            <>
              <p className="constraint-message">
                Due to time constraints, not all routes have been updated yet. 
                Please select from the available locations.
              </p>
              
              <button 
                className="view-routes-button"
                onClick={() => setShowAvailableRoutes(true)}
              >
                View Available Routes
              </button>
            </>
          )}
        </div>
      </div>
      
      {/* Inline Available Routes Modal - only shown when requested */}
      {showAvailableRoutes && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <h2>Available Locations</h2>
              <button className="close-button" onClick={() => setShowAvailableRoutes(false)}>×</button>
            </div>
            
            <div className="modal-content">
              {loading ? (
                <div className="loading">Loading available locations...</div>
              ) : (
                <>
                  <div className="notice-box">
                    <p><strong>Note:</strong> Due to time constraints, only certain routes have been implemented. Please select from the available options below.</p>
                  </div>
                  
                  <h3>Available Locations ({locations.length})</h3>
                  <div className="locations-grid">
                    {/* Display all available locations in a grid */}
                    {locations.map(location => (
                      <div key={location.id || location.name} className="location-item">
                        {location.name}
                      </div>
                    ))}
                    
                    {/* Show a message if no locations are found */}
                    {locations.length === 0 && (
                      <div className="no-locations">
                        No available locations found.
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
            
            <div className="modal-footer">
              <button className="primary-button" onClick={() => setShowAvailableRoutes(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Styles for the error message and modal */}
      <style jsx>{`
        .error-container {
          background-color: #fef7f7;
          border: 1px solid #fddddd;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 24px;
        }
        
        .error-content {
          display: flex;
          align-items: flex-start;
        }
        
        .error-icon {
          color: #d93025;
          margin-right: 16px;
          flex-shrink: 0;
        }
        
        .error-message {
          flex: 1;
        }
        
        .error-message h3 {
          margin-top: 0;
          margin-bottom: 8px;
          color: #d93025;
        }
        
        .constraint-message {
          margin-top: 16px;
          font-style: italic;
        }
        
        .view-routes-button {
          background-color: #4285f4;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          font-weight: 500;
          margin-top: 16px;
          cursor: pointer;
        }
        
        /* Modal styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        
        .modal-container {
          background-color: white;
          border-radius: 8px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          border-bottom: 1px solid #eee;
        }
        
        .modal-content {
          padding: 24px;
          overflow-y: auto;
          flex: 1;
          max-height: 60vh;
        }
        
        .modal-footer {
          padding: 16px 24px;
          border-top: 1px solid #eee;
          display: flex;
          justify-content: flex-end;
        }
        
        .close-button {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #666;
        }
        
        .notice-box {
          background-color: #f8f9fa;
          border-left: 4px solid #4285f4;
          padding: 12px 16px;
          margin-bottom: 16px;
          border-radius: 4px;
        }
        
        .locations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 8px;
          margin-top: 12px;
        }
        
        .location-item {
          background-color: #f0f4f8;
          padding: 8px 12px;
          border-radius: 4px;
          font-size: 14px;
        }
        
        .no-locations {
          grid-column: 1 / -1;
          text-align: center;
          padding: 16px;
          color: #666;
        }
        
        .loading {
          text-align: center;
          padding: 24px;
          color: #666;
        }
        
        .primary-button {
          background-color: #4285f4;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default RouteErrorMessage;
