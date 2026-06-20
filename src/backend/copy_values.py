import sqlite3

def transfer_event_log_data(db_path="../data/incidents.db"):
    """
    Transfers data from the event_log_table to the incidents_fa_values_table.
    For each incident_id, the latest event data will be used to update the corresponding row in incidents_fa_values_table.
    
    Args:
        db_path (str): Path to the SQLite database file.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the most recent event for each incident_id from event_log_table
        query = """
        SELECT incident_id, location, category, subcategory, u_symptom, impact, urgency, priority, assignment_group,
               assigned_to, resolved_by, made_sla
        FROM event_log_table
        WHERE ROWID IN (
            SELECT MAX(ROWID)
            FROM event_log_table
            GROUP BY incident_id
        )
        """
        cursor.execute(query)
        event_data = cursor.fetchall()

        # Iterate over the event data and update the corresponding incident in incidents_fa_values_table
        update_query = """
        UPDATE incidents_fa_values_table
        SET location = ?, category = ?, subcategory = ?, u_symptom = ?, impact = ?, urgency = ?, priority = ?,
            assignment_group = ?, assigned_to = ?, resolved_by = ?, made_sla = ?
        WHERE incident_id = ?
        """

        for row in event_data:
            incident_id = row[0]
            # Get the other fields from the row
            location, category, subcategory, u_symptom, impact, urgency, priority, assignment_group, \
                assigned_to, resolved_by, made_sla = row[1:]

            # Execute the update for each incident_id
            cursor.execute(update_query, (location, category, subcategory, u_symptom, impact, urgency, priority,
                                          assignment_group, assigned_to, resolved_by, made_sla, incident_id))

        # Commit the changes
        conn.commit()
        print("copy_values.py")
        print(f"Data transferred successfully for {len(event_data)} incidents.")

    except Exception as e:
        print("copy_values.py")
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        if conn:
            conn.close()

# Run the transfer
if __name__ == "__main__":
    transfer_event_log_data()
