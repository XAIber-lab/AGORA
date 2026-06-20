import './tabular.css';  // Ensure this CSS correctly styles your table
import * as d3 from 'd3';
import { eel } from './App.js';  // Import eel from App.js

async function tabular(containerId) {
    if (!window.Inputs) {
        console.error("ObservableHQ Inputs library is not loaded.");
        return;
    }

    // Fetch the relevant data from Python via Eel
    let data;
    try {
        // Call the get_tabular_incidents_entries function via Eel
        data = await eel.get_tabular_incidents_entries()();  // Fetch the data from Python
    } catch (error) {
        console.error("Failed to fetch data from Python:", error);
        return;
    }

    if (!data || data.length === 0) {
        console.error("No data available or data could not be retrieved.");
        return;
    }

    // Convert the data into a processable format
    let parsedData = [];
    try {
        parsedData = JSON.parse(data);  // Assuming data is JSON stringified
    } catch (error) {
        console.error("Failed to parse data:", error);
        return;
    }

    // Clear the container before appending the new table
    const container = d3.select(`#${containerId}`)
        .style('width', '100%'); // Set the width of the container to 100% of its parent
    container.selectAll("*").remove();

    try {
        const table = window.Inputs.table(parsedData, {
            multiple: true, // Enable multiple row selection
            width: '100%'
        });

        table.style.tableLayout = "fixed"; // Set table layout to fixed
        

        table.addEventListener('input', () => {
            const selectedRows = table.value; // Get the selected rows
            console.log('Selected incidents:', selectedRows);
            // You can handle the selected rows here, e.g., pass them to another function
        });

        container.node().appendChild(table);
    } catch (error) {
        console.error("Error creating table with ObservableHQ Inputs:", error);
    }
}

export default tabular;
