import sqlite3
import pandas as pd
import json
import eel
from database_filter_variables import *

# Function to count deviations from JSON-like strings
def count_deviations(deviation_str):
    """
    Converts the JSON-like string to a dictionary and returns the deviation counts per state.
    """
    if deviation_str:
        # Convert single quotes to double for JSON compatibility
        deviation_dict = json.loads(deviation_str.replace("'", '"'))  
        return deviation_dict
    return {}

@eel.expose
def get_compliance_per_state_per_incident(db_path="../data/incidents.db"):
    """
    Retrieves the compliance per state for all incidents within the specified date range, 
    aggregating missing, repetition, and mismatch deviations.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        str: A JSON string containing compliance per state for each incident within the date range.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Get filters from the global filter variables
        filters = get_filter_value()
        date_range = filters.get('filters', {}).get('overview_metrics', {}).get('date_range', {})
        
        if not date_range.get('min_date') or not date_range.get('max_date'):
            return json.dumps({'error': 'Date range not specified'})

        # Extract min and max dates from the filters
        min_date = date_range['min_date']
        max_date = date_range['max_date']

        # Build the base query to fetch incidents within the date range
        query = """
            SELECT 
                incident_id,
                fitness,
                cost,
                variant,
                missing_deviation,
                repetition_deviation,
                mismatch_deviation,
                closed_at
            FROM incidents_fa_values_table 
            WHERE closed_at BETWEEN ? AND ?
        """

        # Add the 'whatif_analysis' exclusion clause if applicable
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Add the ORDER BY clause at the end
        query += " ORDER BY closed_at ASC"
                
        # Load data into a DataFrame
        df = pd.read_sql_query(query, conn, params=(min_date, max_date))

        if df.empty:
            return json.dumps({'error': 'No incidents found within the specified date range'})

        # Initialize a list to hold the results for each incident
        results = []

        # Iterate through each incident to calculate compliance per state
        for _, row in df.iterrows():
            # Initialize a dictionary to hold the aggregated deviations per state for the current incident
            total_deviations_per_state = {}

            # Store the fitness value
            fitness = round(row['fitness'], 2)  # Round fitness to 2 decimal places
            cost = round(row['cost'], 2)

            # Aggregate deviations from missing, repetition, and mismatch deviations
            missing_deviations = count_deviations(row['missing_deviation'])
            repetition_deviations = count_deviations(row['repetition_deviation'])
            mismatch_deviations = count_deviations(row['mismatch_deviation'])

            total_deviations_per_type_per_state = {"missing": missing_deviations, "repetition": repetition_deviations, "mismatch": mismatch_deviations}

            # Sum up all deviations per state
            for state, count in missing_deviations.items():
                total_deviations_per_state[state] = total_deviations_per_state.get(state, 0) + count

            for state, count in repetition_deviations.items():
                total_deviations_per_state[state] = total_deviations_per_state.get(state, 0) + count

            for state, count in mismatch_deviations.items():
                total_deviations_per_state[state] = total_deviations_per_state.get(state, 0) + count

            # Calculate the total number of deviations across all states
            total_deviations = sum(total_deviations_per_state.values())

            # Calculate the total number of events from the variant column
            variant = row['variant']
            # Count the total events without separating between states
            total_events = len(variant.split())

            if row['incident_id'] == "INC0030204":
                print("Total events:")
                print(total_events)

            compliance_metric = get_filter_value("filters.compliance_metric")
            # Calculate compliance per state
            if (compliance_metric == "fitness"):
                compliance_per_state = calculate_compliance_per_state(total_deviations_per_state, total_deviations)
                for state in compliance_per_state:    
                    compliance_per_state[state] *=  fitness
            else:
                compliance_per_state = calculate_cost_per_state(total_deviations_per_type_per_state, total_events, get_filter_value("filters.cost_function"))


            # Prepare the result dictionary for the current incident
            incident_result = {
                'incident_id': row['incident_id'],
                'fitness': fitness,
                'cost': cost,
                'closed_at': row['closed_at'],
                'total_deviations_per_state': {state: round(count, 2) for state, count in total_deviations_per_state.items()},
                'total_deviations': round(total_deviations, 2),
                'compliance_per_state': {state: round(score, 2) for state, score in compliance_per_state.items()}
            }

            if incident_result['incident_id'] == "INC0030204":
                print(incident_result)

            # Append the result for the current incident to the results list
            results.append(incident_result)

        return json.dumps(results)

    except Exception as e:
        print("compliance_metric_per_state.py")
        print(f"An error occurred: {e}")
        return json.dumps({'error': str(e)})

    finally:
        # Close the database connection
        if conn:
            conn.close()

def calculate_compliance_per_state(deviations_per_state, total_deviations):
    """
    Calculates the compliance score per state based on the total deviations.

    Args:
        deviations_per_state (dict): Dictionary with the total deviations per state.
        total_deviations (int): Total number of deviations across all states.

    Returns:
        dict: A dictionary with the compliance score per state.
    """
    compliance_scores = {}
    total_compliance = 0

    # Calculate compliance score for each state
    for state, deviations in deviations_per_state.items():
        # Compliance calculation: 1/5 * (1 - (total_deviations_state / total_deviations))
        compliance_score = 0.2 * (1 - (deviations / total_deviations))  if total_deviations != 0 else 0.2
        compliance_scores[state] = compliance_score
        total_compliance += compliance_score

    # Calculate normalization factor
    normalization_factor = 1 / total_compliance if total_compliance != 0 else 0

    # Normalize compliance scores
    for state in compliance_scores:
        compliance_scores[state] *= normalization_factor
    return compliance_scores

def calculate_cost_per_state(deviations_per_type_per_state, total_events, cost_function):
    """
    Calculates the non-compliance cost per state based on deviations and a cost function.

    Args:
        deviations_per_type_per_state (dict): Nested dict with deviation counts per type and state.
        total_events (int): Total number of events in the incident.
        cost_function (dict): Cost weights for each deviation type and state.

    Returns:
        dict: A dictionary mapping each process state to its non-compliance cost.
        Example:
            {"N": 0.12, "A": 0.08, ...}

    Interpretation:
        - Each key is a process state code.
        - Each value is the calculated non-compliance cost for that state.
        - Used for cost-based compliance analysis.
    """
    # Initialize total cost for the process
    non_compliance_cost_per_state = {}

    thresholds = {"missing": False, "repetition": False, "mismatch": False}

    # Loop through all process states of the reference process
    for state in cost_function["missing"]:
        # Set of missing deviations
        deviations_missing = deviations_per_type_per_state["missing"][state]
        
        # Set of repetition deviations
        deviations_repetition = deviations_per_type_per_state["repetition"][state]
        
        # Set of mismatch deviations
        deviations_mismatch = deviations_per_type_per_state["mismatch"][state]
        
        
        # Initialize the non-compliance cost for the current state
        state_non_compliance_cost = 0
        
        # Calculate cost for missing deviations
        if deviations_missing * cost_function["missing"][state] > 1:
            state_non_compliance_cost += 1 * cost_function["cost"]["missing"]
        else:
            state_non_compliance_cost += deviations_missing * cost_function["missing"][state] * cost_function["cost"]["missing"]
        
        # Calculate cost for repetition deviations (normalized by total_events)
        if deviations_repetition * cost_function["repetition"][state] > 1:
            state_non_compliance_cost += 1 * cost_function["cost"]["repetition"]
        else:
            state_non_compliance_cost += deviations_repetition * cost_function["repetition"][state] * cost_function["cost"]["repetition"] / total_events
        
        # Calculate cost for mismatch deviations (normalized by total_events)
        if deviations_mismatch * cost_function["mismatch"][state] > 1:
            state_non_compliance_cost += 1 * cost_function["cost"]["mismatch"]
        else:
            state_non_compliance_cost += deviations_mismatch * cost_function["mismatch"][state] * cost_function["cost"]["mismatch"] / total_events
        
        # Add the non-compliance cost of this state to the dictionary
        non_compliance_cost_per_state[state] = state_non_compliance_cost
    
    # Return non-compliance cost per state
    return non_compliance_cost_per_state

@eel.expose
def get_average_compliance_per_state(db_path="../data/incidents.db"):
    """
    Calculates and returns the average process compliance value for each process state across all incidents closed within the currently selected date range.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        dict: A Python dictionary mapping each process state (str) to its average compliance value (float) across all relevant incidents.

    Interpretation:
        - Each key is a process state name as defined in the reference model.
        - Each value is the average compliance score for that state, calculated over all incidents closed in the selected date range.
        - The compliance score for a state reflects how closely the process execution for that state matched the reference model, considering deviations such as missing, repetition, and mismatch.
        - Higher values (closer to 1.0) indicate better compliance (fewer or less severe deviations); lower values indicate more frequent or severe deviations from the reference process in that state.
        - If no incidents are found in the date range, the function returns {'error': <error_message>}.

    Usage:
        - Use this output to visualize or compare process compliance for each state, identify weak points in process execution, or track improvements over time.
        - The dictionary can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    try:
        # Get compliance data for each incident
        compliance_data = get_compliance_per_state_per_incident(db_path)

        if isinstance(compliance_data, str):
            compliance_data = json.loads(compliance_data)

        if 'error' in compliance_data:
            return {'error': compliance_data['error']}

        # Initialize a dictionary to sum compliance scores per state
        compliance_sum_per_state = {}
        incident_count = 0

        # Iterate through each incident's compliance data
        for incident in compliance_data:
            incident_count += 1
            for state, compliance in incident['compliance_per_state'].items():
                compliance_sum_per_state[state] = compliance_sum_per_state.get(state, 0) + compliance

        # Calculate the average compliance per state
        average_compliance_per_state = {
            state: round(compliance_sum / incident_count, 2)
            for state, compliance_sum in compliance_sum_per_state.items()
        }

        return average_compliance_per_state  # Return a Python dictionary directly

    except Exception as e:
        print("compliance_metric_per_state.py")
        print(f"An error occurred: {e}")
        return {'error': str(e)}  # Return an error as a Python dictionary


