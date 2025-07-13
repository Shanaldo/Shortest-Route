/*
Names: Shanaldo Carty
Completion Date: 5/7/2025
*/

import React from 'react';

const AlgorithmAnalysis = ({ analysisData }) => {
  // Don't render anything if we don't have valid analysis data
  if (!analysisData || !analysisData.best) {
    return null;
  }
  
  // Extract data for the best route and alternative route (if available)
  const { best, alternative } = analysisData;
  
  return (
    <div className="analysis-container">
      <h2 className="analysis-title">Algorithm Performance Analysis</h2>
      
      {/* General algorithm information section */}
      <div className="algorithm-info">
        <p>
          <strong>Algorithm Used: </strong> 
          {best.algorithm}
        </p>
        
        {/* Display the algorithm description if available */}
        {best.algorithm_description && (
          <p className="algorithm-description">
            {best.algorithm_description}
          </p>
        )}
      </div>
      
      {/* Performance metrics for the best route */}
      <div className="analysis-metrics">
        {/* Execution Time metric card */}
        <div className="metric-card">
          <h3 className="metric-title">Execution Time</h3>
          <div className="metric-value">
            {best.execution_time_ms.toFixed(2)} ms
          </div>
          <div className="metric-note">
            Time taken to calculate the optimal route
          </div>
        </div>
        
        {/* Nodes Visited metric card - display only if available */}
        {best.nodes_visited !== undefined && (
          <div className="metric-card">
            <h3 className="metric-title">Nodes Visited</h3>
            <div className="metric-value">
              {best.nodes_visited}
            </div>
            <div className="metric-note">
              Number of towns processed during algorithm execution
            </div>
          </div>
        )}
        
        {/* Edge Relaxations metric card - display only if available */}
        {best.edge_relaxations !== undefined && (
          <div className="metric-card">
            <h3 className="metric-title">Edge Relaxations</h3>
            <div className="metric-value">
              {best.edge_relaxations}
            </div>
            <div className="metric-note">
              Number of road segments evaluated
            </div>
          </div>
        )}
        
        {/* Operations metric card - display only if available */}
        {best.operations !== undefined && (
          <div className="metric-card">
            <h3 className="metric-title">Operations</h3>
            <div className="metric-value">
              {best.operations}
            </div>
            <div className="metric-note">
              Total number of operations performed
            </div>
          </div>
        )}
      </div>
      
      {/* Alternative route analysis - shown only if available */}
      {alternative && (
        <div className="alternative-analysis">
          <h3>Alternative Route Analysis</h3>
          <div className="analysis-metrics">
            <div className="metric-card">
              <h3 className="metric-title">Execution Time</h3>
              <div className="metric-value">
                {alternative.execution_time_ms.toFixed(2)} ms
              </div>
            </div>
            
            {alternative.nodes_visited !== undefined && (
              <div className="metric-card">
                <h3 className="metric-title">Nodes Visited</h3>
                <div className="metric-value">
                  {alternative.nodes_visited}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Section explaining the theoretical complexity of the algorithm */}
      <div className="analysis-explanation">
        <h3>Algorithmic Complexity</h3>
        <p>
          <strong>Time Complexity: </strong>
          {best.time_complexity ? best.time_complexity : (
            // If the algorithm doesn't explicitly provide time complexity,
            // use known values for common algorithms
            <>
              {best.algorithm === "Dijkstra's Algorithm" && "O((V+E)log V)"}
              {best.algorithm === "Bellman-Ford" && "O(VE)"}
              {best.algorithm === "Floyd-Warshall" && "O(V³)"}
              {best.algorithm === "A* Search Algorithm" && "O(E) with a good heuristic"}
              {!["Dijkstra's Algorithm", "Bellman-Ford", "Floyd-Warshall", "A* Search Algorithm"].includes(best.algorithm) && "Not specified"}
            </>
          )}
        </p>
        <p>
          <strong>Space Complexity: </strong>
          {best.space_complexity ? best.space_complexity : (
            // If the algorithm doesn't explicitly provide space complexity,
            // use known values for common algorithms
            <>
              {best.algorithm === "Dijkstra's Algorithm" && "O(V)"}
              {best.algorithm === "Bellman-Ford" && "O(V)"}
              {best.algorithm === "Floyd-Warshall" && "O(V²)"}
              {best.algorithm === "A* Search Algorithm" && "O(V)"}
              {!["Dijkstra's Algorithm", "Bellman-Ford", "Floyd-Warshall", "A* Search Algorithm"].includes(best.algorithm) && "Not specified"}
            </>
          )}
        </p>
        <p className="complexity-note">
          Where V is the number of vertices (towns) and E is the number of edges (roads).
        </p>
      </div>
    </div>
  );
};

export default AlgorithmAnalysis;
