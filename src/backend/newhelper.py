import sqlite3
import json

def convert_minutes_to_days_hours_minutes(minutes):
    """
    Convert minutes into a dictionary with days, hours, and minutes.
    """
    days = minutes // (24 * 60)
    hours = (minutes % (24 * 60)) // 60
    minutes = minutes % 60
    return {"days": days, "hours": hours, "minutes": minutes}

def get_mean_cost_total_and_state_times(db_path="../data/incidents.db"):
    """
    Query incidents_fa_values_table for incidents within January 2017, excluding specific incident IDs, 
    and calculate the mean for costTotal and state times from event_interval_minutes.
    """
    try:
        # List of incident IDs to exclude
        excluded_incident_ids = [
            "INC0023564", "INC0032737", "INC0099711", "INC0099860", "INC0100609", 
            "INC0102711", "INC0102713", "INC0102715", "INC0102891", "INC0102978",
            "INC0103724", "INC0103919", "INC0104208", "INC0105551", "INC0106051",
            "INC0107346", "INC0107571", "INC0107645", "INC0108046", "INC0108374",
            "INC0112185", "INC0112559"
        ]

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Convert the list of excluded incident IDs into a format suitable for the SQL query
        placeholders = ','.join(['?' for _ in excluded_incident_ids])

        # Query to fetch the costTotal and event_interval_minutes for incidents in January 2017 excluding specific incidents
        query = f"""
            SELECT cost, event_interval_minutes
            FROM incidents_fa_values_table
            WHERE closed_at >= '2017-01-01' AND closed_at < '2017-02-01'
            AND incident_id IN ({placeholders})
        """

        cursor.execute(query, excluded_incident_ids)
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # If no results, return a message
        if not results:
            return json.dumps({"message": "No incidents found for January 2017"})

        # Extract costTotal values and calculate the mean
        cost_totals = [row[0] for row in results if row[0] is not None]
        if not cost_totals:
            return json.dumps({"message": "No costTotal data available for January 2017"})
        mean_cost_total = sum(cost_totals) / len(cost_totals)

        # Initialize variables for storing state times
        state_totals = {'N': 0, 'A': 0, 'R': 0, 'C': 0, 'W': 0}
        state_counts = {'N': 0, 'A': 0, 'R': 0, 'C': 0, 'W': 0}

        # Process state times from event_interval_minutes
        for row in results:
            event_interval_minutes = row[1]
            if event_interval_minutes:
                state_times = json.loads(event_interval_minutes)  # Assuming the column stores JSON data
                for state, time in state_times.items():
                    if time is not None:
                        state_totals[state] += time
                        state_counts[state] += 1

        # Calculate average state times and convert to days, hours, and minutes
        average_state_times = {
            state: convert_minutes_to_days_hours_minutes(state_totals[state] / state_counts[state])
            if state_counts[state] > 0 else None
            for state in state_totals
        }

        # Return the mean costTotal and average state times in JSON format
        return json.dumps({
            "mean_costTotal": mean_cost_total,
            "average_state_times": average_state_times
        })

    except Exception as e:
        print("new_helper.py")
        print(f"An error occurred: {e}")
        return json.dumps({"error": str(e)})

# Example usage
if __name__ == "__main__":
    result_json = get_mean_cost_total_and_state_times()
    print("new_helper.py")
    print(result_json)
