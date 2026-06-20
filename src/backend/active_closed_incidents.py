import sqlite3
import pandas as pd
import json
from database_filter_variables import *
import eel

@eel.expose
def get_incidents_open_and_closed_over_time(db_path="../data/incidents.db"):
    """
    Queries the incident opened_at and closed_at from the database and processes it
    to return data for visualizing active and closed incidents over time along with severity levels.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        dict: A dictionary with the following structure:
            {
                'opened_incidents': [
                    {'time': 'YYYY-MM-DD', 'count': int},
                    ...
                ],
                'active_incidents': [
                    {'time': 'YYYY-MM-DD', 'count': int},
                    ...
                ],
                'closed_incidents': [
                    {
                        'time': 'YYYY-MM-DD',
                        'count': int,        # cumulative number of closed incidents up to this date
                        'low': int,          # cumulative number of closed incidents with low severity
                        'moderate': int,     # cumulative number of closed incidents with moderate severity
                        'high': int,         # cumulative number of closed incidents with high severity
                        'critical': int      # cumulative number of closed incidents with critical severity
                    },
                    ...
                ],
                'closed_selected_incidents': [
                    {
                        'time': 'YYYY-MM-DD',
                        'count': int,        # number of closed incidents in the selected period (not cumulative)
                        'low': int,
                        'moderate': int,
                        'high': int,
                        'critical': int
                    },
                    ...
                ]
            }

    Interpretation:
        - Each list contains daily time series data.
        - 'opened_incidents': Number of incidents opened on each date (cumulative).
        - 'active_incidents': Number of incidents that are active (open but not yet closed) on each date.
        - 'closed_incidents': Cumulative number of incidents closed up to each date, with breakdown by severity.
        - 'closed_selected_incidents': Number of incidents closed in the selected period (not cumulative), with breakdown by severity.
        - The 'time' field is a string in 'YYYY-MM-DD' format.
        - The 'low', 'moderate', 'high', and 'critical' fields represent the cumulative or period-specific counts of closed incidents for each severity level.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Query to get opened_at and closed_at for incidents
        query = f"""
        SELECT incident_id, opened_at, closed_at
        FROM incidents_fa_values_table
        WHERE 1=1
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        
        # Execute the query and load the result into a DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Ensure that 'opened_at' and 'closed_at' are datetime objects
        df['opened_at'] = pd.to_datetime(df['opened_at']).dt.normalize()
        df['closed_at'] = pd.to_datetime(df['closed_at'], errors='coerce').dt.normalize()  # Handle NaT values for open incidents

        # Sort the data by opened_at date
        df = df.sort_values('opened_at')

        # Get selected incident IDs
        selected_incident_ids = get_incident_ids_selection()
        formatted_incident_ids = ', '.join(f"'{incident_id}'" for incident_id in selected_incident_ids)

        # Get compliance metric and thresholds
        # Get compliance metric and thresholds
        compliance_metric = get_filter_value("filters.compliance_metric")
        # Try to get metric-specific thresholds first
        compliance_metric_severity_levels2 = get_filter_value("filters.thresholds.compliance_metric_severity_levels2")
        if compliance_metric_severity_levels2 and compliance_metric in compliance_metric_severity_levels2:
            compliance_metric_thresholds = compliance_metric_severity_levels2[compliance_metric]
        else:
            compliance_metric_thresholds = get_filter_value("filters.thresholds.compliance_metric_severity_levels")

        print("active_closed_incidents.py")
        print(compliance_metric_thresholds)

        # Query to get compliance metric values for the selected incidents
        query_selected = f"""
        SELECT incident_id, closed_at, {compliance_metric}
        FROM incidents_fa_values_table
        WHERE incident_id IN ({formatted_incident_ids})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query_selected += f" AND ( {whatif_clause} )"

        # Load the selected incidents' closed_at dates and compliance metric
        df_selected = pd.read_sql_query(query_selected, conn)

        # Ensure 'closed_at' are datetime objects for the selected incidents
        df_selected['closed_at'] = pd.to_datetime(df_selected['closed_at'], errors='coerce').dt.normalize()
        # Filter out NaT (null) values before calculating min and max dates
        df_selected_filtered = df_selected.dropna(subset=['closed_at'])

        # Get the min and max closed_at for the selected incidents
        min_selected_date = df_selected_filtered['closed_at'].min()
        max_selected_date = df_selected_filtered['closed_at'].max()

        # Create a range of dates covering the period from the earliest opened_at to the latest closed_at
        time_range = pd.date_range(start=df['opened_at'].min(), end=df['closed_at'].max(), freq='D')

        # Initialize lists to hold the number of active and closed incidents over time
        opened_incidents = []
        active_incidents = []
        closed_incidents = []
        closed_selected_incidents = []
        closed_low_severity = []
        closed_moderate_severity = []
        closed_high_severity = []
        closed_critical_severity = []

        # Initialize counters for active and closed incidents
        current_active_count = 0
        total_active_count = 0
        current_closed_count = 0
        previous_closed_count = 0
        closed_low_severity_count = 0
        closed_moderate_severity_count = 0
        closed_high_severity_count = 0
        closed_critical_severity_count = 0

        # Helper function to check if a metric value falls within a given threshold range
        def check_threshold(value, threshold):
            conditions = threshold.split('AND')
            for condition in conditions:
                condition = condition.strip()
                if not eval(f"{value} {condition}"):
                    return False
            return True

        # Iterate through each time point in the time range
        for time_point in time_range:
            # Add incidents opened on the current time_point
            current_active_count += df[df['opened_at'] == time_point].shape[0]
            total_active_count += df[df['opened_at'] == time_point].shape[0]
            
            # Subtract incidents closed on the current time_point
            closed_on_current = df[df['closed_at'] == time_point].shape[0]
            current_active_count -= closed_on_current
            current_closed_count += closed_on_current

            if time_point < min_selected_date:
                previous_closed_count = current_closed_count
            
            # Calculate closed incidents by severity levels
            closed_at_current = df_selected_filtered[df_selected_filtered['closed_at'] == time_point]

            # Evaluate each incident for its severity level based on the compliance metric value
            for _, incident in closed_at_current.iterrows():
                metric_value = incident[compliance_metric]

                if check_threshold(metric_value, compliance_metric_thresholds['low']):
                    closed_low_severity_count += 1
                elif check_threshold(metric_value, compliance_metric_thresholds['moderate']):
                    closed_moderate_severity_count += 1
                elif check_threshold(metric_value, compliance_metric_thresholds['high']):
                    closed_high_severity_count += 1
                elif check_threshold(metric_value, compliance_metric_thresholds['critical']):
                    closed_critical_severity_count += 1

            # Append the counts to the lists
            opened_incidents.append({'time': time_point.strftime('%Y-%m-%d'), 'count': total_active_count})
            active_incidents.append({'time': time_point.strftime('%Y-%m-%d'), 'count': current_active_count})
            closed_incidents.append({
                'time': time_point.strftime('%Y-%m-%d'),
                'count': current_closed_count,
                'low': closed_low_severity_count,
                'moderate': closed_moderate_severity_count,
                'high': closed_high_severity_count,
                'critical': closed_critical_severity_count
            })

        # Filter the active and closed incidents lists based on the selected min and max closed_at dates
        opened_incidents = [entry for entry in opened_incidents if min_selected_date <= pd.to_datetime(entry['time']) <= max_selected_date]
        active_incidents = [entry for entry in active_incidents if min_selected_date <= pd.to_datetime(entry['time']) <= max_selected_date]
        closed_incidents = [entry for entry in closed_incidents if min_selected_date <= pd.to_datetime(entry['time']) <= max_selected_date]

        closed_selected_incidents = closed_incidents
        if closed_selected_incidents:
            for incident in closed_selected_incidents:
                incident['count'] -= previous_closed_count

        # Prepare the result to return
        result = {
            'opened_incidents': opened_incidents,
            'active_incidents': active_incidents,
            'closed_incidents': closed_incidents,
            'closed_selected_incidents': closed_selected_incidents
        }
        # Return the result as a JSON string
        return result

    except Exception as e:
        print("active_closed_incidents.py")
        print(f"An error occurred: {e}")
        return {'active_incidents': [], 'closed_incidents': []}  # Return empty data on error
    
    finally:
        # Close the database connection
        conn.close()

# Example usage
if __name__ == "__main__":
    # Query the active and closed incidents data and print the JSON result
    incidents_json = get_incidents_open_and_closed_over_time()
    print("active_closed_incidents.py")
    print(incidents_json)
