import sqlite3
import pandas as pd
import eel
import json
from database_filter_variables import get_incident_compliance_metric, get_incident_ids_from_tabular_selection

@eel.expose
def calculate_individual_averages(db_path="../data/incidents.db"):
    """
    Fetches selected incidents from 'incident_ids_from_tabular_selection',
    queries the 'incidents_fa_values_table' to retrieve the compliance metric values, TTR (time_to_states_last_occurrence),
    and SLA compliance, and returns the averages and percentage of incidents that made the SLA.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        dict: A dictionary containing the average compliance metric, average TTR, and the percentage of incidents that made the SLA.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Fetch the selected incident IDs from 'incident_ids_from_tabular_selection'
        incident_ids = get_incident_ids_from_tabular_selection()  # Directly use the list

        if not incident_ids:
            return {"error": "No incidents selected"}

        # Get the compliance metric column name
        compliance_metric = get_incident_compliance_metric()

        # Query the database for the compliance metric values, time_to_states_last_occurrence (TTR), and made_sla values
        query = f"""
        SELECT {compliance_metric}, time_to_states_last_occurrence, made_sla
        FROM incidents_fa_values_table
        WHERE incident_id IN ({','.join(['?'] * len(incident_ids))})
        """

        # Execute the query
        df = pd.read_sql_query(query, conn, params=incident_ids)

        if df.empty:
            return {"error": "No matching incidents found"}

        # Extract the TTR values from the time_to_states_last_occurrence column
        def extract_ttr(time_to_states):
            time_to_states_dict = json.loads(time_to_states)
            return time_to_states_dict.get("TTR", None)  # Get the TTR value, or None if it doesn't exist

        df["TTR"] = df["time_to_states_last_occurrence"].apply(extract_ttr)

        # Calculate the averages
        avg_compliance_metric = df[compliance_metric].mean()
        avg_ttr = df["TTR"].mean()

        # Convert average_ttr from minutes to "xd xh xmin" format
        def format_ttr(ttr_minutes):
            if pd.isna(ttr_minutes):
                return None
            days, remainder = divmod(ttr_minutes, 1440)  # 1440 minutes in a day
            hours, minutes = divmod(remainder, 60)
            return f"{int(days)}d {int(hours)}h {int(minutes)}min"

        avg_ttr_formatted = format_ttr(avg_ttr)

        # Calculate the percentage of incidents that made SLA
        made_sla_percentage = df["made_sla"].mean() * 100  # Boolean column: True = 1, False = 0

        # Ensure SLA percentage is returned with two decimal places
        made_sla_percentage = round(made_sla_percentage, 2) if pd.notna(made_sla_percentage) else 0.00

        # Convert numpy types to native Python types
        avg_compliance_metric = float(avg_compliance_metric) if pd.notna(avg_compliance_metric) else None

        # Return the averages and SLA percentage
        return {
            "average_compliance_metric": avg_compliance_metric,
            "average_ttr": avg_ttr_formatted,  # Use formatted TTR value
            "sla_percentage": f"{made_sla_percentage:.2f}"  # Return SLA percentage formatted to two decimal places
        }

    except Exception as e:
        print("individual_incident_metrics.py")
        print(f"An error occurred: {e}")
        return {"error": str(e)}

    finally:
        # Close the database connection
        conn.close()

@eel.expose
def get_incident_event_intervals(db_path="../data/incidents.db"):
    """
    Fetches selected incidents from 'incident_ids_from_tabular_selection',
    queries the 'incidents_fa_values_table' to retrieve the incident_id and event_interval_minutes columns,
    and returns them as a list of dictionaries.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of dictionaries containing the incident_id and event_interval_minutes for each selected incident.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Fetch the selected incident IDs from 'incident_ids_from_tabular_selection'
        incident_ids = get_incident_ids_from_tabular_selection()  # Directly use the list

        if not incident_ids:
            return {"error": "No incidents selected"}

        # Query the database for the incident_id and event_interval_minutes values
        query = f"""
        SELECT incident_id, event_interval_minutes
        FROM incidents_fa_values_table
        WHERE incident_id IN ({','.join(['?'] * len(incident_ids))})
        """

        # Execute the query
        df = pd.read_sql_query(query, conn, params=incident_ids)

        if df.empty:
            return {"error": "No matching incidents found"}

        # Convert the DataFrame to a list of dictionaries
        result = df.to_dict(orient="records")

        return result

    except Exception as e:
        print("individual_incident_metrics.py")
        print(f"An error occurred: {e}")
        return {"error": str(e)}

    finally:
        # Close the database connection
        conn.close()

# Example usage
if __name__ == "__main__":
    averages = calculate_individual_averages()
    print("individual_incident_metrics.py")
    print(averages)

    event_intervals = get_incident_event_intervals()
    print("individual_incident_metrics.py")
    print(event_intervals)