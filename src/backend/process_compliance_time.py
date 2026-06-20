import sqlite3
from database_filter_variables import *
import eel

@eel.expose
def get_closed_ordered_incidents(db_name='../data/incidents.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Get the list of incident IDs from get_incident_ids_selection
        incident_ids = get_incident_ids_selection()

        # Create a placeholder string for the incident_ids list for the SQL query
        placeholder = ', '.join('?' for _ in incident_ids)
        compliance_metric = get_incident_compliance_metric()

        # Query to select the incidents, filter by selected incident IDs, and order by closed_at
        cursor.execute(f'''
            SELECT incident_id, closed_at, {compliance_metric}
            FROM incidents_fa_values_table
            WHERE incident_id IN ({placeholder})
            ORDER BY closed_at ASC
        ''', incident_ids)

        # Fetch all the results
        incidents = cursor.fetchall()

        # Process each incident to calculate the compliance metric
        result = []
        for incident in incidents:
            incident_id = incident[0]
            closed_at = incident[1]
            compliance_metric = incident[2]
            result.append((incident_id, closed_at, compliance_metric))

        # Return the final ordered result
        return result

    except sqlite3.Error as e:
        print("process_compliance_time.py")
        print(f"An error occurred: {e}")
        return None
    
    finally:
        # Close the connection
        conn.close()

def main():
    
    ordered_incidents = get_closed_ordered_incidents()

    if ordered_incidents:
        print("process_compliance_time.py")
        print("Ordered Incidents:")
        for incident in ordered_incidents:
            print(f"ID: {incident[0]}, Closed At: {incident[1]}, Compliance Metric: {incident[2]}")
    print("process_compliance_time.py")
    print(ordered_incidents)
if __name__ == "__main__":
    main()
