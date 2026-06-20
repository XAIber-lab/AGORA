import pandas as pd
import sqlite3
import ast
import eel
import json

from database_filter_variables import *


def parse_dict_column(column):
    """
    Convert string representation of dictionary to an actual dictionary.
    """
    return column.apply(lambda x: ast.literal_eval(x))

@eel.expose
def count_frequencies():
    """
    Counts the frequencies of process states for missing, repetition, and mismatch deviations across all incidents specified in `incident_ids_from_time_period`.

    Returns:
        dict: A Python dictionary with three top-level keys ('missing', 'repetition', 'mismatch'), each mapping to a dictionary of process state codes and their respective counts.
        Example:
            {
                "missing":    {"N": 3, "A": 0, "R": 2, "C": 1, "W": 0},
                "repetition": {"N": 1, "A": 2, "R": 0, "C": 0, "W": 1},
                "mismatch":   {"N": 0, "A": 1, "R": 1, "C": 2, "W": 0}
            }

    Interpretation:
        - Each top-level key ('missing', 'repetition', 'mismatch') refers to a type of process deviation.
        - Each inner dictionary maps process state codes (e.g., 'N', 'A', 'R', 'C', 'W') to the total count of that deviation type for the state, summed over all relevant incidents.
        - The counts represent how many times each state was involved in the respective deviation type (missing, repetition, or mismatch) in the selected incidents.
        - Higher counts indicate more frequent deviations for that state and type.
        - If no incidents are found, all counts will be zero.

    Usage:
        - Use this output to identify which process states are most prone to missing, repetition, or mismatch deviations.
        - The dictionary can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    db_path = "../data/incidents.db"
    conn = sqlite3.connect(db_path)
    try:
        # Prepare the incident IDs for SQL query
        formatted_incident_ids = ', '.join(f"'{incident_id}'" for incident_id in get_incident_ids_selection())

        # Query the necessary data from the database
        query = f"""
        SELECT missing, repetition, mismatch 
        FROM incident_alignment_table 
        WHERE incident_id IN ({formatted_incident_ids})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        df = pd.read_sql_query(query, conn)

        # Initialize counters
        frequencies = {
            'missing': {'N': 0, 'A': 0, 'R': 0, 'C': 0, 'W': 0},
            'repetition': {'N': 0, 'A': 0, 'R': 0, 'C': 0, 'W': 0},
            'mismatch': {'N': 0, 'A': 0, 'R': 0, 'C': 0, 'W': 0}
        }

        # Sum up the counts for each state in each column
        for column in ['missing', 'repetition', 'mismatch']:
            parsed_column = parse_dict_column(df[column])
            for state in frequencies[column].keys():
                frequencies[column][state] = int(parsed_column.apply(lambda x: x[state]).sum())

        return frequencies  # Return the Python dictionary directly

    finally:
        conn.close()

def main():
    try:
        # Count frequencies
        frequencies = count_frequencies()

        # Print results in a cleaned format
        print("count_deviations_db.py")
        print("Frequencies of each state for missing, repetition, and mismatch activities:")
        for activity_type, counts in frequencies.items():
            print("count_deviations_db.py")
            print(f"{activity_type.capitalize()}:")
            for state, count in counts.items():
                print("count_deviations_db.py")
                print(f"  {state}: {count}")
            print("count_deviations_db.py")
            print()  # Add a blank line for readability

    except Exception as e:
        print("count_deviations_db.py")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
