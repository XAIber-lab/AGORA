import sqlite3
import json
from database_filter_variables import *
import eel

@eel.expose
def get_ordered_time_to_states_last_occurrence(db_name='../data/incidents.db'):
    """
    Fetches and returns the time to last occurrence of process states for each incident, ordered by the incident's closed_at timestamp.

    Args:
        db_name (str): Path to the SQLite database file.

    Returns:
        str: A JSON-formatted string containing a list of dictionaries, each with:
            - incident_id (str): The ID of the incident.
            - closed_at (str): The date and time when the incident was closed.
            - time_to_states (dict): A dictionary mapping 'TT' + state code (str) to time in minutes (int or float).
        Example:
            [
                {
                    "incident_id": "INC0033734",
                    "closed_at": "2016-06-26 10:00:00",
                    "time_to_states": {"TTN": 13, "TTA": 26187, "TTR": 31602, "TTC": 38824}
                },
                ...
            ]

    Interpretation:
        - Each dictionary represents one incident, including its ID, closure timestamp, and a mapping of process states to the time (in minutes) taken to reach their last occurrence.
        - The keys in time_to_states are formatted as 'TT' (Time To) followed by the state code (e.g., 'TTN' for Time To state N).
        - The values are the number of minutes until the last occurrence of each state in the incident's process flow.
        - The list is ordered by the closed_at timestamp in ascending order (oldest first).
        - Only incidents selected by get_incident_ids_selection() and filtered by what-if analysis are included.
        - If no incidents are found or an error occurs, the function returns None.

    Usage:
        - Use this output to analyze the timing of process state transitions across incidents, identify bottlenecks, or visualize process timelines.
        - The JSON string can be directly consumed by JavaScript via Eel for frontend analytics, dashboards, or reporting.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Get the list of incident IDs from get_incident_ids_selection
        incident_ids = get_incident_ids_selection()

        # Create a placeholder string for the incident_ids list for the SQL query
        placeholder = ', '.join('?' for _ in incident_ids)

        # Query to select the incidents, filter by selected incident IDs, and order by closed_at
        # Start with the base query, including placeholders for the incident_ids
        query = """
            SELECT incident_id, closed_at, time_to_states_last_occurrence
            FROM incidents_fa_values_table
            WHERE incident_id IN ({placeholder})
            ORDER BY closed_at ASC
        """

        # Add the 'whatif_analysis' exclusion clause if it exists
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            # Insert the 'whatif_analysis' clause before the ORDER BY clause
            query = query.replace('ORDER BY closed_at ASC', f"AND ( {whatif_clause} ) ORDER BY closed_at ASC")

        # Replace the placeholder for the incident_ids
        placeholder = ','.join(['?'] * len(incident_ids))
        query = query.format(placeholder=placeholder)

        # Execute the query with the incident_ids as parameters
        cursor.execute(query, incident_ids)

        # Fetch all the results
        incidents = cursor.fetchall()

        # Process each incident to return in the desired format
        result = []
        for incident in incidents:
            incident_id = incident[0]
            closed_at = incident[1]
            time_to_states = json.loads(incident[2])  # Assuming time_to_states_last_occurrence is stored as a JSON string
            result.append({
                'incident_id': incident_id,
                'closed_at': closed_at,
                'time_to_states': time_to_states
            })

        return json.dumps(result)

    except sqlite3.Error as e:
        print("process_timedeltas.py")
        print(f"An error occurred: {e}")
        return None
    
    finally:
        # Close the connection
        conn.close()


def main():
    
    ordered_incidents = get_ordered_time_to_states_last_occurrence()

    if ordered_incidents:
        print("process_timedeltas.py")
        print("Ordered Incidents:")
        for incident in ordered_incidents:
            print("process_timedeltas.py")
            print(f"ID: {incident['incident_id']}, Closed At: {incident['closed_at']}, Time to States: {incident['time_to_states']}")
    print("process_timedeltas.py")
    print(ordered_incidents)

if __name__ == "__main__":
    main()
