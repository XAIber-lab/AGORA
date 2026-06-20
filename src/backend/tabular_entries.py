import sqlite3
import pandas as pd
import json
from database_filter_variables import *
import eel
import ast
import re  # Import re for regex operations

def build_filter_query(filters):
    """
    Builds a SQL filter query based on the provided filters dictionary.
    
    Args:
        filters (dict): The filters dictionary returned from get_filter_value().

    Returns:
        tuple: A tuple containing the SQL query fragment representing the active filters and the list of parameters.
    """
    # Initialize an empty list to hold all filter conditions
    conditions = []
    # Initialize a list for parameters
    parameters = []

    filters = filters.get('filters', {})

    # Handle compliance bar filters (severity levels)
    compliance_bar_filters = filters.get('overview_metrics', {}).get('compliance_bar', {})
    severity_levels = filters.get('thresholds', {}).get('compliance_metric_severity_levels', {})
    compliance_conditions = []

    compliance_metric = filters.get('compliance_metric', '')
    print("tabular_entries.py1")
    for level, is_active in compliance_bar_filters.items():
        if is_active:
            threshold = severity_levels.get(level)
            if threshold:
                # Correct the SQL syntax by repeating the compliance_metric for both conditions
                min_condition, max_condition = threshold.split('AND')
                min_condition = min_condition.strip()
                max_condition = max_condition.strip()

                # If compliance_metric is not present, add it to both conditions
                if compliance_metric not in min_condition:
                    min_condition = f"{compliance_metric} {min_condition}"
                if compliance_metric not in max_condition:
                    max_condition = f"{compliance_metric} {max_condition}"

                compliance_conditions.append(f"({min_condition} AND {max_condition})")
    
    if compliance_conditions:
        conditions.append(f"({' OR '.join(compliance_conditions)})")

    # Handle statistical analysis filters
    statistical_analysis_filters = filters.get('statistical_analysis', {})
    for field, value in statistical_analysis_filters.items():
        if value is not None:
            if field == 'perc_sla_met':
                if value:
                    conditions.append("made_sla = 1")
                else:
                    conditions.append("made_sla = 0")
            elif field == 'perc_assigned_to_resolved_by':
                if value:
                    conditions.append("assigned_to = resolved_by")
                else:
                    conditions.append("assigned_to != resolved_by")
            elif field == 'perc_false_positives':
                if value:
                    conditions.append("opened_at = closed_at")
                else:
                    conditions.append("opened_at != closed_at")

    # Handle common variants filters
    common_variants_filters = filters.get('common_variants', {})
    if common_variants_filters:  # Check if it's not None and not empty
        placeholders = ', '.join('?' for _ in common_variants_filters)
        conditions.append(f"variant IN ({placeholders})")
        parameters.extend(common_variants_filters)

    # Handle deviation filters
    deviation_filters = filters.get('deviations_distribution', {})
    for deviation_type, states in deviation_filters.items():
        if states:  # Check if it's not None and not empty
            deviation_column = f"{deviation_type}_deviation"
            for state in states:
                # Build condition to check if the value for a state is not zero
                conditions.append(f"CAST(json_extract({deviation_column}, '$.{state}') AS INTEGER) > 0")

    # Map filter fields to database column names
    field_column_mapping = {
        'symptom': 'u_symptom',
        'impact': 'impact',
        'urgency': 'urgency',
        'priority': 'priority',
        'location': 'location',
        'category': 'category',
    }

    # Handle technical analysis filters
    technical_analysis_filters = filters.get('technical_analysis', {})
    for field, values in technical_analysis_filters.items():
        # Only add the filter if values is not empty or False
        if values and values is not False:
            # Map the field to the correct column name
            column_name = field_column_mapping.get(field, field)
            
            if field in ['impact', 'urgency', 'priority']:
                # Separate numeric and non-numeric values
                numeric_values = [v for v in values if v != '?']
                non_numeric_values = [v for v in values if v == '?']
                conditions_sub = []
                params_sub = []
                if numeric_values:
                    # Extract numeric part from the values
                    numeric_ids = []
                    for v in numeric_values:
                        match = re.match(r'^(\d+)', v)
                        if match:
                            numeric_ids.append(int(match.group(1)))
                        else:
                            # Handle values that don't start with a number
                            continue
                    if numeric_ids:
                        placeholders = ', '.join('?' for _ in numeric_ids)
                        conditions_sub.append(
                            f"CAST(substr({column_name}, 1, instr({column_name}, ' ') - 1) AS INTEGER) IN ({placeholders})"
                        )
                        params_sub.extend(numeric_ids)
                if non_numeric_values:
                    # Handle '?' value
                    conditions_sub.append(f"{column_name} IS NULL OR {column_name} = '?'")
                if conditions_sub:
                    conditions.append('(' + ' OR '.join(conditions_sub) + ')')
                    parameters.extend(params_sub)
            elif field in ['category', 'location', 'symptom']:
                numeric_values = []
                non_numeric_values = []
                for v in values:
                    if v == '?':
                        non_numeric_values.append(v)
                    else:
                        # Extract numeric part from the value
                        match = re.search(r'(\d+)$', v)
                        if match:
                            numeric_values.append(int(match.group(1)))
                        else:
                            # Handle values that don't have numeric part
                            non_numeric_values.append(v)
                conditions_sub = []
                params_sub = []
                if numeric_values:
                    placeholders = ', '.join('?' for _ in numeric_values)
                    conditions_sub.append(
                        f"extract_numeric_end({column_name}) IN ({placeholders})"
                    )
                    params_sub.extend(numeric_values)
                if non_numeric_values:
                    # Handle '?' or other non-numeric values
                    placeholders = ', '.join('?' for _ in non_numeric_values)
                    conditions_sub.append(f"{column_name} IN ({placeholders})")
                    params_sub.extend(non_numeric_values)
                if conditions_sub:
                    conditions.append('(' + ' OR '.join(conditions_sub) + ')')
                    parameters.extend(params_sub)
            else:
                # For other fields, compare directly
                placeholders = ', '.join('?' for _ in values)
                conditions.append(f"{column_name} IN ({placeholders})")
                parameters.extend(values)

    # Handle date range filters
    date_range = filters.get('overview_metrics', {}).get('date_range', {})
    if date_range.get('min_date') and date_range.get('max_date'):    
        conditions.append(f"closed_at BETWEEN ? AND ?")
        parameters.extend([date_range['min_date'], date_range['max_date']])

    # Join all conditions with AND
    return ' AND '.join(conditions), parameters

