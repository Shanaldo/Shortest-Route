/*
Names: Shanaldo Carty, Rachjae Gayle, Shanice Burrell, Rajaire Thomas
ID#: 2108949, 2100400, 2202903, 2207216
Completion Date: 4/4/2025
*/

import React, { useState, useEffect } from 'react';
import AvailableRoutesModal from './AvailableRoutesModal';

const RouteForm = ({ onSubmit, loading }) => {
  // Set up state variables to track form values and UI state
  const [source, setSource] = useState('');               // Starting location input
  const [destination, setDestination] = useState('');     // Destination input
  const [preference, setPreference] = useState('fastest'); // Route preference (fastest or shortest)
  const [options, setOptions] = useState({                // Avoidance options
    tolls: false,
    highways: false,
    hillyRoads: false,
    innerCity: false,
  });
  
  // UI state for showing available routes and autocomplete
  const [showAvailableRoutes, setShowAvailableRoutes] = useState(false);
  const [availableLocations, setAvailableLocations] = useState([]);
  const [sourceOptions, setSourceOptions] = useState([]);      // Autocomplete options for source
  const [destOptions, setDestOptions] = useState([]);          // Autocomplete options for destination
  const [sourceInputFocused, setSourceInputFocused] = useState(false);
  const [destInputFocused, setDestInputFocused] = useState(false);

  // When the component first loads, fetch the list of available locations
  // This will be used for autocomplete suggestions
  useEffect(() => {
    fetch('/api/available-locations')
      .then(response => response.json())
      .then(data => {
        setAvailableLocations(data.locations || []);
      })
      .catch(err => {
        console.error('Failed to load available locations', err);
      });
  }, []);
  
  // Update source location suggestions when user types in the source field
  useEffect(() => {
    if (source) {
      // Filter locations that match what the user has typed
      const filtered = availableLocations.filter(loc => 
        loc.name.toLowerCase().includes(source.toLowerCase())
      );
      setSourceOptions(filtered.slice(0, 5)); // Limit to 5 suggestions for clean UI
    } else {
      setSourceOptions([]);
    }
  }, [source, availableLocations]);
  
  // Update destination location suggestions when user types in the destination field
  useEffect(() => {
    if (destination) {
      // Filter locations that match what the user has typed
      const filtered = availableLocations.filter(loc => 
        loc.name.toLowerCase().includes(destination.toLowerCase())
      );
      setDestOptions(filtered.slice(0, 5)); // Limit to 5 suggestions
    } else {
      setDestOptions([]);
    }
  }, [destination, availableLocations]);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent the browser from refreshing the page
    
    // Validate that both source and destination are filled in
    if (!source || !destination) {
      alert("Please enter both source and destination locations.");
      return;
    }
    
    // Validate that source and destination are not the same
    if (source === destination) {
      alert("Source and destination cannot be the same location.");
      return;
    }
    
    // Create data object to send to the parent component
    const requestData = {
      source,
      destination,
      preference,
      options: {
        tolls: options.tolls,
        highways: options.highways,
        hillyRoads: options.hillyRoads,
        innerCity: options.innerCity,
      }
    };
    
    // Call the onSubmit function passed from the parent component
    onSubmit(requestData);
  };

  // Handle checkbox changes for the avoidance options
  const handleOptionChange = (option) => {
    setOptions(prev => ({
      ...prev,
      [option]: !prev[option]  // Toggle the checked state
    }));
  };
  
  // Handle selecting a location from the autocomplete dropdown for source
  const selectSourceLocation = (location) => {
    setSource(location.name);
    setSourceOptions([]);  // Clear suggestions after selection
  };
  
  // Handle selecting a location from the autocomplete dropdown for destination
  const selectDestLocation = (location) => {
    setDestination(location.name);
    setDestOptions([]);  // Clear suggestions after selection
  };

  return (
    <>
      {/* Main form */}
      <form className="route-form" onSubmit={handleSubmit}>
        <h2>Find the Best Route</h2>
        
        {/* Notice about available routes */}
        <div className="notice-box">
          <p>
            <strong>Note:</strong> Due to time constraints, only certain routes have been implemented.
            <button 
              type="button" 
              className="view-routes-button"
              onClick={() => setShowAvailableRoutes(true)}
            >
              View available routes
            </button>
          </p>
        </div>
        
        {/* Source location input with autocomplete */}
        <div className="input-group">
          <label htmlFor="source">Starting Point (Source):</label>
          <div className="autocomplete-container">
            <input 
              type="text"
              id="source" 
              value={source} 
              onChange={(e) => setSource(e.target.value)}
              onFocus={() => setSourceInputFocused(true)}
              onBlur={() => setTimeout(() => setSourceInputFocused(false), 200)}
              placeholder="Enter starting location in Jamaica"
              required
            />
            {/* Show autocomplete dropdown when input is focused and there are options */}
            {sourceInputFocused && sourceOptions.length > 0 && (
              <div className="autocomplete-dropdown">
                {sourceOptions.map(location => (
                  <div 
                    key={location.id} 
                    className="autocomplete-item"
                    onClick={() => selectSourceLocation(location)}
                  >
                    {location.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Destination location input with autocomplete */}
        <div className="input-group">
          <label htmlFor="destination">Ending Point (Destination):</label>
          <div className="autocomplete-container">
            <input 
              type="text"
              id="destination" 
              value={destination} 
              onChange={(e) => setDestination(e.target.value)}
              onFocus={() => setDestInputFocused(true)}
              onBlur={() => setTimeout(() => setDestInputFocused(false), 200)}
              placeholder="Enter destination in Jamaica"
              required
            />
            {/* Show autocomplete dropdown when input is focused and there are options */}
            {destInputFocused && destOptions.length > 0 && (
              <div className="autocomplete-dropdown">
                {destOptions.map(location => (
                  <div 
                    key={location.id} 
                    className="autocomplete-item"
                    onClick={() => selectDestLocation(location)}
                  >
                    {location.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Route preference selection */}
        <div className="input-group">
          <label htmlFor="preference">Route Preference:</label>
          <select 
            id="preference" 
            value={preference} 
            onChange={(e) => setPreference(e.target.value)}
          >
            <option value="fastest">Fastest Route (Least Time)</option>
            <option value="shortest">Shortest Route (Least Distance)</option>
          </select>
        </div>
        
        {/* Empty column for grid layout */}
        <div className="input-group"></div>
        
        {/* Route avoidance options */}
        <div className="preferences-group">
          <h3>Route Preferences:</h3>
          <div className="checkbox-group">
            <div className="checkbox-item">
              <input 
                type="checkbox" 
                id="avoid-tolls" 
                checked={options.tolls} 
                onChange={() => handleOptionChange('tolls')} 
              />
              <label htmlFor="avoid-tolls">Avoid Toll Roads</label>
            </div>
            
            <div className="checkbox-item">
              <input 
                type="checkbox" 
                id="avoid-highways" 
                checked={options.highways} 
                onChange={() => handleOptionChange('highways')} 
              />
              <label htmlFor="avoid-highways">Avoid Highways</label>
            </div>
            
            <div className="checkbox-item">
              <input 
                type="checkbox" 
                id="avoid-hilly-roads" 
                checked={options.hillyRoads} 
                onChange={() => handleOptionChange('hillyRoads')} 
              />
              <label htmlFor="avoid-hilly-roads">Avoid Hilly Roads</label>
            </div>
            
            <div className="checkbox-item">
              <input 
                type="checkbox" 
                id="avoid-inner-city" 
                checked={options.innerCity} 
                onChange={() => handleOptionChange('innerCity')} 
              />
              <label htmlFor="avoid-inner-city">Avoid Inner-City Roads</label>
            </div>
          </div>
        </div>
        
        {/* Submit button */}
        <button 
          type="submit" 
          className="submit-button" 
          disabled={loading || !source || !destination}  // Disable if loading or inputs are empty
        >
          {loading ? "Calculating Routes..." : "Find Routes"}
        </button>
      </form>
      
      {/* Modal to show available routes (separate component) */}
      <AvailableRoutesModal 
        isOpen={showAvailableRoutes} 
        onClose={() => setShowAvailableRoutes(false)} 
      />
      
      {/* Styles for the form */}
      <style jsx>{`
        .route-form {
          background-color: white;
          padding: 24px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          max-width: 800px;
          margin: 0 auto;
        }
        
        .notice-box {
          background-color: #f8f9fa;
          border-left: 4px solid #4285f4;
          padding: 12px 16px;
          margin-bottom: 20px;
          border-radius: 4px;
          display: flex;
          align-items: center;
        }
        
        .view-routes-button {
          background: none;
          border: none;
          color: #4285f4;
          font-weight: 500;
          margin-left: 8px;
          cursor: pointer;
          text-decoration: underline;
        }
        
        .input-group {
          margin-bottom: 16px;
        }
        
        .autocomplete-container {
          position: relative;
        }
        
        .autocomplete-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background-color: white;
          border: 1px solid #ddd;
          border-radius: 0 0 4px 4px;
          z-index: 10;
          max-height: 200px;
          overflow-y: auto;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .autocomplete-item {
          padding: 8px 12px;
          cursor: pointer;
        }
        
        .autocomplete-item:hover {
          background-color: #f0f4f8;
        }
        
        /* Keep the rest of your existing styles */
      `}</style>
    </>
  );
};

export default RouteForm;