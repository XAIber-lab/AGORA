import React, { useState, useEffect } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimeThresholds.css'; // Custom styles for the component
import { eel } from './App.js';

const TimeThresholds = () => {
  const [states, setStates] = useState([]);
  const [settings, setSettings] = useState({});

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const fetchedStates = await eel.get_pnml_states()(); // Fetch the states from backend
        setStates(fetchedStates);

        // Initialize settings for each state with default values
        const initialSettings = {};
        fetchedStates.forEach(state => {
          initialSettings[state] = {
            acceptableMax: 30,
            nonAcceptableMax: 120,
            deviations: { missing: 0, repetition: 0, mismatch: 0 }
          };
        });
        setSettings(initialSettings);
      } catch (error) {
        console.error('Failed to fetch states:', error);
      }
    };
    fetchStates();
  }, []);

  const handleSliderChange = (state, values) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      [state]: {
        ...prevSettings[state],
        acceptableMax: values[0],
        nonAcceptableMax: values[1]
      }
    }));
  };

  const handleDeviationChange = (state, type, value) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      [state]: {
        ...prevSettings[state],
        deviations: {
          ...prevSettings[state].deviations,
          [type]: value
        }
      }
    }));
  };

  const saveSettingsToBackend = async () => {
    // Placeholder function to send data to the backend
    console.log('This function will save the settings to the backend:', settings);
    // Here you can use eel to send the `settings` object to the backend
    // Example: await eel.set_state_time_settings(stateName, settings[stateName])();
  };

  return (
    <div className="time-thresholds-container">
      <div className="settings-name">TIME THRESHOLDS</div>
      {states.map((state) => (
        <div key={state} className="state-settings">
          <div className="settings-name">{state} Time Settings</div>
          <div className="slider-container">
            <Slider
              range
              min={0}
              max={240}
              step={1}
              value={[
                settings[state]?.acceptableMax || 30,
                settings[state]?.nonAcceptableMax || 120
              ]}
              onChange={(values) => handleSliderChange(state, values)}
              marks={{
                [settings[state]?.acceptableMax || 30]: `${settings[state]?.acceptableMax || 30} min`,
                [settings[state]?.nonAcceptableMax || 120]: `${settings[state]?.nonAcceptableMax || 120} min`
              }}
              trackStyle={[
                { backgroundColor: 'green' }, // Min to Acceptable Max
                { backgroundColor: 'orange' }, // Acceptable Min to Acceptable Max
                { backgroundColor: 'red' } // Acceptable Max to Non-Acceptable Max
              ]}
              railStyle={{ backgroundColor: 'lightgrey' }}
            />
          </div>
          <div className="deviation-settings">
            <div className="settings-name">Acceptable Deviations</div>
            <div className="deviation-row">
              <div className="deviation-item">
                <label>
                  Missing:
                  <input
                    type="number"
                    value={settings[state]?.deviations?.missing || 0}
                    onChange={(e) => handleDeviationChange(state, 'missing', Number(e.target.value))}
                  />
                </label>
              </div>
              <div className="deviation-item">
                <label>
                  Repetition:
                  <input
                    type="number"
                    value={settings[state]?.deviations?.repetition || 0}
                    onChange={(e) => handleDeviationChange(state, 'repetition', Number(e.target.value))}
                  />
                </label>
              </div>
              <div className="deviation-item">
                <label>
                  Mismatch:
                  <input
                    type="number"
                    value={settings[state]?.deviations?.mismatch || 0}
                    onChange={(e) => handleDeviationChange(state, 'mismatch', Number(e.target.value))}
                  />
                </label>
              </div>
            </div>
          </div>
        </div>
      ))}
      <button className="save-button" onClick={saveSettingsToBackend}>Save All Settings</button>
    </div>
  );
};

export default TimeThresholds;
