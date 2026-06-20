import sqlite3
import eel
import json
from database_filter_variables import *

@eel.expose
def insert_assessment_result(name, entry_type, incident_ids_list, control_id, status, db_path="../data/security_controls.db"):
    """
    Inserts a new record into the assessment_results table and links the assessment result to the 
    security control by appending the name to the evidence field.
    Also updates the status of the security control.

    Parameters:
    name (str): The name of the assessment result.
    entry_type (str): The type of the assessment result ('finding', 'area of concern', 'non-conformaty').
    incident_ids_list (str): A comma-separated string of incident IDs.
    control_id (int): The ID of the security control to link the evidence to.
    status (str): The new status for the security control ('covered', 'partially covered', 'not covered').
    db_path (str): Path to the SQLite database.
    """
    try:
        # Check if the entry_type is valid
        if entry_type not in ('finding', 'area of concern', 'non-conformity'):
            raise ValueError("Invalid entry type. Must be one of: 'finding', 'area of concern', 'non-conformity'.")

        # Validate the status
        valid_statuses = ['covered', 'partially covered', 'not covered']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Valid statuses are: {valid_statuses}")

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the record into the assessment_results table
        cursor.execute("""
            INSERT INTO assessment_results (name, type, incident_ids_list) 
            VALUES (?, ?, ?)
        """, (name, entry_type, incident_ids_list))

        # Fetch the ID of the newly inserted assessment result
        assessment_result_id = cursor.lastrowid

        # Fetch the current evidence value for the security control
        cursor.execute("SELECT evidence FROM security_controls WHERE id = ?", (control_id,))
        result = cursor.fetchone()
        current_evidence = result[0] if result else ""

        # Append the new assessment name to the current evidence, separating by ';' if necessary
        if current_evidence:
            updated_evidence = current_evidence + ";" + name
        else:
            updated_evidence = name

        # Update the evidence and status fields in the security_controls table
        cursor.execute("""
            UPDATE security_controls 
            SET evidence = ?, status = ? 
            WHERE id = ?
        """, (updated_evidence, status, control_id))

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print("add_assessment_result.py")
        print(f"Successfully inserted {entry_type} with name {name}, incident IDs: {incident_ids_list}, and updated status to '{status}'")
        return {"assessment_result_id": assessment_result_id, "control_id": control_id, "updated_evidence": updated_evidence}

    except Exception as e:
        print("add_assessment_result.py")
        print(f"An error occurred: {e}")
        return None

@eel.expose
def get_all_assessment_ids_and_names(db_path="../data/security_controls.db"):
    """
    Queries the assessment_results table and returns a list of all assessment ids and names.
    
    Parameters:
    db_path (str): Path to the SQLite database.
    
    Returns:
    list: A list of dictionaries with 'id' and 'name' keys for each assessment result.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to fetch all ids and names from the assessment_results table
        cursor.execute("SELECT id, name FROM assessment_results")
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Extract the ids and names from the results
        assessment_list = [{"id": row[0], "name": row[1]} for row in results]

        return assessment_list

    except Exception as e:
        print("add_assessment_result.py")
        print(f"An error occurred: {e}")
        return []    

@eel.expose
def get_all_assessment_details(db_path="../data/security_controls.db"):
    """
    Fetches all assessment results from the assessment_results table including all attributes.

    Parameters:
    db_path (str): Path to the SQLite database.

    Returns:
    list: A list of dictionaries containing 'id', 'type', 'incident_ids_list', and 'name' for each assessment result.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to fetch all records from the assessment_results table
        cursor.execute("SELECT id, type, incident_ids_list, name FROM assessment_results")
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Convert the results to a list of dictionaries
        assessment_details = [
            {"id": row[0], "type": row[1], "incident_ids_list": row[2], "name": row[3]}
        for row in results]

        return json.dumps(assessment_details)

    except Exception as e:
        print("add_assessment_result.py")
        print(f"An error occurred while fetching assessment details: {e}")
        return []  

