import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './GlobalProgress.css';
import { eel } from './App';  // Ensure eel is imported

const GlobalProgress = (updateProgress) => {
  const [progressData, setProgressData] = useState({});

  // Function to fetch progress data from the backend
  const fetchProgressData = async () => {
    try {
      // Call the exposed function from the backend via Eel
      const result = JSON.parse(await eel.get_global_progress()());

      // Update the state with the fetched data
      setProgressData(result);
    } catch (error) {
      console.error('Failed to fetch global progress data:', error);
    }
  };

  // Fetch data when the component mounts
  useEffect(() => {
    fetchProgressData();
  }, [updateProgress]);

  return (
    <div className="global-progress-container">
      {Object.keys(progressData).map((key) => (
        <ProgressRow key={key} operator={key} progress={progressData[key]} />
      ))}
    </div>
  );
};

const ProgressRow = ({ operator, progress }) => {
  const barRef = useRef();

  useEffect(() => {
    const container = d3.select(barRef.current);
    const width = container.node().getBoundingClientRect().width;
    const height = 25;

    container.selectAll('*').remove(); // Clear previous content

    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Background bar (unfulfilled portion in red)
    svg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'red'); // Red color for unfulfilled

    // Progress bar (fulfilled portion in green)
    const progressWidth = progress * width;
    svg.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', progressWidth)
      .attr('height', height)
      .attr('fill', 'green'); // Green color for fulfilled
      

    // Progress text in the middle
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height / 2)
      .attr('dy', '.35em')
      .attr('text-anchor', 'middle')
      .attr('fill', '#fff')
      .text(`${(progress * 100).toFixed(2)}%`)
      .style('font-size', '12px')
      .style('pointer-events', 'none'); // Allow clicks to pass through text

  }, [progress]);

  return (
    <div className="progress-row">
      <div className="operator-name">{operator}</div>
      <div className="progress-bar-container">
        <div className="progress-bar" ref={barRef}></div>
      </div>
    </div>
  );
};

export default GlobalProgress;
