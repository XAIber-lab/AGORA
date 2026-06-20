import React, { useEffect, useState, useRef } from 'react';
import * as d3 from 'd3';
import { eel } from './App';

const DeviationsBarChart = ({ height, globalFilterTrigger, refreshTrigger }) => {
  const containerRef = useRef();
  const [deviationData, setDeviationData] = useState([]);
  const [selectedFilters, setSelectedFilters] = useState({
    missing: [],
    repetition: [],
    mismatch: [],
  }); // To track selected states for each deviation type

  // Function to fetch state mapping, deviations data, and assessment filters
  const fetchStateMapping = async () => {
    try {
      const stateMapping = await eel.read_mapping_from_file()(); // Fetch state mapping
      const deviations = await eel.count_frequencies()(); // Fetch deviations data
      const filters = await eel.get_filter_value('filters')();
      const assessmentFilters = filters.thresholds;

      // Process the data to fit the required structure
      const statesArray = Object.keys(stateMapping).map((state) => {
        const stateId = stateMapping[state];
        const missing = deviations.missing[stateId] || 0;
        const repetition = deviations.repetition[stateId] || 0;
        const mismatch = deviations.mismatch[stateId] || 0;

        // Get acceptable thresholds for the state and deviation type
        const acceptableMissing = parseInt(assessmentFilters[state].deviations.acceptableMissing.replace('<=', ''), 10);
        const acceptableRepetition = parseInt(assessmentFilters[state].deviations.acceptableRepetition.replace('<=', ''), 10);
        const acceptableMismatch = parseInt(assessmentFilters[state].deviations.acceptableMismatch.replace('<=', ''), 10);

        // Determine if deviations exceed thresholds
        const missingExceeds = missing > acceptableMissing;
        const repetitionExceeds = repetition > acceptableRepetition;
        const mismatchExceeds = mismatch > acceptableMismatch;

        return {
          stateName: stateId,
          deviations: {
            MISSING: missing,
            REPETITION: repetition,
            MISMATCH: mismatch,
          },
          exceedsThreshold: {
            MISSING: missingExceeds,
            REPETITION: repetitionExceeds,
            MISMATCH: mismatchExceeds,
          },
          totalDeviations: missing + repetition + mismatch, // Store the sum of deviations
        };
      });

      setDeviationData(statesArray);
    } catch (error) {
      console.error('Error fetching state mapping or assessment filters:', error);
    }
  };

  // Function to handle the click event on a bar
  const handleBarClick = async (stateName, deviationType) => {
    const deviationKey = deviationType.toLowerCase();
    const currentFilter = selectedFilters[deviationKey];
    let updatedFilter;

    if (currentFilter.includes(stateName)) {
      // If state is already selected, remove it from the filter array
      updatedFilter = currentFilter.filter((item) => item !== stateName);
    } else {
      // If state is not selected, add it to the filter array
      updatedFilter = [...currentFilter, stateName];
    }

    // Update the selected filters state
    setSelectedFilters((prevState) => ({
      ...prevState,
      [deviationKey]: updatedFilter,
    }));

    // Update the filter value in the backend
    try {
      await eel.set_filter_value(`filters.deviations_distribution.${deviationKey}`, updatedFilter);
      globalFilterTrigger();
      console.log(`Set filter filters.deviations_distribution.${deviationKey} to ${JSON.stringify(updatedFilter)}`);
    } catch (error) {
      console.error(`Failed to set filter for filters.deviations_distribution.${deviationKey}:`, error);
    }
  };

  // Function to render bar chart for a single state
  const renderBarChart = (data, width, height, container) => {
    const paddingTop = 20; // Padding above the chart for visibility of counts
    const paddingBottom = 5;
    const svgHeight = height + paddingTop + paddingBottom; // Increase the total SVG height

    const svg = d3.select(container).append('svg').attr('width', width).attr('height', svgHeight);

    // X and Y scales
    const xScale = d3
      .scaleBand()
      .domain(['MISSING', 'REPETITION', 'MISMATCH'])
      .range([0, width])
      .paddingOuter(1);

    const yScale = d3.scaleLinear().domain([0, data.totalDeviations]).range([height, paddingTop]); // Adjust range

    // Create bars
    svg
      .selectAll('rect')
      .data(Object.entries(data.deviations))
      .enter()
      .append('rect')
      .attr('x', (d) => xScale(d[0]))
      .attr('y', (d) => yScale(d[1]))
      .attr('width', xScale.bandwidth())
      .attr('height', (d) => height - yScale(d[1]))
      .attr('fill', (d) => {
        const deviationType = d[0];
        const exceedsThreshold = data.exceedsThreshold[deviationType];
        return exceedsThreshold ? 'red' : 'green'; // Set color based on threshold comparison
      })
      .attr('stroke', (d) => (selectedFilters[d[0].toLowerCase()].includes(data.stateName) ? 'blue' : 'none')) // Add blue stroke if selected
      .attr('stroke-width', 2)
      .style('cursor', 'pointer') // Indicate that bars are clickable
      .on('click', (event, d) => {
        // Call the handleBarClick function with state name and deviation type
        handleBarClick(data.stateName, d[0]);
      });

    // Add text for each bar to show the number of deviations
    svg
      .selectAll('text')
      .data(Object.entries(data.deviations))
      .enter()
      .append('text')
      .attr('x', (d) => xScale(d[0]) + xScale.bandwidth() / 2) // Center text in the bar
      .attr('y', (d) => yScale(d[1]) - 5) // Position above the bar
      .attr('text-anchor', 'middle')
      .attr('fill', 'white') // Text color
      .style('font-size', '10px') // Font size
      .text((d) => d[1]); // Display the deviation value

    // Add X-axis with ticks and labels but hide the axis line
    const xAxis = svg
      .append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(xScale).tickSize(0));

    // Remove the X-axis line but keep the ticks and labels
    xAxis.select('path').remove();

    // Style and adjust the labels
    xAxis
      .selectAll('.tick text')
      .attr('fill', 'white')
      .style('font-size', '8px')
      .attr('dx', (d, i) => {
        if (i === 0) return '-1em'; // Adjust for spacing
        if (i === 2) return '1em';
      })
      .attr('dy', (d, i) => {
        if (i === 1) return '2em'; // Lower middle label
        return '1em';
      });

    // Remove the tick lines
    xAxis.selectAll('.tick line').remove();
  };

  useEffect(() => {
    fetchStateMapping();
  }, [refreshTrigger]);

  useEffect(() => {
    if (deviationData.length > 0 && containerRef.current) {
      const containerWidth = containerRef.current.getBoundingClientRect().width;

      d3.select(containerRef.current).selectAll('*').remove();

      const chartWidth = containerWidth / deviationData.length;

      // Render a chart for each state
      deviationData.forEach((data) => {
        const chartContainer = d3
          .select(containerRef.current)
          .append('div')
          .attr('class', 'state-chart')
          .style('width', `${chartWidth}px`)
          .style('display', 'inline-block');

        renderBarChart(data, chartWidth, height, chartContainer.node());
      });
    }
  }, [deviationData, selectedFilters]); // Re-render when selectedFilters changes

  return <div ref={containerRef} className="bar-chart-container"></div>;
};

export default DeviationsBarChart;