@eel.expose
def apply_what_if_analysis_multiple(assessment_ids, db_path="../data/security_controls.db"):
    """
    Fetches the incident_ids_list for multiple assessment IDs and combines them into one big list.
    Appends the combined list to the 'filters.whatif_analysis' key via the set_filter_value function.
    
    Parameters:
    assessment_ids (list of int): The IDs of the assessment results to query.
    db_path (str): Path to the SQLite database.
    
    Returns:
    str: Success message or error.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        combined_incident_ids = set()  # Use a set to avoid duplicates

        for assessment_id in assessment_ids:
            # Query to fetch the incident_ids_list for each assessment ID
            cursor.execute("SELECT incident_ids_list FROM assessment_results WHERE id = ?", (assessment_id,))
            result = cursor.fetchone()

            if result is None:
                raise ValueError(f"No assessment found with ID {assessment_id}")

            incident_ids_list = result[0]
            incident_ids_array = incident_ids_list.split(",")  # Convert comma-separated string to a list

            # Add the incident IDs to the combined set
            combined_incident_ids.update(incident_ids_array)

        # Convert the set back to a list and pass it to the filter
        combined_incident_ids_list = list(combined_incident_ids)
        set_filter_value("filters.whatIf_analysis", combined_incident_ids_list)

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return f"Successfully applied what-if analysis for assessment IDs: {', '.join(map(str, assessment_ids))}"

    except Exception as e:
        print("add_assessment_result.py")
        print(f"An error occurred: {e}")
        return str(e)
    
@eel.expose
def remove_assessment_result(assessment_id, db_path="../data/security_controls.db"):
    """
    Removes an assessment result from the database and updates the associated security control's evidence.

    Parameters:
    assessment_id (int): The ID of the assessment result to remove.
    db_path (str): Path to the SQLite database.

    Returns:
    str: Success message or error.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the name of the assessment result to be removed
        cursor.execute("SELECT name FROM assessment_results WHERE id = ?", (assessment_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"No assessment result found with ID {assessment_id}")
        assessment_name = result[0]

        # Remove the assessment result from the assessment_results table
        cursor.execute("DELETE FROM assessment_results WHERE id = ?", (assessment_id,))

        # Update the evidence field in the security_controls table
        cursor.execute("SELECT id, evidence FROM security_controls")
        controls = cursor.fetchall()
        for control_id, evidence in controls:
            if evidence:
                # Remove the assessment name from the evidence field
                updated_evidence = ";".join(
                    [e.strip() for e in evidence.split(";") if e.strip() != assessment_name]
                )
                cursor.execute(
                    "UPDATE security_controls SET evidence = ? WHERE id = ?",
                    (updated_evidence, control_id),
                )

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print("add_assessment_result.py")
        print(f"Successfully removed assessment result with ID {assessment_id}")
        return f"Successfully removed assessment result with ID {assessment_id}"

    except Exception as e:
        print("add_assessment_result.py")
        print(f"An error occurred while removing assessment result: {e}")
        return str(e)

# Example usage:
if __name__ == "__main__":
    # Path to the SQLite database
    db_path = "../data/security_controls.db"

    try:
        # Fetch all assessment IDs and names
        assessments = get_all_assessment_ids_and_names(db_path=db_path)

        if not assessments:
            print("No assessments found in the database.")
        else:
            print(f"Found {len(assessments)} assessments. Removing them...")

            # Iterate over each assessment and remove it
            for assessment in assessments:
                assessment_id = assessment['id']
                assessment_name = assessment['name']
                print(f"Removing assessment ID {assessment_id} with name '{assessment_name}'...")
                result = remove_assessment_result(assessment_id, db_path=db_path)
                print(result)

            print("All assessments have been removed.")

    except Exception as e:
        print(f"An error occurred in the main function: {e}")
