import React, { useState, useEffect } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './ThresholdSlider.css';
import { eel } from './App.js';

const ThresholdSlider = ({ onSettingsChange }) => {
  // Initialize thresholds with default values
  const [thresholds, setThresholds] = useState([0, 0.25, 0.5, 0.75, 1]);
  const [selectedMetric, setSelectedMetric] = useState('fitness');

  // Use useEffect to asynchronously fetch the initial thresholds
  useEffect(() => {
    const fetchThresholds = async () => {
      const fetchedThresholds = JSON.parse(await eel.get_compliance_metric_thresholds()());
      
      // Map the JSON structure to an array of threshold values
      const thresholdArray = [
        fetchedThresholds.critical[0],
        fetchedThresholds.critical[1],
        fetchedThresholds.moderate[1],
        fetchedThresholds.high[1],
        fetchedThresholds.low[1]
      ];

      setThresholds(thresholdArray);
    };
    fetchThresholds();
  }, []); // Empty dependency array ensures this runs once when the component is mounted

  const handleSliderChange = (newThresholds) => {
    setThresholds(newThresholds);
    onSettingsChange(); // Pass the new values back to the parent component
  };

  const handleMetricChange = (e) => {
    const metric = e.target.value;
    setSelectedMetric(metric);
    eel.set_incident_compliance_metric(metric)();
    eel.set_filter_value('filters.compliance_metric', metric);
    onSettingsChange();
    console.log(`Selected metric: ${metric}`);
  };

  // Send thresholds to backend when the user is done moving the slider
  const handleAfterChange = async (newThresholds) => {
    // Map the array of threshold values back into the JSON format
    const thresholdsJSON = {
      critical: [newThresholds[0], newThresholds[1]],
      moderate: [newThresholds[1], newThresholds[2]],
      high: [newThresholds[2], newThresholds[3]],
      low: [newThresholds[3], newThresholds[4]]
    };

    // Save to backend using the existing method
    await eel.set_compliance_metric_thresholds(JSON.stringify(thresholdsJSON))();

    // Update the assessment_filters in the backend
    await eel.set_filter_value("filters.thresholds.compliance_metric_severity_levels.critical", `>= ${newThresholds[0]} AND <= ${newThresholds[1]}`)();
    await eel.set_filter_value("filters.thresholds.compliance_metric_severity_levels.high", ` > ${newThresholds[1]} AND <= ${newThresholds[2]}`)();
    await eel.set_filter_value("filters.thresholds.compliance_metric_severity_levels.moderate", `> ${newThresholds[2]} AND <= ${newThresholds[3]}`)();
    await eel.set_filter_value("filters.thresholds.compliance_metric_severity_levels.low", `> ${newThresholds[3]} AND <= ${newThresholds[4]}`)();

    console.log("Saved thresholds to assessment_filters:", thresholdsJSON);
  };

  return (
    <div>
      <div className="settings-name">COMPLIANCE METRIC</div>
      {/* Dropdown for metric selection */}
      <div className="metric-container">
        <label htmlFor="metric-select" className="metric-label">Select Metric:</label>
        <select
          id="metric-select"
          value={selectedMetric}
          onChange={handleMetricChange}
          className="metric-dropdown"
        >
          <option value="fitness">Fitness</option>
          <option value="cost">Non-Compliance Cost</option>
        </select>
      </div>

      {/* Slider for thresholds */}
      <div className="threshold-slider-container">
        <div className="threshold-labels">
          <div>Critical</div>
          <div>High</div>
          <div>Moderate</div>
          <div>Low</div>
        </div>

        <div className="slider-row">
          <Slider
            range
            min={0}
            max={1}
            step={0.01}
            value={thresholds}
            onChange={handleSliderChange}    // Update the state during dragging
            onAfterChange={handleAfterChange} // Save to backend after user stops adjusting
            marks={{
              [thresholds[0]]: thresholds[0].toFixed(2),
              [thresholds[1]]: thresholds[1].toFixed(2),
              [thresholds[2]]: thresholds[2].toFixed(2), 
              [thresholds[3]]: thresholds[3].toFixed(2),
              [thresholds[4]]: thresholds[4].toFixed(2)
            }}
            trackStyle={[
              { backgroundColor: 'purple' },  // Critical range
              { backgroundColor: 'red' }, // High range
              { backgroundColor: 'orange' },    // Moderate range
              { backgroundColor: 'green' } // Low range
            ]}
            railStyle={{ backgroundColor: 'lightgrey' }} // Style the rail
          />
        </div>
      </div>
    </div>
  );
};

export default ThresholdSlider;
