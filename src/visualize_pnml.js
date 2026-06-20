import * as d3 from 'd3';
import { XMLParser } from 'fast-xml-parser';
import { eel } from './App';

// Function to parse PNML string
async function parsePnml(pnmlString) {
    try {
        const parserOptions = {
            ignoreAttributes: false,
            attributeNamePrefix: "@_"
        };
        const parser = new XMLParser(parserOptions);
        const result = parser.parse(pnmlString);
        return result;
    } catch (err) {
        console.error("Error parsing PNML:", err);
        throw err;
    }
}

function wrapText(selection, width) {
    selection.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reduce((acc, word) => acc.concat(word.split('-').flatMap((part, i, arr) => i < arr.length - 1 ? [part + '-', ''] : part)), []).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1,
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");

        while ((word = words.pop()) !== undefined) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", `${++lineNumber * lineHeight + dy}em`).text(word);
            }
        }
    });
}

// Function to create and update circular bar charts
function createCircularBarChart(svg, chartInnerRadius, deviations, activity, x, y, id) {
    let categories = ['MISSING', 'REPETITION', 'MISMATCH'];
    let colors = ['green', 'lime', 'yellow', 'darkorange'];

    let values = {
        'MISSING': deviations.missing[activity],
        'REPETITION': deviations.repetition[activity],
        'MISMATCH': deviations.mismatch[activity]
    };

    // Find the maximum value to set scale domain
    let maxDeviation = values.MISSING + values.REPETITION + values.MISMATCH;

    let data = categories.map((c, i) => ({
        name: c,
        value: values[c],  // Normalize values
        color: colors[i]
    }));

    let chartOuterRadius = chartInnerRadius + 20;
    let barPadding = 1;
    let nBars = categories.length;
    let barWidth = (chartOuterRadius - chartInnerRadius) / nBars - barPadding;

    data.forEach((d, i) => {
        d.radius = (chartOuterRadius - chartInnerRadius) / nBars * i + barPadding;
    });

    let bgArc = d3.arc()
        .innerRadius(d => chartInnerRadius + d.radius)
        .outerRadius(d => chartInnerRadius + d.radius + barWidth)
        .startAngle(0)
        .endAngle(Math.PI);

    let chartGroup = svg.select(`.chart-${id}`);
    if (chartGroup.empty()) {
        chartGroup = svg.append('g').attr('class', `chart-${id}`);
    }
    chartGroup.attr('transform', `translate(${x},${y})`);

    let bgBars = chartGroup.selectAll('path.arc')
        .data(data)
        .join('path')
        .attr('class', 'arc')
        .style('fill', d => d.color)
        .style('opacity', 0.5)
        .attr('d', d => bgArc(d));

    let arc = d3.arc()
        .innerRadius(d => chartInnerRadius + d.radius)
        .outerRadius(d => chartInnerRadius + d.radius + barWidth)
        .startAngle(0)
        .endAngle(d => angle(d.value / maxDeviation));

    let bars = chartGroup;
    bars.selectAll('path.bar')
        .data(data)
        .join('path')
        .attr('class', 'bar')
        .style('fill', d => d.color)
        .attr('d', d => arc(d));

    // Add text labels at the end of each bar
    bars.selectAll('text.value')
        .data(data)
        .join(enter => enter.append('text')
            .attr('class', 'value')
            .attr('x', d => coord(1.50, chartInnerRadius + d.radius + barWidth / 2).x - 5)
            .attr('y', d => coord(0.50, chartInnerRadius + d.radius + barWidth / 2).y)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'end')
            .attr('fill', '#fff')
            .attr('font-size', '8px') // Adjust the font-size as needed
            .text(d => d.value));

    // Add category names to the left of the starting point of each bar
    bars.selectAll('text.category')
        .data(data)
            .join(enter => enter.append('text')
            .attr('class', 'category')
            .attr('x', d => coord(1.50, chartInnerRadius + d.radius + barWidth / 2).x - 5)
            .attr('y', d => coord(1.50, chartInnerRadius + d.radius + barWidth / 2).y)
            .attr('dy', '0.2em')
            .attr('text-anchor', 'end')
            .attr('fill', '#fff')
            .attr('font-size', '8px')
            .text(d => d.name));


    function angle(value) {
        return d3.scaleLinear()
            .domain([0, 1])
            .range([0, Math.PI])(value);
    }

    function coord(value, radius) {
        let a = angle(value);
        let x_off = Math.cos(a) * radius;
        let y_off = Math.sin(a) * radius;
        return { x: x_off, y: y_off };
    }
}

