import { eel } from './App';
import React, { useState, useEffect, useCallback, useRef, useLayoutEffect } from 'react';
import './IncidentSelection.css';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import * as d3 from 'd3';

const IncidentSelection = ({ onSelectionChange }) => {
  const [minDate, setMinDate] = useState('09/01/2017'); // Set initial minDate
  const [maxDate, setMaxDate] = useState('18/02/2017'); // Set initial maxDate
  const [startDate, setStartDate] = useState('01/06/2016'); // Set initial startDate
  const [endDate, setEndDate] = useState('01/07/2016'); // Set initial endDate
  const [incidentCount, setIncidentCount] = useState(null);
  const [totalIncidents, setTotalIncidents] = useState(null);

  const [editingStartDate, setEditingStartDate] = useState(false);
  const [editingEndDate, setEditingEndDate] = useState(false);

  const progressBarRef = useRef(); // Reference for the D3 progress bar

  const formatToDDMMYYYY = (dateStr) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  const formatDateToYYYYMMDD = (dateStr) => {
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month}-${day}`;
  };

  useEffect(() => {
    const fetchMinMaxDatesAndTotalIncidents = async () => {
      try {
        const [minDateFromBackend, maxDateFromBackend] = await eel.get_min_max_closed_date()();
        const formattedMinDate = formatToDDMMYYYY(minDateFromBackend);
        const formattedMaxDate = formatToDDMMYYYY(maxDateFromBackend);

        setMinDate(formattedMinDate); // Set fetched minDate from backend
        setMaxDate(formattedMaxDate); // Set fetched maxDate from backend

        const totalIncidentsFromBackend = await eel.count_unique_incidents()();
        setTotalIncidents(totalIncidentsFromBackend);

        // Fetch initial incident count for the specified date range
        const count = await eel.number_of_closed_incidents_in_time_period(startDate, endDate)();
        setIncidentCount(count);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchMinMaxDatesAndTotalIncidents();
  }, []);

  // Debounced function to fetch incident count
  const debouncedFetchIncidentCount = useCallback(
    debounce(async (startDate, endDate) => {
      try {
        const count = await eel.number_of_closed_incidents_in_time_period(startDate, endDate)();

        // Set filter values in 'YYYY-MM-DD' format
        await eel.set_filter_value('filters.overview_metrics.date_range.min_date', formatDateToYYYYMMDD(startDate));
        await eel.set_filter_value('filters.overview_metrics.date_range.max_date', formatDateToYYYYMMDD(endDate));

        setIncidentCount(count);
        onSelectionChange(); // Notify parent about the change
      } catch (error) {
        console.error('Error querying incidents:', error);
        setIncidentCount(null);
      }
    }, 500),
    []
  );

  useEffect(() => {
    if (startDate && endDate) {
      debouncedFetchIncidentCount(startDate, endDate);
    }
  }, [startDate, endDate, debouncedFetchIncidentCount]);

  const handleSliderChange = (value) => {
    const [newStartDate, newEndDate] = value.map((val) => formatDateToString(new Date(val)));
    setStartDate(newStartDate);
    setEndDate(newEndDate);
  };

  const handleDateInputChange = (setDate, setEditing, value) => {
    setDate(value);
    setEditing(false);
    onSelectionChange(); // Notify parent about the change
  };

  const formatDateToTimestamp = (dateStr) => {
    const [day, month, year] = dateStr.split('/');
    return new Date(`${year}-${month}-${day}`).getTime();
  };

  const formatDateToString = (date) => {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  const progressBarValue = incidentCount && totalIncidents ? (incidentCount / totalIncidents) * 100 : 0;

  // Render the D3 progress bar
  const renderProgressBar = () => {
    const container = d3.select(progressBarRef.current);
    const width = container.node().getBoundingClientRect().width;
    const height = 20;

    // If width or height is zero, skip rendering
    if (width === 0 || height === 0) {
      console.warn('Container dimensions are zero. Skipping progress bar rendering.');
      return;
    }

    container.selectAll('*').remove(); // Clear previous content

    const svg = container.append('svg').attr('width', width).attr('height', height);

    // Background rectangle
    svg
      .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', height)
      .attr('fill', '#e0e0e0');

    // Filled rectangle representing the progress
    svg
      .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', (progressBarValue / 100) * width)
      .attr('height', height)
      .attr('fill', 'steelblue');

    // Text label showing the incident count and percentage
    svg
      .append('text')
      .attr('x', width / 2)
      .attr('y', height / 2)
      .attr('dy', '.35em')
      .attr('text-anchor', 'middle')
      .attr('fill', '#000')
      .text(`Incidents: ${incidentCount} / ${totalIncidents} (${Math.round(progressBarValue)}%)`)
      .style('font-size', '14px');
  };

  useLayoutEffect(() => {
    if (incidentCount !== null && totalIncidents !== null) {
      renderProgressBar();
    }
  }, [incidentCount, totalIncidents]);

  return (
    <div className="incident-query-container">
      <div className="date-range-container">
        <Slider
          range
          min={formatDateToTimestamp(minDate)}
          max={formatDateToTimestamp(maxDate)}
          value={[formatDateToTimestamp(startDate), formatDateToTimestamp(endDate)]}
          onChange={handleSliderChange}
          className="date-range-slider"
        />
        <div className="date-range-labels">
          {editingStartDate ? (
            <input
              type="text"
              value={startDate}
              onChange={(e) => handleDateInputChange(setStartDate, setEditingStartDate, e.target.value)}
              onBlur={() => setEditingStartDate(false)}
              onKeyDown={(e) => e.key === 'Enter' && handleDateInputChange(setStartDate, setEditingStartDate, startDate)}
              className="date-input"
            />
          ) : (
            <span onClick={() => setEditingStartDate(true)} className="date-label">
              {startDate}
            </span>
          )}
          {editingEndDate ? (
            <input
              type="text"
              value={endDate}
              onChange={(e) => handleDateInputChange(setEndDate, setEditingEndDate, e.target.value)}
              onBlur={() => setEditingEndDate(false)}
              onKeyDown={(e) => e.key === 'Enter' && handleDateInputChange(setEndDate, setEditingEndDate, endDate)}
              className="date-input"
            />
          ) : (
            <span onClick={() => setEditingEndDate(true)} className="date-label">
              {endDate}
            </span>
          )}
        </div>
      </div>
      <div className="result-section">
        <div
          ref={progressBarRef}
          className="d3-progress-bar"
          style={{ width: '100%', minHeight: '20px', minWidth: '200px' }}
        ></div>
      </div>
    </div>
  );
};

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

export default IncidentSelection;
