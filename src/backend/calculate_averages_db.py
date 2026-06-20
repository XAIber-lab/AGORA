import sqlite3
import eel

from database_filter_variables import *

@eel.expose
def calculate_column_average(column_name, db_path="../data/incidents.db", table_name="incidents_fa_values_table"):
    """
    Calculates the average value of a specified column in a given SQLite database table,
    considering only incidents specified by the `get_incident_ids_selection()` function.

    Args:
        column_name (str): The name of the column to calculate the average for.
        db_path (str): Path to the SQLite database file.
        table_name (str): The name of the table in the database.

    Returns:
        float: The average value of the specified column for the selected incidents.
        None: If the column does not exist or any error occurs.

    Interpretation:
        - The function computes the average for the specified column, but only for incidents whose IDs are returned by `get_incident_ids_selection()`.
        - If no incident IDs are selected, the function returns 0.000.
        - If the column does not exist in the table, the function returns None.
        - If any error occurs during database access or calculation, the function returns None.
        - The result is a single float value representing the average, which can be used for analytics, reporting, or further calculations.
        - The output can be directly consumed by JavaScript via Eel for frontend analytics and reporting.

    Usage:
        - Use this function to calculate KPIs or metrics (e.g., average cost, average compliance) for a filtered set of incidents.
        - The function is suitable for dynamic dashboards, reporting, or AI-driven analysis.
    """
    try:
        # Get the list of incident IDs to consider
        incident_ids = get_incident_ids_selection()
        if not incident_ids:
            return 0.000

        # Format incident IDs for SQL query
        formatted_incident_ids = ', '.join(f"'{incident_id}'" for incident_id in incident_ids)

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the specified column exists in the table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        
        if column_name not in columns:
            raise ValueError(f"The column '{column_name}' does not exist in the table '{table_name}'.")

        # Calculate the average value of the specified column for the selected incidents
        query = f"""
        SELECT AVG({column_name}) 
        FROM {table_name}
        WHERE incident_id IN ({formatted_incident_ids})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        cursor.execute(query)
        average_value = cursor.fetchone()[0]

        # Close the connection
        cursor.close()
        conn.close()

        return average_value

    except sqlite3.Error as e:
        print("calculate_averages_db.py")
        print(f"An error occurred with the database: {e}")
        return None
    except Exception as e:
        print("calculate_averages_db.py")
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    column_name = "cost"  # Replace with the desired column name
    average_value = calculate_column_average(column_name)
    
    if average_value is not None:
        print("calculate_averages_db.py")
        print(f"The average value of '{column_name}' for the selected incidents is: {average_value}")
    else:
        print("calculate_averages_db.py")
        print(f"Could not calculate the average value for '{column_name}'.")
