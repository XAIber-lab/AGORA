import pandas as pd
import sqlite3
from collections import Counter
import eel
from database_filter_variables import *

def process_alignment(alignment):
    """Extracts relevant events and creates a variant."""
    try:
        events = alignment.split(';')
        return ' '.join([event[3] for event in events if event.startswith('[S]') or event.startswith('[L]')])
    except Exception as e:
        print("common_variants_db.py")
        print(f"Failed processing alignment {alignment}: {e}")
        return ""

def analyze_alignments(df):
    """Analyzes alignments in a DataFrame and returns sorted variants."""
    try:
        df['processed'] = df['alignment'].apply(process_alignment)
        variant_counts = Counter(df['processed'])
        return sorted(variant_counts.items(), key=lambda x: x[1], reverse=True)
    except Exception as e:
        print("common_variants_db.py")
        print(f"Error during analysis: {e}")
        return []

@eel.expose
def get_sorted_variants_from_db():
    """
    Queries the incident_alignment_table in the SQLite database for alignments of selected incidents,
    processes the alignment data to extract process variants, and returns a sorted list of variants by frequency.

    Returns:
        list of tuples: Each tuple is (variant, frequency), sorted from most frequent to least frequent.
        Example:
            [
                ("N R C", 12),
                ("N A R C", 8),
                ("N R R C", 3),
                ...
            ]

    Interpretation:
        - Each variant is a string representing the sequence of process states (e.g., "N R C") as extracted from the alignment data.
        - The frequency is the number of incidents in which that variant occurred.
        - The list is sorted in descending order by frequency, so the most common variants appear first.
        - Only incidents selected by get_incident_ids_selection() and filtered by what-if analysis are included.
        - If no incidents are found, the function returns an empty list.

    Usage:
        - Use this output to identify the most common process flows (variants) in the selected incident set.
        - The result can be visualized as a ranked list, bar chart, or used for further process mining and compliance analysis.
        - The output can be directly consumed by JavaScript via Eel for frontend analytics and reporting.
    """
    try:
        db_path = "../data/incidents.db"
        conn = sqlite3.connect(db_path)

        # Format the incident IDs for SQL query
        formatted_incident_ids = ', '.join(f"'{incident_id}'" for incident_id in get_incident_ids_selection())

        # Build the base SQL query to select the desired columns
        query = f"""
        SELECT alignment
        FROM incident_alignment_table
        WHERE incident_id IN ({formatted_incident_ids})
        """

        # Add the 'whatif_analysis' exclusion clause
        whatif_clause = apply_whatif_analysis_filter()
        if whatif_clause:
            query += f" AND ( {whatif_clause} )"

        df = pd.read_sql(query, conn)
        conn.close()
        return analyze_alignments(df)
    except Exception as e:
        print("common_variants_db.py")
        print(f"An error occurred while querying the database: {e}")
        return []
    
def update_variants_in_db():
    """
    Queries all incident IDs and their alignments from the incident_alignment_table, processes the alignment data
    to calculate the variant for each incident ID, and updates the variant column in the incidents_fa_values_table
    with the calculated variant.
    """
    try:
        db_path = "../data/incidents.db"
        conn = sqlite3.connect(db_path)

        # Query all incident_id and alignment data from incident_alignment_table
        query = "SELECT incident_id, alignment FROM incident_alignment_table"
        df = pd.read_sql(query, conn)

        # Process each alignment to calculate the variant
        df['variant'] = df['alignment'].apply(process_alignment)

        # Update the variant in the incidents_fa_values_table
        for _, row in df.iterrows():
            update_query = """
            UPDATE incidents_fa_values_table
            SET variant = ?
            WHERE incident_id = ?
            """
            conn.execute(update_query, (row['variant'], row['incident_id']))

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        
        print("common_variants_db.py")
        print("Variants updated successfully in the database.")
    except Exception as e:
        print(f"An error occurred during the update process: {e}")

# Example usage
if __name__ == "__main__":
    sorted_variants = get_sorted_variants_from_db()
    print("common_variants_db.py")
    print(process_alignment("[S]N;[M]A;[S]R;[L]R;[S]C;"))
    update_variants_in_db()
