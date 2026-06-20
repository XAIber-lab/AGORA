import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { schemeSet2 } from 'd3-scale-chromatic';
import { eel } from './App';
import './ProcessComplianceBarChart.css'; // Import the CSS file

const ProcessComplianceBarChart = ({ height = 500, refreshTrigger }) => {
  const svgRef = useRef();
  const [enabledStates, setEnabledStates] = useState({
    N: true,
    A: true,
    W: true,
    R: true,
    C: true,
  });

  // Mapping from state codes to state names
  const stateNames = {
    N: 'detection',
    A: 'activation',
    W: 'awaiting',
    R: 'resolution',
    C: 'closure',
  };

  const [complianceMetric, setComplianceMetric] = useState(''); // Add state for complianceMetric

  useEffect(() => {
    // Fetch compliance metric
    const fetchComplianceMetric = async () => {
      const metric = await eel.get_filter_value('filters.compliance_metric')();
      setComplianceMetric(metric.toUpperCase());
    };

    fetchComplianceMetric();
  }, []);

  useEffect(() => {
    // Fetch data from the exposed Python function
    eel.get_compliance_per_state_per_incident()().then(data => {
      const svgElement = d3.select(svgRef.current);
      const containerWidth = svgElement.node().parentNode.clientWidth;

      const width = containerWidth;
      const margin = { top: 10, right: 20, bottom: 25, left: 40 };
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Clear previous SVG content if any
      svgElement.selectAll('*').remove();

      // Parse the JSON data
      const parsedData = JSON.parse(data);

      // Process data to calculate compliance scores per state
      const complianceData = parsedData.map(d => {
        const complianceMetric = Object.entries(d.compliance_per_state || {}).reduce((acc, [state, score]) => {
          acc[state] = score;
          return acc;
        }, {});
        return {
          incidentId: d.incident_id,
          closedAt: new Date(d.closed_at),
          complianceMetric, // Object with compliance scores per state
          totalDeviations: d.total_deviations,
        };
      });

      // Group by closedAt date to check for overlaps
      const groupedByDate = d3.group(complianceData, d => d.closedAt);

      // Assign a horizontal offset based on the number of bars that share the same closedAt date
      groupedByDate.forEach((group, date) => {
        group.forEach((d, i) => {
          // d.offset = i - (group.length - 1) / 2; Center the bars around the original position
          d.offset = 0;
        });
      });

      // Flatten the compliance data for stacked bars, only including enabled states
      const flattenedData = [];
      complianceData.forEach(d => {
        Object.entries(d.complianceMetric).forEach(([state, score]) => {
          if (enabledStates[state]) {
            flattenedData.push({
              incidentId: d.incidentId,
              closedAt: d.closedAt,
              state,
              score,
              offset: d.offset, // Add offset to each bar
            });
          }
        });
      });

      // Define the fixed order for states and filter by enabled states
      const orderedStates = ['N', 'A', 'W', 'R', 'C'].filter(state => enabledStates[state]);

      // Set up scales
      const xScale = d3.scaleTime()
        .domain([
          d3.timeDay.floor(d3.min(flattenedData, d => d.closedAt)), // Start at the beginning of the first date
          d3.timeDay.ceil(d3.max(flattenedData, d => d.closedAt)), // End at the end of the last date
        ])
        .range([0, innerWidth]);

      const yScale = d3.scaleLinear()
        .domain([0, 1])
        .nice()
        .range([innerHeight, 0]);

      const colorScale = d3.scaleOrdinal()
        .domain(orderedStates)
        .range(schemeSet2);

      const g = svgElement.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
        .attr('class', 'graph-group')
        .attr('pointer-events', 'all');

      // Set the bar width and spacing for overlapping bars
      const barWidth = 5;
      const maxOffset = 2; // Maximum offset for bars

      // Stack the data for stacked bar chart using the fixed order of states
      const stack = d3.stack()
        .keys(orderedStates)
        .value((d, key) => d.complianceMetric[key] || 0);

      const stackedData = stack(complianceData);

      // Append the bars
      g.append('g')
        .attr('class', 'bars')
        .selectAll('g')
        .data(stackedData)
        .join('g')
        .attr('fill', d => colorScale(d.key))
        .selectAll('rect')
        .data(d => d)
        .join('rect')
        .attr('x', d => xScale(d.data.closedAt) + (d.data.offset * (barWidth + maxOffset))) // Adjust position based on offset
        .attr('y', d => yScale(d[1]))
        .attr('height', d => yScale(d[0]) - yScale(d[1]))
        .attr('width', barWidth) // Adjust width of bars as needed
        .append('title') // Add tooltip on hover
        .text(d => `Incident: ${d.data.incidentId}\nState: ${stateNames[d.key]}\nScore: ${(d[1] - d[0]).toFixed(2)}`); // Updated tooltip to show state name

      // Append the x-axis
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .attr('class', 'x-axis')
        .call(d3.axisBottom(xScale).tickPadding(5))
        .selectAll('text')
        .attr('fill', 'white'); // Make the axis text white

      g.select('.x-axis path').style('stroke', 'white'); // Set x-axis line color to white
      g.select('.x-axis line').style('stroke', 'white'); // Set x-axis ticks color to white
      g.select('.x-axis').selectAll('.tick line').attr('stroke', 'white');

      // Append the y-axis with 5 ticks
      g.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(yScale)
          .ticks(5) // Specify 5 ticks on the y-axis
          .tickSize(-innerWidth)
          .tickPadding(5))
        .selectAll('text')
        .attr('fill', 'white'); // Set y-axis text color to white

      g.select('.y-axis path').style('stroke', 'white'); // Set y-axis line color to white
      g.select('.y-axis line').style('stroke', 'white'); // Set y-axis ticks color to white
      

      // Apply zoom behavior
      const zoom = d3.zoom()
        .scaleExtent([1, 1000])
        .translateExtent([[margin.left, margin.top], [containerWidth - margin.right, height - margin.top]])
        .extent([[margin.left, margin.top], [containerWidth - margin.right, height - margin.top]])
        .on('zoom', (event) => {
          const newXScale = event.transform.rescaleX(xScale);
          g.selectAll('.bars rect').attr('x', d => newXScale(d.data.closedAt) + (d.data.offset * (barWidth + maxOffset))); // Adjust position on zoom
          g.select('.x-axis').call(d3.axisBottom(newXScale).tickPadding(5));

          // Reapply styles to x-axis elements after zoom
          g.select('.x-axis').selectAll('text').attr('fill', 'white');
          g.select('.x-axis path').style('stroke', 'white');
          g.select('.x-axis line').style('stroke', 'white');
          g.select('.x-axis').selectAll('.tick line').attr('stroke', 'white');
        });

      svgElement.call(zoom);

    }).catch(error => {
      console.error('Error fetching data:', error);
    });
  }, [height, refreshTrigger, enabledStates]);

  const toggleState = stateCode => {
    setEnabledStates({
      ...enabledStates,
      [stateCode]: !enabledStates[stateCode],
    });
  };

  return (
    <div>
      <div className="header-row">
        <div className="name">{complianceMetric} OVER TIME</div>
        <div className="controls">
          {Object.keys(enabledStates).map(stateCode => (
            <label key={stateCode} style={{ color: 'white', marginLeft: '10px' }}>
              <input
                type="checkbox"
                checked={enabledStates[stateCode]}
                onChange={() => toggleState(stateCode)}
              />
              {stateNames[stateCode].toUpperCase()} {/* Display the state name instead of code */}
            </label>
          ))}
        </div>
      </div>
      <svg ref={svgRef} style={{ width: '100%', height: height }} />
    </div>
  );
};

export default ProcessComplianceBarChart;