@eel.expose
def get_tabular_incidents_entries(db_path="../data/incidents.db"):
    """
    Queries the incident_alignment_table for selected incident IDs and the specified compliance metric,
    applying any active filters.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        dict: A Python dictionary containing the incident data, which will be converted to a JavaScript object by Eel.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Register the extract_numeric_end function
        def extract_numeric_end(s):
            import re
            if s is None:
                return None
            m = re.search(r'(\d+)$', s)
            if m:
                return int(m.group(1))
            else:
                return None
        conn.create_function("extract_numeric_end", 1, extract_numeric_end)
        
        # Get all the filters
        filters = get_filter_value()

        # Get incident IDs selection
        incident_ids_selection = get_incident_ids_selection()

        if not incident_ids_selection:
            return []  # Return an empty list if no incident IDs

        # Format the incident IDs for SQL query
        formatted_incident_ids = ', '.join('?' for _ in incident_ids_selection)
        compliance_metric = get_filter_value("filters.compliance_metric")
        incident_id_params = incident_ids_selection

        # Build the base SQL query to select the desired columns
        query = f"""
        SELECT incident_id, {compliance_metric}, opened_at, closed_at, impact, urgency, priority, made_sla, assigned_to, resolved_by, category, location, u_symptom, variant, missing_deviation, repetition_deviation, mismatch_deviation
        FROM incidents_fa_values_table
        WHERE incident_id IN ({formatted_incident_ids})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Add the dynamically constructed filter conditions
        filter_clause, parameters = build_filter_query(filters)
        if filter_clause:
            query += f" AND ( {filter_clause} )"

        
        # Combine parameters
        all_params = incident_id_params + parameters
        
        # Execute the query and load the result into a DataFrame
        df = pd.read_sql_query(query, conn, params=all_params)

        # Convert the DataFrame to a list of dictionaries
        result = df.to_dict(orient='records')

        return result  # Return the list of dictionaries, which Eel will convert to a JavaScript object

    except Exception as e:
        print("tabular_entries.py3")
        print(f"An error occurred: {e}")
        return []  # Return an empty list on error
        
    finally:
        # Close the database connection
        conn.close()

# Example usage
if __name__ == "__main__":
    # Query the incident compliance data and print the JSON result
    filters = get_filter_value()
    filter_clause, parameters = build_filter_query(filters)
    print("tabular_entries.py")
    print(filter_clause)
    print("tabular_entries.py")
    print(parameters)
