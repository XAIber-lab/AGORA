import sqlite3
import eel
import base64
import os
import random
import string
import json
from google import genai
from api_keys import GEMINI_API_KEY

def get_gemini_summary(comments):
    prompt = (
        "Try to generate an ai summary from the report. Structure the content and provide generated idea on what to do (possible remediations). "
        "Will even better support the claim of decision making. What is the state of decision? Suggest for each point a remediation?\n"
        f"Comments: {comments}"
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        print("response.text")
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return None



@eel.expose
def save_screenshot_and_link_to_control(screenshot_data, name, comments, control_id, status, db_path="../data/security_controls.db"):
    """
    Saves the screenshot to the filesystem and links it to a security control by updating its evidence field.
    Also updates the status of the security control.

    Args:
        screenshot_data (str): Base64 encoded image data of the screenshot.
        name (str): The name of the screenshot file (without extension).
        comments (str): Comments for the screenshot.
        control_id (int): The ID of the security control to link the evidence to.
        status (str): The new status for the security control ('covered', 'partially covered', 'not covered').
        db_path (str): Path to the SQLite database.

    Returns:
        dict: A dictionary containing the assessment_view_id and filename, or None if an error occurred.
    """
    try:
        # Decode the base64 encoded image data
        image_data = base64.b64decode(screenshot_data)

        # Create the filename using the provided name and append ".png"
        filename = f"{name}.png"

        # Define the path to save the image
        save_directory = '../assessment_results'
        os.makedirs(save_directory, exist_ok=True)
        save_path = os.path.join(save_directory, filename)

        # Save the image to the filesystem
        with open(save_path, 'wb') as f:
            f.write(image_data)

        # Ensure control_id is an integer
        control_id = int(control_id)

        # Validate the status
        valid_statuses = ['covered', 'partially covered', 'not covered']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Valid statuses are: {valid_statuses}")

        # Generate AI summary from comments
        ai_summary = get_gemini_summary(comments)
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the filename and comments into the assessment_views table
        cursor.execute("""
            INSERT INTO assessment_views (view_data, comments, ai_summary) 
            VALUES (?, ?, ?)
        """, (filename, comments, ai_summary))

        # Fetch the ID of the newly inserted assessment view
        assessment_view_id = cursor.lastrowid

        # Fetch the current evidence value for the security control
        cursor.execute("SELECT evidence FROM security_controls WHERE id = ?", (control_id,))
        result = cursor.fetchone()
        current_evidence = result[0] if result else ""

        # Append the new filename to the current evidence, separating by ';' if necessary
        if current_evidence:
            updated_evidence = current_evidence + ";" + filename
        else:
            updated_evidence = filename

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

        # Return the ID of the newly inserted assessment view and the filename
        return {"assessment_view_id": assessment_view_id, "filename": filename}

    except Exception as e:
        print("link_view_to_security_control.py")
        print(f"An error occurred: {e}")
        return None

    
@eel.expose
def fetch_all_assessment_views(db_path="../data/security_controls.db"):
    """
    Fetches all entries from the assessment_views table, including the image file and comments.

    Args:
        db_path (str): Path to the SQLite database.

    Returns:
        str: A JSON string containing the assessment view data (ID, image filename, base64-encoded image, comments).
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all entries from the assessment_views table
        cursor.execute("SELECT id, view_data, comments, ai_summary FROM assessment_views")
        views = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Prepare the list to hold the assessment view data
        assessment_views_list = []

        # Path to the directory where images are stored
        save_directory = '../assessment_results'

        # Process each view entry
        for view in views:
            view_id, image_filename, comment, ai_summary = view

            # Define the full path to the image file
            image_path = os.path.join(save_directory, image_filename)

            # Read the image file and encode it to base64
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                encoded_image = None  # If the image doesn't exist, set it to None

            # Append the assessment view data to the list
            assessment_views_list.append({
                "id": view_id,
                "image_filename": image_filename,
                "encoded_image": encoded_image,
                "comments": comment,
                "ai_summary": ai_summary
            })

        # Return the data as a JSON string
        return json.dumps(assessment_views_list)

    except sqlite3.Error as e:
        print("link_view_to_security_control.py")
        print(f"An error occurred while fetching assessment views: {e}")
        return json.dumps([])

@eel.expose
def remove_assessment_view(view_id, db_path="../data/security_controls.db"):
    """
    Removes a specific assessment view from the database and updates the associated security controls' evidence fields.

    Args:
        view_id (int): The ID of the assessment view to remove.
        db_path (str): Path to the SQLite database.

    Returns:
        str: A success message or error message.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the filename of the assessment view to be removed
        cursor.execute("SELECT view_data FROM assessment_views WHERE id = ?", (view_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"No assessment view found with ID {view_id}")
        image_filename = result[0]

        # Delete the assessment view from the assessment_views table
        cursor.execute("DELETE FROM assessment_views WHERE id = ?", (view_id,))

        # Update the evidence field in the security_controls table
        cursor.execute("SELECT id, evidence FROM security_controls")
        controls = cursor.fetchall()
        for control_id, evidence in controls:
            if evidence:
                # Remove the reference to the deleted view from the evidence field
                updated_evidence = ";".join(
                    [e.strip() for e in evidence.split(";") if e.strip() != image_filename]
                )
                cursor.execute(
                    "UPDATE security_controls SET evidence = ? WHERE id = ?",
                    (updated_evidence, control_id),
                )

        # Commit the transaction
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Remove the image file from the filesystem
        save_directory = '../assessment_results'
        image_path = os.path.join(save_directory, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        print("link_view_to_security_control.py")
        print(f"Successfully removed assessment view with ID {view_id}")
        return f"Successfully removed assessment view with ID {view_id}"

    except Exception as e:
        print("link_view_to_security_control.py")
        print(f"An error occurred while removing assessment view: {e}")
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Path to the SQLite database
    db_path = "../data/security_controls.db"

    try:
        # Fetch all assessment views
        print("Fetching all assessment views...")
        assessment_views_json = fetch_all_assessment_views(db_path=db_path)
        assessment_views = json.loads(assessment_views_json)

        if not assessment_views:
            print("No assessment views found in the database.")
        else:
            print(f"Found {len(assessment_views)} assessment views. Updating AI summaries...")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for view in assessment_views:
                view_id = view['id']
                comment = view['comments']
                print(f"Generating AI summary for assessment view ID {view_id}...")
                ai_summary = get_gemini_summary(comment)
                cursor.execute(
                    "UPDATE assessment_views SET ai_summary = ? WHERE id = ?",
                    (ai_summary, view_id)
                )
                conn.commit()
                print(f"Updated AI summary for assessment view ID {view_id}.")

            cursor.close()
            conn.close()
            print("All assessment views have been updated with AI summaries.")

    except Exception as e:
        print(f"An error occurred in the main function: {e}")