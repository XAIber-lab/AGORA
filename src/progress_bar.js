import './progress_bar.css';
import * as d3 from 'd3';
import { eel } from './App';

async function createProgressBar(containerId, metricName, limits = [0, 1], height = 30) {
    // Fetch the severity levels from the backend in the new JSON format
    const severityLevels = JSON.parse(await eel.get_compliance_metric_thresholds()());
    console.log(severityLevels);
    const progress = await eel.calculate_column_average(metricName)();
    const [min, max] = limits;
    const scaledProgress = ((progress - min) / (max - min)) * 100;
    const roundedProgress = progress.toFixed(3);

    const container = d3.select(`#${containerId}`);
    const width = container.node().getBoundingClientRect().width;
    container.selectAll('*').remove();

    // Add metric name above the progress bar
    container.append('div')
        .attr('class', 'metric-name')
        .text(metricName)
        .style('text-align', 'center')
        .style('color', 'white')
        .style('margin-bottom', '5px');

    const svg = container.append('svg')
        .attr('width', '100%')
        .attr('height', height);

    // Define severity colors and map them to severity levels
    const severityColors = ['purple', 'red', 'orange', 'green'];
    const severityRanges = [
        severityLevels.critical,
        severityLevels.moderate,
        severityLevels.high,
        severityLevels.low
    ];

    // Create background rectangles for each severity range
    severityRanges.forEach((range, index) => {
        const rangeStart = range[0];
        const rangeEnd = range[1];

        const rect = svg.append('rect')
            .attr('x', (width * (rangeStart - min)) / (max - min))
            .attr('y', 0)
            .attr('width', (width * (rangeEnd - rangeStart)) / (max - min))
            .attr('height', height)
            .attr('fill', severityColors[index])
            .attr('stroke', 'none')
            .on('click', async function () {
                const isSelected = d3.select(this).attr('stroke') === '#007FFF';
                d3.select(this).attr('stroke', isSelected ? 'none' : '#007FFF').attr('stroke-width', isSelected ? '0' : '3');
                
                // Set the filter for the clicked severity range
                await eel.set_filter_compliance_metric_thresholds(metricName, rangeStart, rangeEnd)();
                
                // Trigger tabular update after setting filter
                //tabular('table-container');
            });
    });

    // Add dotted line for average value
    svg.append('line')
        .attr('x1', (width * scaledProgress) / 100)
        .attr('y1', 0)
        .attr('x2', (width * scaledProgress) / 100)
        .attr('y2', height)
        .attr('stroke', '#000')
        .attr('stroke-dasharray', '2,2')  // More dashes
        .attr('stroke-width', '2');

    // Add text label for average value next to the line
    svg.append('text')
        .attr('x', (width * scaledProgress) / 100 + 20)
        .attr('y', height / 2)  // Position at the middle of the bar
        .attr('dy', '.35em')
        .attr('text-anchor', 'middle')
        .attr('fill', '#000')
        .text(`${roundedProgress}`)
        .style('font-size', '14px');
}

export default createProgressBar;
