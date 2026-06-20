import sqlite3
import pandas as pd
import json
import eel
import re  # Import regular expressions module
from database_filter_variables import *

@eel.expose
def get_critical_incidents(db_path="../data/incidents.db"):
    """
    Retrieves incidents that fall into the critical range based on the selected compliance metric and threshold levels.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        list: A list of dictionaries, each representing a critical incident with its incident_id and compliance metric value.
        Example:
            [
                {"incident_id": "INC0121001", "fitness": 0.32},
                {"incident_id": "INC0121002", "fitness": 0.41},
                ...
            ]

    Interpretation:
        - The function selects incidents whose compliance metric (e.g., 'fitness' or 'cost') falls within the critical threshold as defined in the filters.
        - The compliance metric and thresholds are dynamically selected using get_filter_value.
        - Only incidents selected by get_incident_ids_selection() and filtered by what-if analysis are included.
        - For 'fitness', lower values are more critical; for 'cost', higher values are more critical.
        - The result is sorted by the compliance metric in the appropriate order (ascending for 'fitness', descending for 'cost').
        - If no incidents are found or an error occurs, the function returns an empty list.

    Usage:
        - Use this output to identify and analyze the most critical incidents for process improvement, reporting, or targeted remediation.
        - The list can be directly consumed by JavaScript via Eel for frontend analytics, dashboards, or visualization.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Get the compliance metric from the filters
        compliance_metric = get_filter_value("filters.compliance_metric")

        compliance_metric_severity_levels2 = get_filter_value("filters.thresholds.compliance_metric_severity_levels2")
        if compliance_metric_severity_levels2 and compliance_metric in compliance_metric_severity_levels2:
            thresholds = compliance_metric_severity_levels2[compliance_metric]
        else:
            thresholds = get_filter_value("filters.thresholds.compliance_metric_severity_levels")

        # Get selected incident IDs
        incident_ids = get_incident_ids_selection()
        if not incident_ids:
            return []  # No incidents to process

        formatted_incident_ids = ', '.join(f"'{incident_id}'" for incident_id in incident_ids)

        # Define severity level and sort order based on the compliance metric
        if compliance_metric == 'fitness':
            severity_level = 'critical'  # Lower fitness values are more critical
            sort_order = 'ASC'  # Lower values first
        elif compliance_metric == 'cost':
            severity_level = 'critical'  # Higher cost values are more critical
            sort_order = 'DESC'  # Higher values first
        else:
            raise ValueError(f"Unknown compliance metric: {compliance_metric}")

        # Get the threshold string for the severity level
        threshold_str = thresholds[severity_level]  # e.g., '>= 0 AND <= 0.5'

        # Build the threshold condition for the SQL query
        threshold_condition = build_threshold_condition(compliance_metric, threshold_str)

        # Build the SQL query to get incidents that fall in the critical range
        query = f"""
            SELECT incident_id, {compliance_metric}
            FROM incidents_fa_values_table
            WHERE incident_id IN ({formatted_incident_ids})
            AND {threshold_condition}
        """

        # Add the 'whatif_analysis' exclusion clause if applicable
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ({whatif_clause})"

        # Add the ORDER BY clause
        query += f" ORDER BY {compliance_metric} {sort_order}"

        # Execute the query and load the result into a DataFrame
        df = pd.read_sql_query(query, conn)

        # Convert the DataFrame to a list of dictionaries (JavaScript object equivalent)
        result = df.to_dict(orient='records')

        return result  # Return the result as a list of dictionaries

    except Exception as e:
        print("critical_incidents.py")
        print(f"An error occurred: {e}")
        return []  # Return an empty list on error

    finally:
        # Close the database connection
        conn.close()

def build_threshold_condition(compliance_metric, threshold_str):
    """
    Builds a SQL condition string by embedding the compliance metric into the threshold expressions.

    Args:
        compliance_metric (str): The compliance metric column name.
        threshold_str (str): The threshold expression string, e.g., '>= 0 AND <= 0.5'.

    Returns:
        str: A SQL condition string with the compliance metric applied to each condition.
    """
    # Split the threshold_str into tokens using 'AND' or 'OR' as delimiters
    tokens = re.split(r'\s+(AND|OR)\s+', threshold_str)
    conditions = []
    for token in tokens:
        token = token.strip()
        if token in ('AND', 'OR'):
            # Logical operators are added directly
            conditions.append(token)
        else:
            # Prepend the compliance metric to each condition
            conditions.append(f"{compliance_metric} {token}")
    # Join the conditions back into a single string
    condition_str = ' '.join(conditions)
    return condition_str

# Example usage
if __name__ == "__main__":
    critical_incidents_json = get_critical_incidents()
    print("critical_incidents.py")
    print(critical_incidents_json)
