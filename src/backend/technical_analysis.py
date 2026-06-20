import sqlite3
import json
import re  # To handle extracting numbers from string
import eel
from database_filter_variables import *

def extract_numeric_value(value):
    """
    Extracts the first numeric value from a string.
    If the value is already an integer, it returns it as is.
    If no numeric value is found, returns None.
    """
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        match = re.search(r'\d+', value)  # Find the first numeric value in the string
        return int(match.group()) if match else None
    return None

@eel.expose
def get_incident_technical_attributes(db_path="../data/incidents.db"):
    """
    Retrieves selected technical attributes for each incident specified by get_incident_ids_selection(),
    cleans the attribute values to extract only numeric data, and returns the result as a list of dictionaries.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of dictionaries, each representing an incident and its technical attributes.
        Example:
            [
                {
                    "symptom": 2,
                    "impact": 3,
                    "urgency": 1,
                    "priority": 2,
                    "location": 5,
                    "category": 4
                },
                ...
            ]
        If no incidents are selected or an error occurs, returns a dictionary with an "error" key.

    Interpretation:
        - Each dictionary contains the numeric values for the specified technical attributes of an incident.
        - Non-numeric text in the attribute values is removed; only the first numeric value is extracted.
        - Only incidents selected by get_incident_ids_selection() and filtered by what-if analysis are included.
        - If no incidents are selected, the function returns {"error": "No incidents selected."}.
        - If an error occurs, the function returns {"error": <error_message>}.

    Usage:
        - Use this output for technical analysis, attribute distribution, or to visualize incident characteristics in dashboards or reports.
        - The list can be directly consumed by JavaScript via Eel for frontend analytics and visualization.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Fetch the selected incident IDs
        incident_ids = get_incident_ids_selection()  # Directly use the list

        if not incident_ids:
            return {"error": "No incidents selected."}

        # Query to get the desired columns from the incidents_fa_values_table
        query = f"""
        SELECT incident_id, u_symptom, impact, urgency, priority, location, category
        FROM incidents_fa_values_table
        WHERE incident_id IN ({','.join(['?'] * len(incident_ids))})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Execute the query
        cursor = conn.cursor()
        cursor.execute(query, incident_ids)
        rows = cursor.fetchall()

        # Format the result into a list of dictionaries
        traces = []
        for row in rows:
            traces.append({
                "symptom": extract_numeric_value(row[1]),
                "impact": extract_numeric_value(row[2]),
                "urgency": extract_numeric_value(row[3]),
                "priority": extract_numeric_value(row[4]),
                "location": extract_numeric_value(row[5]),
                "category": extract_numeric_value(row[6])
            })

        # Return the result as a list of dictionaries
        return traces

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Close the database connection
        if conn:
            conn.close()

# Example usage
if __name__ == "__main__":
    result = get_incident_technical_attributes()
    print("technical_analysis.py")
    print(result)
