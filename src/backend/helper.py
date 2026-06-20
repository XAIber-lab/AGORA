import sqlite3

def update_incidents_with_opened_at(db_path="../data/incidents.db"):
    """
    Update the incidents_fa_values_table with the earliest opened_at value from the event_log_table.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the earliest opened_at time for each incident_id from event_log_table
        cursor.execute("""
            SELECT incident_id, MIN(opened_at) AS earliest_opened_at
            FROM event_log_table
            GROUP BY incident_id
        """)
        incident_opened_times = cursor.fetchall()

        # Update the incidents_fa_values_table with the earliest opened_at time
        for incident_id, earliest_opened_at in incident_opened_times:
            cursor.execute("""
                UPDATE incidents_fa_values_table
                SET opened_at = ?
                WHERE incident_id = ?
            """, (earliest_opened_at, incident_id))

        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print("helper.py")
        print("Opened_at values successfully updated in incidents_fa_values_table.")

    except Exception as e:
        print("helper.py")
        print(f"An error occurred: {e}")

def copy_deviation_columns(db_path="../data/incidents.db"):
    """
    Copies the content of the 'missing', 'repetition', and 'mismatch' columns from the 
    'incident_alignment_table' into the 'missing_deviation', 'repetition_deviation', and 
    'mismatch_deviation' columns of the 'incidents_fa_values_table'.
    
    Args:
        db_path (str): Path to the SQLite database file.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL query to update the incidents_fa_values_table
        update_query = """
        UPDATE incidents_fa_values_table
        SET 
            missing_deviation = (
                SELECT missing 
                FROM incident_alignment_table 
                WHERE incident_alignment_table.incident_id = incidents_fa_values_table.incident_id
            ),
            repetition_deviation = (
                SELECT repetition 
                FROM incident_alignment_table 
                WHERE incident_alignment_table.incident_id = incidents_fa_values_table.incident_id
            ),
            mismatch_deviation = (
                SELECT mismatch 
                FROM incident_alignment_table 
                WHERE incident_alignment_table.incident_id = incidents_fa_values_table.incident_id
            )
        """

        # Execute the update query
        cursor.execute(update_query)

        # Commit the changes
        conn.commit()
        print("helper.py")
        print("Deviation columns updated successfully.")

    except Exception as e:
        print("helper.py")
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

# Example usage
if __name__ == "__main__":
    copy_deviation_columns()
