import sqlite3
from datetime import datetime, timedelta
import json  # Import JSON to store the data in JSON format
from database_filter_variables import *
from define_mapping import read_mapping_from_file
import eel

def get_event_state_intervals(incident_id, db_path="../data/incidents.db"):
    """
    Retrieve the first and last occurrence of each state (N, A, W, R, C) for a given incident_id.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
        SELECT event, sys_updated_at
        FROM event_log_table 
        WHERE incident_id = ?
        ORDER BY sys_updated_at ASC
        """
        cursor.execute(query, (incident_id,))
        events = cursor.fetchall()
        cursor.close()
        conn.close()

        state_intervals = {}
        state_order = ['N', 'A', 'W', 'R', 'C']
        start_index = 0

        for state in state_order:
            first_occurrence = None
            last_occurrence = None
            last_occurrence_index = None

            for i in range(start_index, len(events)):
                event, timestamp = events[i]
                if event == state:
                    if first_occurrence is None:
                        first_occurrence = timestamp
                    last_occurrence = timestamp
                    last_occurrence_index = i

            if first_occurrence and last_occurrence:
                state_intervals[state] = (first_occurrence, last_occurrence)
                start_index = last_occurrence_index + 1

        return state_intervals

    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred: {e}")
        return {}

def format_timedelta(td):
    """
    Format a timedelta object as 'Xd, Xh, Xmin'.
    """
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days}d, {hours}h, {minutes}min"

def calculate_time_in_all_states(state_intervals):
    """
    Calculate the total time an incident was in each state.
    """
    try:
        states = list(state_intervals.keys())
        time_in_states = {}

        for i, state in enumerate(states):
            start_time = datetime.strptime(state_intervals[state][0], "%Y-%m-%d %H:%M:%S")
            if i + 1 < len(states):
                next_state = states[i + 1]
                next_start_time = datetime.strptime(state_intervals[next_state][0], "%Y-%m-%d %H:%M:%S")
            else:
                next_start_time = datetime.strptime(state_intervals[state][1], "%Y-%m-%d %H:%M:%S")

            time_in_state = next_start_time - start_time
            time_in_states[state] = format_timedelta(time_in_state)

        return time_in_states
    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred: {e}")
        return {}
    
def calculate_transition_times(state_intervals):
    """
    Calculate the time between state transitions.
    """
    try:
        states = list(state_intervals.keys())
        transition_times = {}

        for i, state in enumerate(states):
            current_end_time = datetime.strptime(state_intervals[state][1], "%Y-%m-%d %H:%M:%S")

            if i + 1 < len(states):
                next_state = states[i + 1]
                next_start_time = datetime.strptime(state_intervals[next_state][0], "%Y-%m-%d %H:%M:%S")
                transition_time = next_start_time - current_end_time
                transition_key = f"{state}->{next_state}"
                transition_times[transition_key] = format_timedelta(transition_time)
                

        return transition_times

    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred: {e}")
        return {}

def format_minutes_to_timedelta(minutes):
    """Convert minutes to a formatted timedelta string."""
    td = timedelta(minutes=minutes)
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes = remainder // 60
    return f"{days}d, {hours}h, {minutes}min"