// Function to create the visualization
async function createVisualization(containerId, places, transitions, arcs, deviations, stateMapping, stateTimes, transitionTimes) {
    const parent = d3.select(`#${containerId}`);
    parent.selectAll('*').remove();

    const width = parent.node().getBoundingClientRect().width;
    const height = 300;
    const nodeRadius = 40;

    const svg = parent.append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .style("background-color", "#1b1b1b");

    const nodes = [...places, ...transitions];
    const links = arcs.map(arc => ({
        source: arc.source,
        target: arc.target
    }));

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(200))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 2)
        .attr("stroke", "#aaa");

    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter().append("g")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("click", function(event, d) {
            const chartGroup = svg.select(`.chart-${d.id}`);
            if (!chartGroup.empty()) {
                chartGroup.remove();
            } else {
                if (stateMapping[d.label]) {
                    createCircularBarChart(svg, nodeRadius, deviations, stateMapping[d.label], d.x, d.y, d.id);
                } else {
                    console.error('Label not found in the mapping:', d.label);
                    return null; // or you could return a default value or throw an error
                }
                
            }
        });

    node.append("circle")
        .attr("r", nodeRadius)
        .attr("fill", d => d.type === 'place' ? '#1f77b4' : '#ff7f0e');

    node.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#FFF")
        .text(d => d.label)
        .call(wrapText, 2 * nodeRadius);

    node.append("text")
        .attr("dy", "2em")
        .attr("text-anchor", "middle")
        .attr("fill", "#FFF")
        .attr("font-size", "8px")
        .text(d => stateMapping[d.label] && stateTimes[stateMapping[d.label]] ? stateTimes[stateMapping[d.label]] : '');

    const transitionTexts = svg.append("g")
        .attr("class", "transition-texts")
        .selectAll("text")
        .data(links)
        .enter().append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.5em")
        .attr("fill", "#FFF")
        .attr("font-size", "8px")
        .text(d => {
            const sourceNode = d.source;
            const targetNode = d.target;
            if (sourceNode && targetNode) {
                const transitionKey = `${stateMapping[sourceNode.label]}->${stateMapping[targetNode.label]}`;
                return transitionTimes[transitionKey] || '';
            }
            return '';
        });

    simulation
        .nodes(nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(links);

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", d => `translate(${d.x},${d.y})`);
        node.each(function(d) {
            let chartGroup = svg.select(`.chart-${d.id}`);
            if (!chartGroup.empty()) {
                chartGroup.attr('transform', `translate(${d.x},${d.y})`);
            }
        });

        // Update the position of transition texts
        transitionTexts
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2)
            .attr("transform", d => {
                const angle = calculateAngle(d.source, d.target);
                return `rotate(${angle}, ${(d.source.x + d.target.x) / 2}, ${(d.source.y + d.target.y) / 2})`;
            });
    }

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    function calculateAngle(source, target) {
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        return Math.atan2(dy, dx) * (180 / Math.PI);
    }
}


// Function to visualize PNML data
async function visualizePnml(containerId, pnmlString) {
    try {
        // Fetch data first
        const deviations = await eel.count_frequencies()();
        const stateMapping = await eel.read_mapping_from_file()();
        const stateTimes = await eel.get_average_state_times()();
        const transitionTimes = await eel.get_average_transition_times()();
        
        // Then parse the PNML data
        const parsedPnml = await parsePnml(pnmlString);
        console.log("Parsed PNML Data:", parsedPnml);

        const net = parsedPnml?.pnml?.net;
        if (!net) {
            throw new Error("PNML data does not contain 'net' property.");
        }

        const netData = Array.isArray(net) ? net[0] : net;

        const places = netData.place ? netData.place.map(place => {
            const name = place?.name?.text ?? place['@_id'];
            const x = place?.graphics?.position ? parseFloat(place.graphics.position['@_x']) : 0;
            const y = place?.graphics?.position ? parseFloat(place.graphics.position['@_y']) : 0;

            return {
                id: place['@_id'],
                label: name,
                type: 'place',
                x: x,
                y: y
            };
        }) : [];

        const transitions = netData.transition ? netData.transition.map(transition => {
            const name = transition?.name?.text ?? transition['@_id'];
            const x = transition?.graphics?.position ? parseFloat(transition.graphics.position['@_x']) : 0;
            const y = transition?.graphics?.position ? parseFloat(transition.graphics.position['@_y']) : 0;

            return {
                id: transition['@_id'],
                label: name,
                type: 'transition',
                x: x,
                y: y
            };
        }) : [];

        const arcs = netData.arc ? netData.arc.map(arc => ({
            source: arc['@_source'],
            target: arc['@_target']
        })) : [];

        // Ensure deviations are fetched before calling createVisualization
        await createVisualization(containerId, places, transitions, arcs, deviations, stateMapping, stateTimes, transitionTimes);

    } catch (err) {
        console.error("Error visualizing PNML:", err);
    }
}

export default visualizePnml;
