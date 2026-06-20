import React, { useEffect, useState } from 'react';
import { eel } from './App'; // Assuming eel is set up in your App
import './ProcessIndicatorsVisualization.css'; // Custom CSS for layout and styling
import Collapsible from 'react-collapsible';
import ProcessStateTimes from './ProcessStateTimes';
import ProcessComplianceBarChart from './ProcessComplianceBarChart';
import DeviationsBarChart from './DeviationsBarChart';

const ProcessIndicatorsVisualization = ({ refreshTrigger }) => {
  const [statesData, setStatesData] = useState([]);

  useEffect(() => {
    // Fetch state mapping, deviations, and durations
    const fetchData = async () => {
      try {
        // Fetch state mapping from eel
        const states = await eel.read_mapping_from_file()();
        const deviations = await eel.count_frequencies()();
        const durations = await eel.get_average_state_times()();

        // Calculate deviations and durations for each state
        const statesArray = Object.keys(states).map(state => {
          const stateId = states[state];
          
          // Sum deviations (missing, repetition, mismatch) for each state
          const totalDeviations = 
            deviations.missing[stateId] +
            deviations.repetition[stateId] +
            deviations.mismatch[stateId];

          // Get the corresponding duration for each state
          const duration = durations[stateId] || '0h'; // Fallback to '0h' if not available

          return {
            state,
            deviations: totalDeviations,
            durations: duration,
            comp: Math.floor(Math.random() * 100) + 1 // Simulated compliance percentage
          };
        });

        setStatesData(statesArray);
      } catch (error) {
        console.error("Error fetching states data from eel:", error);
      }
    };

    fetchData();
  }, [refreshTrigger]);

  return (
    <div className="visualization-wrapper">
      {/* Right column with values */}
      <div className="layer-values">
        
        {/* DEVIATIONS Row */}
        <Collapsible
          trigger={[<div className="layer-row full-width-trigger">
            {statesData.map((state, i) => (
              <div className="state-column" key={`deviations-${i}`}>
                {state.deviations}
              </div>
            ))}
          </div>]}>
          <DeviationsBarChart height={80} refreshTrigger={refreshTrigger} />
        </Collapsible>

        {/* DURATIONS Row */}
        <Collapsible
          trigger={[
            <div className="layer-row full-width-trigger">
              {statesData.map((state, i) => (
                <div className="state-column" key={`durations-${i}`}>
                  {state.durations}
                </div>
              ))}
            </div>]}>
          <ProcessStateTimes height={200} refreshTrigger={refreshTrigger} />
        </Collapsible>

        {/* COMP Row */}
        <Collapsible
          trigger={[
            <div className="layer-row full-width-trigger">
              {statesData.map((state, i) => (
                <div className="state-column" key={`comp-${i}`}>
                  {state.comp}
                </div>
              ))}
            </div>]}>
          <ProcessComplianceBarChart height={100} refreshTrigger={refreshTrigger} />
        </Collapsible>
      </div>
    </div>
  );
};

export default ProcessIndicatorsVisualization;