@eel.expose   
def get_average_state_times(db_path="../data/incidents.db"):
    """
    Calculates and returns the average time spent in each process state across all incidents closed within the currently selected date range.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        str (JSON): A JSON string representing a dictionary mapping each process state (str) to its average time spent (str, formatted as 'Xd, Xh, Xmin').
        Example:
            {
                "Investigation": "0d, 2h, 15min",
                "Containment": "0d, 1h, 40min",
                "Eradication": "0d, 3h, 5min",
                ...
            }

    Interpretation:
        - Each key is a process state name as defined in the reference model.
        - Each value is the average time spent in that state, calculated over all incidents closed in the selected date range.
        - The time is formatted as days, hours, and minutes (e.g., '0d, 2h, 15min').
        - If no incidents are found in the date range, the function returns an empty dictionary as a JSON string.

    Usage:
        - Use this output to visualize or compare how long incidents typically spend in each state, identify bottlenecks, or track improvements over time.
        - The JSON string can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch incident IDs selection
        incident_ids = tuple(get_incident_ids_selection())

        # Fetch state times as JSON and convert them to minutes
        query = """
            SELECT event_interval_minutes 
            FROM incidents_fa_values_table 
            WHERE incident_id IN ({placeholders})
        """

        # Add the 'whatif_analysis' exclusion clause if it exists
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Now finalize the query by replacing the placeholders for incident IDs
        placeholders = ','.join(['?'] * len(incident_ids))
        query = query.format(placeholders=placeholders)


        # Execute the query with the incident_ids as parameters
        cursor.execute(query, incident_ids)

        state_times_list = cursor.fetchall()

        total_time_in_states = {}
        count_in_states = {}

        for state_times_json in state_times_list:
            state_times = json.loads(state_times_json[0])  # Convert JSON string back to dictionary

            for state, minutes in state_times.items():
                if state not in total_time_in_states:
                    total_time_in_states[state] = 0
                    count_in_states[state] = 0

                total_time_in_states[state] += minutes
                count_in_states[state] += 1

        # Calculate average time in each state
        average_time_in_states = {}
        for state in total_time_in_states:
            if count_in_states[state] > 0:
                avg_minutes = total_time_in_states[state] / count_in_states[state]
                average_time_in_states[state] = format_minutes_to_timedelta(avg_minutes)

        cursor.close()
        conn.close()

        # Read the state mapping
        state_mapping = read_mapping_from_file()

        # Order the results based on the state mapping
        ordered_average_time_in_states = {
            state: average_time_in_states.get(state_mapping[state_key], "N/A")
            for state_key, state in state_mapping.items()
        }

        return json.dumps(ordered_average_time_in_states)

    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred while fetching average state times: {e}")
        return {}

@eel.expose
def get_average_transition_times(db_path="../data/incidents.db"):
    """
    Calculates and returns the average time taken to transition between each pair of process states across all incidents closed within the currently selected date range.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        str (JSON): A JSON string representing a dictionary mapping each state transition (str, e.g. 'Investigation->Containment') to its average transition time (str, formatted as 'Xd, Xh, Xmin').
        Example:
            {
                "Investigation->Containment": "0d, 0h, 30min",
                "Containment->Eradication": "0d, 1h, 10min",
                ...
            }

    Interpretation:
        - Each key is a state transition, formatted as 'StateA->StateB' according to the reference model.
        - Each value is the average time taken to transition from StateA to StateB, calculated over all incidents closed in the selected date range.
        - The time is formatted as days, hours, and minutes (e.g., '0d, 0h, 30min').
        - If no incidents are found in the date range, the function returns an empty dictionary as a JSON string.

    Usage:
        - Use this output to visualize or compare how long transitions between states typically take, identify delays or bottlenecks, or track improvements over time.
        - The JSON string can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch incident IDs selection
        incident_ids = tuple(get_incident_ids_selection())

        query = """
            SELECT transition_interval_minutes 
            FROM incidents_fa_values_table 
            WHERE incident_id IN ({placeholders})
        """

        # Add the 'whatif_analysis' exclusion clause if it exists
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        # Now finalize the query by replacing the placeholders for incident IDs
        placeholders = ','.join(['?'] * len(incident_ids))
        query = query.format(placeholders=placeholders)

        # Execute the query with the incident_ids as parameters
        cursor.execute(query, incident_ids)

        transition_times_list = cursor.fetchall()

        total_transition_times = {}
        count_transition_times = {}

        for transition_times_json in transition_times_list:
            transition_times = json.loads(transition_times_json[0])  # Convert JSON string back to dictionary

            for transition, minutes in transition_times.items():
                if transition not in total_transition_times:
                    total_transition_times[transition] = 0
                    count_transition_times[transition] = 0

                total_transition_times[transition] += minutes
                count_transition_times[transition] += 1

        # Calculate average transition time between states
        average_transition_times = {}
        for transition in total_transition_times:
            if count_transition_times[transition] > 0:
                avg_minutes = total_transition_times[transition] / count_transition_times[transition]
                average_transition_times[transition] = format_minutes_to_timedelta(avg_minutes)

        cursor.close()
        conn.close()

        # Read the state mapping
        state_mapping = read_mapping_from_file()

        # Order the transition results based on the state mapping
        ordered_average_transition_times = {}
        for state_key, state in state_mapping.items():
            for next_state_key, next_state in state_mapping.items():
                transition_key = f"{state}->{next_state}"
                if transition_key in average_transition_times:
                    ordered_average_transition_times[transition_key] = average_transition_times[transition_key]

        return json.dumps(ordered_average_transition_times)

    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred while fetching average transition times: {e}")
        return {}

def calculate_time_to_last_occurrence(db_path="../data/incidents.db"):
    """
    Calculate the time to the last occurrence of each state for every incident.
    Store the result in the `time_to_states_last_occurrence` column in `incidents_fa_values_table`.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all incident IDs and opened_at from incidents_fa_values_table
        cursor.execute("SELECT incident_id, opened_at FROM incidents_fa_values_table")
        incidents = cursor.fetchall()

        total_incidents = len(incidents)
        processed_incidents = 0

        for incident_id, opened_at in incidents:
            processed_incidents += 1
            print("time_between_states_and_transitions.py")
            print(f"Processing incident {processed_incidents}/{total_incidents} (ID: {incident_id})")

            # Get the state intervals for the current incident
            state_intervals = get_event_state_intervals(incident_id, db_path)

            if not state_intervals:
                print("time_between_states_and_transitions.py")
                print(f"Skipping incident {incident_id} due to missing state intervals.")
                continue

            # Convert the opened_at string to a datetime object
            opened_at_datetime = datetime.strptime(opened_at, "%Y-%m-%d %H:%M:%S")

            # Calculate the time to the last occurrence of each state
            time_to_states_last_occurrence = {}
            for state, interval in state_intervals.items():
                last_occurrence = datetime.strptime(interval[1], "%Y-%m-%d %H:%M:%S")
                time_to_last_occurrence = last_occurrence - opened_at_datetime
                minutes = int(time_to_last_occurrence.total_seconds() // 60)
                time_to_states_last_occurrence[f"TT{state}"] = minutes

            # Convert the dictionary to a JSON string
            time_to_states_last_occurrence_json = json.dumps(time_to_states_last_occurrence)

            # Update the incidents_fa_values_table with the calculated times
            cursor.execute("""
                UPDATE incidents_fa_values_table
                SET time_to_states_last_occurrence = ?
                WHERE incident_id = ?
            """, (time_to_states_last_occurrence_json, incident_id))

            # Commit after each incident to ensure data is saved progressively
            conn.commit()

        cursor.close()
        conn.close()
        print("time_between_states_and_transitions.py")
        print("Time to last occurrence of each state successfully calculated and stored.")

    except Exception as e:
        print("time_between_states_and_transitions.py")
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    state_intervals = get_event_state_intervals('INC0000084')
    print("time_between_states_and_transitions.py")
    print(state_intervals)
    print("time_between_states_and_transitions.py")
    print(get_average_state_times())
    print("time_between_states_and_transitions.py")
    print(get_average_transition_times())
