/*
Names: Shanaldo Carty
Completion Date: 5/7/2025
*/

import React, { useState, useEffect } from 'react';

const AvailableRoutesModal = ({ isOpen, onClose }) => {
  // State variables to manage the modal's data and UI states
  const [locations, setLocations] = useState([]); // List of available locations
  const [routes, setRoutes] = useState([]);      // List of available routes
  const [loading, setLoading] = useState(true);  // Whether data is currently loading
  const [error, setError] = useState(null);      // General error message
  const [detailedError, setDetailedError] = useState(null); // Technical error details
  const [showAllRoutes, setShowAllRoutes] = useState(false); // Whether to show all routes or just the first 20
  const [searchTerm, setSearchTerm] = useState(''); // Search filter for routes

  // Helper function to handle fetch responses consistently
  // This centralizes error handling for API requests
  const handleFetchResponse = async (response) => {
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
    }
    return response.json();
  };

  // Load data when the modal is opened
  useEffect(() => {
    // Only fetch data when the modal is open
    if (isOpen) {
      setLoading(true);
      setError(null);
      setDetailedError(null);
      
      // Define the API URLs - make sure these match your backend routes
      const locationsUrl = '/api/available-locations';
      const routesUrl = '/api/available-routes';

      // Fetch available locations
      const fetchLocations = fetch(locationsUrl)
        .then(handleFetchResponse)
        .then(data => {
          console.log('Locations data received:', data);
          setLocations(data.locations || []);
          return true;
        })
        .catch(err => {
          console.error('Failed to load available locations:', err);
          setDetailedError(`Locations API error: ${err.message}`);
          return false;
        });
        
      // Fetch available routes
      const fetchRoutes = fetch(routesUrl)
        .then(handleFetchResponse)
        .then(data => {
          console.log('Routes data received:', data);
          setRoutes(data.routes || []);
          return true;
        })
        .catch(err => {
          console.error('Failed to load available routes:', err);
          setDetailedError(prevError => 
            prevError ? `${prevError}\nRoutes API error: ${err.message}` : `Routes API error: ${err.message}`
          );
          return false;
        });
      
      // Wait for both fetches to complete
      Promise.all([fetchLocations, fetchRoutes])
        .then(results => {
          setLoading(false);
          const [locationsSucceeded, routesSucceeded] = results;
          if (!locationsSucceeded || !routesSucceeded) {
            setError('Failed to load some or all data. Check console for details.');
          }
        })
        .catch(err => {
          console.error('Error in Promise.all:', err);
          setLoading(false);
          setError('An unexpected error occurred. Check console for details.');
        });
    }
  }, [isOpen]); // Only run when the isOpen prop changes
  
  // Filter routes based on search term
  // This allows users to find specific routes easily
  const filteredRoutes = routes.filter(route => 
    route.display.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Display only first 20 routes unless "show all" is clicked
  // This keeps the UI manageable for users
  const displayedRoutes = showAllRoutes ? filteredRoutes : filteredRoutes.slice(0, 20);

  // If the modal is closed, render nothing
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2>Available Routes</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-content">
          {loading ? (
            <div className="loading">Loading available routes...</div>
          ) : error ? (
            <div className="error-container">
              <div className="error-message">{error}</div>
              {detailedError && (
                <div className="detailed-error">
                  <h4>Technical Details (for developers):</h4>
                  <pre>{detailedError}</pre>
                </div>
              )}
              <div className="troubleshooting-tips">
                <h4>Troubleshooting Tips:</h4>
                <ul>
                  <li>Ensure the backend server is running (check Python console)</li>
                  <li>Verify API endpoints are correct in both frontend and backend</li>
                  <li>Check network connection and for any CORS issues</li>
                  <li>Review server logs for any backend errors</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              {/* Notice about implementation status */}
              <div className="notice-box">
                <p><strong>Note:</strong> Due to time constraints, only certain routes have been implemented. Please select from the available options below.</p>
              </div>
              
              {/* Search box for filtering routes */}
              <div className="search-box">
                <input
                  type="text"
                  placeholder="Search routes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
              
              {/* Available locations section */}
              <div className="locations-section">
                <h3>Available Locations ({locations.length})</h3>
                {locations.length > 0 ? (
                  <div className="locations-grid">
                    {locations.map(location => (
                      <div key={location.id} className="location-item">
                        {location.name}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-data-message">No locations found.</div>
                )}
              </div>
              
              {/* Available routes section */}
              <div className="routes-section">
                <h3>Available Routes ({filteredRoutes.length})</h3>
                {filteredRoutes.length > 0 ? (
                  <div className="routes-list">
                    {displayedRoutes.map((route, index) => (
                      <div key={index} className="route-item">
                        {route.display}
                      </div>
                    ))}
                    
                    {/* "Show more" button if there are more than 20 routes */}
                    {filteredRoutes.length > 20 && !showAllRoutes && (
                      <button 
                        className="show-more-button"
                        onClick={() => setShowAllRoutes(true)}
                      >
                        Show all {filteredRoutes.length} routes
                      </button>
                    )}
                  </div>
                ) : searchTerm ? (
                  <div className="no-routes-found">
                    No routes found matching "{searchTerm}"
                  </div>
                ) : (
                  <div className="no-data-message">No routes available.</div>
                )}
              </div>
            </>
          )}
        </div>
        
        <div className="modal-footer">
          <button className="primary-button" onClick={onClose}>Close</button>
        </div>
      </div>
      
      {/* Styles for the modal */}
      <style jsx>{`
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
          max-width: 700px;
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
        
        .search-box {
          margin-bottom: 16px;
        }
        
        .search-input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
        }
        
        .locations-section, .routes-section {
          margin-bottom: 24px;
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
        
        .routes-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-top: 12px;
        }
        
        .route-item {
          background-color: #f0f4f8;
          padding: 8px 12px;
          border-radius: 4px;
          font-size: 14px;
        }
        
        .show-more-button {
          background-color: transparent;
          border: none;
          color: #4285f4;
          padding: 8px;
          margin-top: 8px;
          cursor: pointer;
          font-weight: 500;
          text-align: center;
        }
        
        .no-routes-found, .no-data-message {
          text-align: center;
          padding: 16px;
          color: #666;
          font-style: italic;
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
        
        .loading {
          text-align: center;
          padding: 24px;
          color: #666;
        }
        
        .error-container {
          background-color: #fef7f7;
          border: 1px solid #fddddd;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
        }
        
        .error-message {
          color: #d93025;
          font-weight: 500;
          margin-bottom: 12px;
        }
        
        .detailed-error {
          background-color: #f8f9fa;
          border-radius: 4px;
          padding: 12px;
          margin-bottom: 16px;
        }
        
        .detailed-error pre {
          white-space: pre-wrap;
          word-break: break-word;
          font-size: 12px;
          color: #5f6368;
        }
        
        .troubleshooting-tips {
          background-color: #f8f9fa;
          border-radius: 4px;
          padding: 12px;
        }
        
        .troubleshooting-tips h4 {
          margin-top: 0;
          margin-bottom: 8px;
          color: #202124;
        }
        
        .troubleshooting-tips ul {
          margin: 0;
          padding-left: 24px;
        }
        
        .troubleshooting-tips li {
          margin-bottom: 4px;
          color: #5f6368;
        }
      `}</style>
    </div>
  );
};

export default AvailableRoutesModal;
