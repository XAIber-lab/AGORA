import sqlite3
from datetime import datetime
import eel

from database_filter_variables import set_incident_ids_selection

@eel.expose
def query_closed_incidents(start_date=None, end_date=None, db_path="../data/incidents.db"):
    try:

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        def standardize_date(date_str):
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        query = "SELECT DISTINCT incident_id FROM event_log_table"
        params = []

        if start_date and end_date:
            start_date_formatted = standardize_date(start_date)
            end_date_formatted = standardize_date(end_date)
            query += """
            WHERE date(substr(closed_at, 1, 10)) 
                  BETWEEN ? AND ?
            """
            params.extend([start_date_formatted, end_date_formatted])
        elif start_date:
            start_date_formatted = standardize_date(start_date)
            query += """
            WHERE date(substr(closed_at, 1, 10)) 
                  >= ?
            """
            params.append(start_date_formatted)
        elif end_date:
            end_date_formatted = standardize_date(end_date)
            query += """
            WHERE date(substr(closed_at, 1, 10)) 
                  <= ?
            """
            params.append(end_date_formatted)

        cursor.execute(query, params)
        incidents = cursor.fetchall()

        # Set global list of selected incidents
        set_incident_ids_selection([incident[0] for incident in incidents])

        cursor.close()
        conn.close()

        return [incident[0] for incident in incidents]

    except Exception as e:
        print("select_time_period_db.py")
        print(f"An error occurred: {e}")
        return []

@eel.expose
def count_unique_incidents(db_path="../data/incidents.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT COUNT(DISTINCT incident_id) FROM event_log_table"

        cursor.execute(query)
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count

    except sqlite3.Error as e:
        print("select_time_period_db.py")
        print(f"An error occurred: {e}")
        return None

@eel.expose
def number_of_closed_incidents_in_time_period(start_date, end_date):
    return len(query_closed_incidents(start_date, end_date))

@eel.expose
def get_min_max_closed_date(db_path="../data/incidents.db"):
    """
    Returns the minimum and maximum closed_at dates from the event_log_table.
    
    Args:
    db_path (str): Path to the SQLite database file.
    
    Returns:
    tuple: A tuple containing the minimum and maximum dates in 'YYYY-MM-DD' format.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT 
            MIN(date(substr(closed_at, 1, 10))), 
            MAX(date(substr(closed_at, 1, 10)))
        FROM event_log_table
        """

        cursor.execute(query)
        min_date, max_date = cursor.fetchone()

        cursor.close()
        conn.close()

        return min_date, max_date

    except sqlite3.Error as e:
        print("select_time_period_db.py")
        print(f"An error occurred: {e}")
        return None, None

def main():
    start_date = '01/06/2016'
    end_date = '01/07/2016'

    incidents = query_closed_incidents(start_date, end_date)
    print("select_time_period_db.py")
    print(f"Number of selected incident IDs: {len(incidents)}")

    print("select_time_period_db.py")
    print(incidents)

if __name__ == "__main__":
    main()
