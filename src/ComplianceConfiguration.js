import React, { useEffect, useState } from 'react';
import './ComplianceConfiguration.css';

// Access eel exposed in window (App exports eel as window.eel)
const eel = window.eel;

const ActivityList = ['detection', 'activation', 'awaiting', 'resolution', 'closure'];

const ComplianceConfiguration = ({ refreshTrigger }) => {
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [complianceMetric, setComplianceMetric] = useState('fitness');
  const [complianceThresholds, setComplianceThresholds] = useState({});
  const [editingCostFunction, setEditingCostFunction] = useState(false);
  const [costFunctionJson, setCostFunctionJson] = useState('');
  // Severity levels state for the form
  const [severityLevels, setSeverityLevels] = useState({ low: '', moderate: '', high: '', critical: '' });

  // Sync severityLevels state with filters and complianceMetric
  useEffect(() => {
    const levels = (filters.thresholds && filters.thresholds.compliance_metric_severity_levels2 && filters.thresholds.compliance_metric_severity_levels2[complianceMetric]) || {};
    setSeverityLevels({
      low: levels.low || '',
      moderate: levels.moderate || '',
      high: levels.high || '',
      critical: levels.critical || ''
    });
  }, [complianceMetric, filters.thresholds]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const allFilters = await eel.get_filter_value()();
        setFilters(allFilters.filters || {});

        const metric = await eel.get_filter_value('filters.compliance_metric')();
        setComplianceMetric(metric);

        const thresholdsStr = await eel.get_compliance_metric_thresholds()();
        try {
          setComplianceThresholds(JSON.parse(thresholdsStr));
        } catch (e) {
          setComplianceThresholds(thresholdsStr || {});
        }

        // Prepopulate cost function editor if available
        if (allFilters && allFilters.filters && allFilters.filters.cost_function) {
          setCostFunctionJson(JSON.stringify(allFilters.filters.cost_function, null, 2));
        }
      } catch (err) {
        console.error('Failed to load filter/config values', err);
      }
      setLoading(false);
    };

    load();
  }, [refreshTrigger]);

  const onMetricChange = async (e) => {
    const val = e.target.value;
    setComplianceMetric(val);
    try {
        await eel.set_filter_value('filters.compliance_metric', val)();
    } catch (err) {
      console.error('Failed to set incident compliance metric', err);
    }
  };

  const saveCostFunction = async () => {
    try {
      const parsed = JSON.parse(costFunctionJson);
      // Send the parsed object directly, not as a string
      await eel.set_filter_value('filters.cost_function', parsed)();
      // Call backend to update cost with compliance per state
      await eel.update_cost_with_compliance_per_state()();
      setEditingCostFunction(false);
      // refresh local copy
      const allFilters = await eel.get_filter_value()();
      setFilters(allFilters.filters || {});
    } catch (err) {
      alert('Invalid JSON: ' + err.message);
    }
  };

  const toggleSeverityFilter = async (metricName, rangeStart, rangeEnd) => {
    try {
      await eel.set_filter_compliance_metric_thresholds(metricName, rangeStart, rangeEnd)();
      const allFilters = await eel.get_filter_value()();
      setFilters(allFilters.filters || {});
    } catch (err) {
      console.error('Failed toggling severity filter', err);
    }
  };

  const updateThreshold = async (path, value) => {
    try {
      // we set the raw value (string) into the nested path
      await eel.set_filter_value(path, value)();
      const allFilters = await eel.get_filter_value()();
      setFilters(allFilters.filters || {});
    } catch (err) {
      console.error('Failed to set filter value', err);
    }
  };

  return (
    <div className="compliance-config-container">
      <h2>Compliance Configuration</h2>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <div className="top-row">
            <div className="tile" style={{ flex: '0 1 320px' }}>
              <h3>Applied Compliance Metric</h3>
              <select value={complianceMetric} onChange={onMetricChange}>
                <option value="fitness">fitness</option>
                <option value="cost">cost</option>
              </select>
              <p className="muted">Currently applied metric used across analyses.</p>
              {complianceMetric === 'fitness' && (
                <p className="muted" style={{ marginTop: 4 }}>
                  <strong>Fitness:</strong> Measures how closely the observed process matches the reference model, penalizing any type of deviations equally.
                </p>
              )}
              {complianceMetric === 'cost' && (
                <p className="muted" style={{ marginTop: 4 }}>
                  <strong>Cost:</strong> Evaluates an incidents compliance based on a customizable cost function, allowing weighted penalties for different process activities and cost assignments for per devation type.
                </p>
              )}
            </div>

            {/* Severity Levels Tile */}
            <div className="tile" style={{ flex: '0 1 340px' }}>
              <h3>Set Severity Levels ({complianceMetric})</h3>
              <form
                onSubmit={async e => {
                  e.preventDefault();
                  // Only update the selected compliance metric's severity levels
                  await eel.set_filter_value(
                    `filters.thresholds.compliance_metric_severity_levels2.${complianceMetric}`,
                    severityLevels
                  )();
                  // Refresh local state
                  const allFilters = await eel.get_filter_value()();
                  setFilters(allFilters.filters || {});
                }}
              >
                {['low', 'moderate', 'high', 'critical'].map(level => (
                  <div key={level} style={{ marginBottom: 8 }}>
                    <label style={{ fontWeight: 500, marginRight: 8 }}>{level.charAt(0).toUpperCase() + level.slice(1)}:</label>
                    <input
                      type="text"
                      value={severityLevels[level] || ''}
                      onChange={e => setSeverityLevels({ ...severityLevels, [level]: e.target.value })}
                      style={{ width: '70%', padding: '4px', fontSize: '14px', borderRadius: '4px', border: '1px solid #ccc' }}
                    />
                  </div>
                ))}
                <button type="submit" style={{ marginTop: 8 }}>Save Severity Levels</button>
              </form>
              <p className="muted">Set the severity level ranges for the selected compliance metric.</p>
            </div>

            {complianceMetric === 'cost' && (
              <div className="tile large" style={{ flex: '1 1 260px' }}>
                <h3>Cost Function (JSON)</h3>
                <textarea
                  className="json-editor"
                  value={costFunctionJson}
                  onChange={(e) => setCostFunctionJson(e.target.value)}
                  rows={12}
                />
                <div style={{ marginTop: 8 }}>
                  <button onClick={saveCostFunction}>Save Cost Function</button>
                  <button onClick={() => setEditingCostFunction(false)} style={{ marginLeft: 8 }}>Cancel</button>
                </div>
                <p className="muted">Edit the cost function JSON used when <strong>cost</strong> metric is selected.</p>
              </div>
            )}
          </div>

          <div className="bottom-row">
            {ActivityList.map((activity) => (
              <div className="tile" key={activity}>
                <h3>{activity.charAt(0).toUpperCase() + activity.slice(1)}</h3>

                <div className="sub-header">Time Duration Thresholds</div>
                <div className="field">
                  <label>acceptableTime</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].acceptableTime) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.acceptableTime`, e.target.value)}
                  />
                </div>
                <div className="field">
                  <label>nonAcceptableTime</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].nonAcceptableTime) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.nonAcceptableTime`, e.target.value)}
                  />
                </div>

                <div className="sub-header">Deviation Type Thresholds</div>
                <div className="field">
                  <label>acceptableMissing</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].deviations && filters.thresholds[activity].deviations.acceptableMissing) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.deviations.acceptableMissing`, e.target.value)}
                  />
                </div>
                <div className="field">
                  <label>acceptableRepetition</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].deviations && filters.thresholds[activity].deviations.acceptableRepetition) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.deviations.acceptableRepetition`, e.target.value)}
                  />
                </div>
                <div className="field">
                  <label>acceptableMismatch</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].deviations && filters.thresholds[activity].deviations.acceptableMismatch) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.deviations.acceptableMismatch`, e.target.value)}
                  />
                </div>

                <div className="sub-header">Compliance Metric Thresholds</div>
                <div className="field">
                  <label>acceptableCompliance (fitness)</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].fitness && filters.thresholds[activity].fitness.acceptableCompliance) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.fitness.acceptableCompliance`, e.target.value)}
                  />
                </div>

                <div className="field">
                  <label>acceptableCompliance (cost)</label>
                  <input
                    type="text"
                    defaultValue={(filters.thresholds && filters.thresholds[activity] && filters.thresholds[activity].cost && filters.thresholds[activity].cost.acceptableCompliance) || ''}
                    onBlur={(e) => updateThreshold(`filters.thresholds.${activity}.cost.acceptableCompliance`, e.target.value)}
                  />
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default ComplianceConfiguration;
