import os
import eel
import sqlite3
import json
from sqlite3 import Error

def create_connection(db_file):
    """ Create a database connection to a SQLite database in the specified directory """
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    try:
        conn = sqlite3.connect(db_file)
        print("database_sec_controls.py")
        print(f"Connected to SQLite, version {sqlite3.version}")
        return conn
    except Error as e:
        print("database_sec_controls.py")
        print(e)
    return None

def create_tables(conn):
    """ Create table by executing SQL statements """
    sql_create_security_controls_table = """
    CREATE TABLE IF NOT EXISTS security_controls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        comments TEXT,
        operator_id INTEGER,
        status TEXT NOT NULL CHECK(status IN ('covered', 'partially covered', 'not covered'))
    );
    """
    sql_create_tags_table = """
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """
    sql_create_control_tags_table = """
    CREATE TABLE IF NOT EXISTS control_tags (
        control_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        FOREIGN KEY (control_id) REFERENCES security_controls (id),
        FOREIGN KEY (tag_id) REFERENCES tags (id),
        PRIMARY KEY (control_id, tag_id)
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_security_controls_table)
        cursor.execute(sql_create_tags_table)
        cursor.execute(sql_create_control_tags_table)
        conn.commit()
        print("database_sec_controls.py")
        print("Tables created successfully")
    except Error as e:
        print("database_sec_controls.py")
        print(e)

@eel.expose
def insert_security_control(title, description, operator_name, status='not covered'):
    """Insert a security control into the database."""
    try:
        database = "../data/security_controls.db"  # Path to the database file
        conn = sqlite3.connect(database)

        # Ensure status is a string and has a valid value
        if not isinstance(status, str):
            raise ValueError(f"Invalid status type: {type(status)}. Expected a string.")
        if status not in ['covered', 'partially covered', 'not covered']:
            raise ValueError(f"Invalid status value: {status}. Expected one of 'covered', 'partially covered', 'not covered'.")

        # Inserting into security_controls table
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO security_controls (title, description, operator_id, status) VALUES (?, ?, ?, ?)",
            (title, description, operator_name, status)
        )
        control_id = cursor.lastrowid  # Fetch the last inserted id

        conn.commit()
        print("database_sec_controls.py")
        print("Security control inserted successfully.")
        conn.close()
        return "Success"
    except sqlite3.Error as e:
        print("database_sec_controls.py")
        print(f"An error occurred: {e}")
        conn.rollback()
        return f"Error: {e}"
    except ValueError as ve:
        print("database_sec_controls.py")
        print(f"Validation error: {ve}")
        return f"Error: {ve}"

@eel.expose
def fetch_all_security_controls():
    """Fetch and display all security controls along with their tags from the database."""
    try:
        database = "../data/security_controls.db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        sql_query = """
        SELECT sc.id, sc.title, sc.description, sc.operator_id, sc.status, sc.evidence, sc.comments
        FROM security_controls sc
        GROUP BY sc.id;
        """
        
        cursor.execute(sql_query)
        controls = cursor.fetchall()
        controls_list = [{'id': row[0], 'title': row[1], 'description': row[2], 'operator_id': row[3], 'status': row[4], 'evidence': row[5], 'comments': row[6]} for row in controls]
        
        conn.close()
        return json.dumps(controls_list)
    except sqlite3.Error as e:
        print("database_sec_controls.py")
        print(f"An error occurred: {e}")
        return json.dumps([])

@eel.expose
def delete_security_control(control_id):
    """Delete a security control from the database by its ID."""
    try:
        database = "../data/security_controls.db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # SQL command to delete the security control
        sql_delete_control = "DELETE FROM security_controls WHERE id = ?"
        cursor.execute(sql_delete_control, (control_id,))
        
        # Check if the row was deleted
        if cursor.rowcount == 0:
            print("database_sec_controls.py")
            print("No such security control found with ID:", control_id)
        else:
            print("database_sec_controls.py")
            print("Security control deleted successfully.")
        
        # Commit the changes to the database
        conn.commit()

        # Also, delete any associated tags from control_tags to maintain integrity
        sql_delete_tags = "DELETE FROM control_tags WHERE control_id = ?"
        cursor.execute(sql_delete_tags, (control_id,))
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print("database_sec_controls.py")
        print(f"An error occurred: {e}")
        conn.rollback()  # Roll back any changes if an error occurs

@eel.expose
def count_security_controls(security_control_status=None):
    try:
        database = "../data/security_controls.db"  # Path to your database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # SQL query to count the number of security controls
        if security_control_status:
            cursor.execute("SELECT COUNT(*) FROM security_controls WHERE status = ?", (security_control_status,))
        else:
            cursor.execute("SELECT COUNT(*) FROM security_controls")
            
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    except sqlite3.Error as e:
        print("database_sec_controls.py")
        print(f"An error occurred: {e}")
        return 0

# Example usage
def main():

    # Define the database path under ../data directory
    base_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
    database = os.path.join(base_dir, "security_controls.db")

    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("database_sec_controls.py")
        print("Error! cannot create the database connection.")

    # Example security control data
    example_data = [
        ("Perform assessment for Q4 2016", "The assessment period shall be limited to 01/10/2016 - 01/01/2017", "Manager"),
        ("Check process activities", "Perform activity-wise analysis and identify possible process errors", "Monitor"),
        ("Check technical attributes", "Identify patterns in affected service categories and determine their KPIs", "Responder"),
        ("Verify impact on service performance", "Perform What-if analysis excluding the identified incident ranges", "Analyst")
    ]

    for data in example_data:
        insert_security_control(*data)

    controls = fetch_all_security_controls()
    print("database_sec_controls.py")
    print("All security controls:", controls)


if __name__ == '__main__':
    main()
