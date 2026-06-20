import sqlite3
import json
from database_filter_variables import *
import eel

@eel.expose
def get_compliance_metric_distribution(db_path="../data/incidents.db"):
    """
    Retrieves the distribution of a selected compliance metric for all incidents specified by get_incident_ids_selection(),
    formatted as a JSON array suitable for visualization (e.g., violin plot).

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        str: A JSON-formatted string containing a list of dictionaries, each with 'incident_id' and 'value' keys.
        Example:
            [
                {"incident_id": "INC0121001", "value": 0.92},
                {"incident_id": "INC0121002", "value": 0.85},
                ...
            ]
        If no data is found or an error occurs, returns an empty JSON array: []

    Interpretation:
        - Each dictionary in the list represents one incident and its compliance metric value.
        - The metric column is selected dynamically via get_filter_value("filters.compliance_metric").
        - Only incidents selected by get_incident_ids_selection() and filtered by what-if analysis are included.
        - The output is suitable for statistical visualization, such as violin plots, histograms, or box plots.
        - If no incidents are found or an error occurs, the function returns an empty list.

    Usage:
        - Use this output to visualize the distribution of compliance metrics across incidents, identify outliers, or analyze process performance.
        - The JSON string can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        metric_column = get_filter_value("filters.compliance_metric")

        # Get the selected incident IDs
        incident_ids = get_incident_ids_selection()

        # Convert incident_ids list to a format suitable for the SQL query
        incident_ids_placeholder = ",".join("?" * len(incident_ids))

        # Fetch the desired compliance metric values for the selected incidents
        query = f"""SELECT incident_id, {metric_column} FROM incidents_fa_values_table WHERE incident_id IN ({incident_ids_placeholder})"""

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"


        cursor.execute(query, incident_ids)
        metric_values = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        if not metric_values:
            return json.dumps([])  # Return an empty list if no data is found

        # Prepare the data for the violin plot
        distribution_data = []
        for incident in metric_values:
            incident_id, value = incident
            if value is not None:
                distribution_data.append({
                    "incident_id": incident_id,
                    "value": value
                })

        # Convert the distribution data to JSON format
        distribution_json = json.dumps(distribution_data)

        return distribution_json

    except Exception as e:
        print("process_compliance_distribution.py")
        print(f"An error occurred: {e}")
        return json.dumps([])

# Example usage
if __name__ == "__main__":
    distribution_json = get_compliance_metric_distribution()
    print("process_compliance_distribution.py")
    print(distribution_json)
