import React, { useState } from 'react';
import RouteForm from './components/RouteForm';
import ComparisonView from './components/ComparisonView';
import AlgorithmAnalysis from './components/AlgorithmAnalysis';
import RouteErrorMessage from './components/RouteErrorMessage';
import './App.css';
import './road-conditions.css';

function App() {
  const [routeResults, setRouteResults] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableLocations, setAvailableLocations] = useState([]);

  const handleRouteSubmit = async (routeData) => {
    console.log("User selected:", routeData);
    setLoading(true);
    setError(null);

    try {
      // Send route data to API to compare algorithms
      const response = await fetch("/api/compare-routes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(routeData),
      });

      const data = await response.json();

      if (!response.ok) {
        // If we get a formatted error from the server, use it
        if (data.error) {
          setError(data.error);
          if (data.available_locations) {
            setAvailableLocations(data.available_locations);
          }
        } else {
          throw new Error(`Error: ${response.statusText}`);
        }
        return;
      }

      console.log("Route comparison data:", data);
      
      setRouteResults(data);
      
      // Extract algorithm analysis data if available
      if (data.our_algorithm && data.our_algorithm.best_route && data.our_algorithm.best_route.analysis) {
        setAnalysisData({
          best: data.our_algorithm.best_route.analysis,
          alternative: data.our_algorithm.alternative_route?.analysis || null
        });
      } else {
        setAnalysisData(null);
      }
    } catch (error) {
      console.error("Error fetching route comparison:", error);
      setError(`Failed to get route comparison: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AofA Shortest Route Finder</h1>
        <p>Analysis of Algorithms Project - Finding the Optimal Delivery Routes in Jamaica</p>
      </header>

      <main className="app-content">
        <div className="form-container">
          <RouteForm onSubmit={handleRouteSubmit} loading={loading} />
        </div>

        {error && (
          <RouteErrorMessage error={error} availableLocations={availableLocations} />
        )}

        {loading && (
          <div className="loading-message">
            <p>Calculating optimal routes...</p>
          </div>
        )}

        {routeResults && !loading && (
          <div className="results-container">
            <ComparisonView routeResults={routeResults} />
            
            {analysisData && (
              <AlgorithmAnalysis analysisData={analysisData} />
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>University of Technology, Jamaica | Analysis of Algorithms (CIT3003) | 2024-2025</p>
      </footer>
    </div>
  );
}

export default App;