import sqlite3
import pandas as pd
import json
import eel
from database_filter_variables import *

# ...existing code...

@eel.expose
def update_cost_with_compliance_per_state(db_path="../data/incidents.db"):
    """
    Updates the 'cost' column in the incidents_fa_values_table for each incident
    with the sum of the compliance_per_state values as calculated by get_compliance_per_state_per_incident.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        dict: A summary of the update operation, including the number of updated incidents.
    """
    try:
        # Get compliance data for each incident
        compliance_data = get_compliance_per_state_per_incident(db_path)
        if isinstance(compliance_data, str):
            compliance_data = json.loads(compliance_data)
        if 'error' in compliance_data:
            return {'error': compliance_data['error']}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        updated_count = 0

        for incident in compliance_data:
            incident_id = incident['incident_id']
            # The new cost is the sum of compliance_per_state values
            new_cost = sum(incident['compliance_per_state'].values())
            # Update the cost in the database
            cursor.execute(
                "UPDATE incidents_fa_values_table SET cost = ? WHERE incident_id = ?",
                (new_cost, incident_id)
            )
            updated_count += cursor.rowcount

        conn.commit()
        conn.close()
        return {"updated_incidents": updated_count}

    except Exception as e:
        print("compliance_metric_per_state.py")
        print(f"An error occurred during cost update: {e}")
        return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    # Example call to the exposed function
    print(update_cost_with_compliance_per_state())