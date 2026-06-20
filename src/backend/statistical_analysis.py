import sqlite3
import json
import pandas as pd
import eel
from database_filter_variables import *

@eel.expose
def get_statistical_analysis_data(db_path="../data/incidents.db"):
    """
    Calculates and returns key statistical metrics for the selected incidents from the 'incidents_fa_values_table'.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        str: A JSON-formatted string containing the following metrics:
            {
                "perc_sla_met": float,                # Percentage of incidents that met the SLA
                "avg_time_to_resolve": float,         # Average time to resolve incidents (TTR)
                "perc_assigned_to_resolved_by": float,# Percentage of incidents where assigned_to equals resolved_by
                "perc_false_positives": float         # Percentage of incidents where closed_at == opened_at
            }
        If no incidents are selected or an error occurs, returns a JSON string with an "error" key.

    Interpretation:
        - "perc_sla_met": The proportion (in percent) of selected incidents that met their SLA requirements.
        - "avg_time_to_resolve": The average time to resolve (TTR) for selected incidents, extracted from the time_to_states_last_occurrence field.
        - "perc_assigned_to_resolved_by": The proportion (in percent) of incidents where the person assigned to the incident is the same as the person who resolved it.
        - "perc_false_positives": The proportion (in percent) of incidents where the incident was closed at the same time it was opened (potential false positives).
        - All metrics are calculated only for incidents whose IDs are returned by get_incident_ids_selection(), and may be further filtered by what-if analysis.
        - If no incidents are selected, all metrics are omitted and an error message is returned.

    Usage:
        - Use this output to monitor process KPIs, identify trends, or compare performance across time periods or filters.
        - The JSON string can be directly consumed by JavaScript via Eel for frontend analytics, dashboards, or reporting.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Fetch selected incident IDs
        incident_ids = get_incident_ids_selection()

        if not incident_ids:
            return json.dumps({"error": "No incidents selected."})

        # Query to get necessary columns from incidents table
        query = f"""
        SELECT incident_id, made_sla, time_to_states_last_occurrence, assigned_to, resolved_by, 
               closed_at, opened_at
        FROM incidents_fa_values_table
        WHERE incident_id IN ({','.join(['?'] * len(incident_ids))})
        """
        
        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Load data into pandas DataFrame
        df = pd.read_sql_query(query, conn, params=incident_ids)
        
        # Calculate PERC SLA MET
        perc_sla_met = df['made_sla'].mean() * 100 

        # Calculate AVG TIME TO RESOLVE
        def extract_ttr(time_to_states):
            if time_to_states:
                time_to_states_dict = json.loads(time_to_states)
                return time_to_states_dict.get("TTR", None)  # Get the TTR value, or None if it doesn't exist
            return None

        df['TTR'] = df['time_to_states_last_occurrence'].apply(extract_ttr)
        avg_time_to_resolve = df['TTR'].mean() if pd.notna(df['TTR']).any() else 0
        
        # Calculate PERC ASSIGNED TO RESOLVED BY
        perc_assigned_to_resolved_by = (df['assigned_to'] == df['resolved_by']).mean() * 100
        
        # Calculate FALSE POSITIVES
        def calculate_false_positive(closed_at, opened_at):
            if closed_at and opened_at:
                return 1 if closed_at == opened_at else 0
            return 0
        
        df['false_positive'] = df.apply(lambda x: calculate_false_positive(x['closed_at'], x['opened_at']), axis=1)
        perc_false_positives = df['false_positive'].mean() * 100
        
        # Create the result dictionary
        result = {
            "perc_sla_met": round(perc_sla_met, 2),
            "avg_time_to_resolve": round(avg_time_to_resolve, 2),
            "perc_assigned_to_resolved_by": round(perc_assigned_to_resolved_by, 2),
            "perc_false_positives": round(perc_false_positives, 2)
        }

        # Return the result as a JSON string
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": str(e)})

    finally:
        # Close the database connection
        if conn:
            conn.close()

# Example usage
if __name__ == "__main__":
    data = get_statistical_analysis_data()
    print("statistical_analysis.py")
    print(data)
