import sqlite3
import json
import eel

@eel.expose
def get_global_progress():
    """
    Connects to the SQLite database and calculates the progress of security controls
    for each operator. Returns the results as a JSON object (dictionary).
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('../data/security_controls.db')
    cursor = conn.cursor()

    # SQL query to calculate the progress per operator_id
    cursor.execute("""
    SELECT operator_id,
           SUM(CASE status
               WHEN 'covered' THEN 1.0
               WHEN 'partially covered' THEN 0.5
               ELSE 0 END) / COUNT(*) AS progress
    FROM security_controls
    GROUP BY operator_id;
    """)

    # Fetch the results from the query
    results = cursor.fetchall()

    # Prepare the results as a dictionary (JSON object)
    progress_dict = {}
    for operator_id, progress in results:
        # Convert operator_id to string, handle None values
        operator_name = str(operator_id) if operator_id is not None else "Unassigned"
        progress_dict[operator_name] = progress

    # Close the database connection
    conn.close()

    # Return the dictionary (JSON object)
    return json.dumps(progress_dict)

# Example usage
if __name__ == "__main__":
    # Get the progress data
    progress = get_global_progress()
    # Convert the dictionary to a JSON-formatted string and print
    print("global_progess.py")
    print(progress)
