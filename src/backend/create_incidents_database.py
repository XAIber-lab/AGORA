import pandas as pd
from sqlalchemy import create_engine
import os

# Function to load CSV and write to SQLite
def csv_to_sqlite(csv_file, table_name, delimiter=';', database='../data/incidents.db'):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(database), exist_ok=True)
    
    # Create a connection to the SQLite database
    engine = create_engine(f'sqlite:///{database}')
    
    try:
        # Load the CSV file into a DataFrame
        df = pd.read_csv(csv_file, delimiter=delimiter, on_bad_lines='skip')
        
        # Write the DataFrame to a table in the SQLite database
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print("create_incidents_database.py")
        print(f"Data from {csv_file} written to table '{table_name}' in database '{database}'.")
    except pd.errors.ParserError as e:
        print("create_incidents_database.py")
        print(f"Error parsing {csv_file}: {e}")
    except Exception as e:
        print("create_incidents_database.py")
        print(f"An error occurred: {e}")

# Main function to execute the script
if __name__ == "__main__":
    # Define the CSV file paths
    event_log_csv = '../data/simple_log.csv'
    incident_log_csv = '../data/IM_log.csv'
    
    # Write each CSV to the database
    csv_to_sqlite(event_log_csv, 'event_log_table', delimiter=';')
    csv_to_sqlite(incident_log_csv, 'incident_alignment_table', delimiter=',')
