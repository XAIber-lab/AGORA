"""Main Python application file"""

import os
import platform
import random
import sys
import eel

from validate_pnml import validate_pnml
from calculate_averages_db import calculate_column_average
from csv_reader import get_csv_data
from pnml_reader import get_pnml_data, get_pnml_states
from common_variants_db import *
from database_sec_controls import insert_security_control
from count_deviations_db import count_frequencies
from define_mapping import extract_places_from_pnml, write_mapping_to_file
from select_time_period_db import query_closed_incidents, count_unique_incidents, number_of_closed_incidents_in_time_period
from tabular_entries import *
from time_between_states_and_transitions import get_average_state_times, get_average_transition_times
from pnml_reader import get_pnml_data
from process_compliance_time import get_closed_ordered_incidents
from process_compliance_distribution import get_compliance_metric_distribution
from process_timedeltas import get_ordered_time_to_states_last_occurrence
from active_closed_incidents import get_incidents_open_and_closed_over_time
from critical_incidents import get_critical_incidents
from individual_incident_metrics import calculate_individual_averages, get_incident_event_intervals
from technical_analysis import get_incident_technical_attributes
from statistical_analysis import get_statistical_analysis_data
from compliance_metric_per_state import get_compliance_per_state_per_incident, get_average_compliance_per_state, update_cost_with_compliance_per_state
from add_assessment_result import insert_assessment_result, apply_what_if_analysis_multiple, get_all_assessment_details
from link_view_to_security_control import save_screenshot_and_link_to_control, fetch_all_assessment_views
from global_progress import get_global_progress
from ai_recommendation import generate_assessment_security_control
from database_filter_variables import *

filter_conditions = {}


@eel.expose
def communicate_pnml_validation_py(pnml_input):
    validation_result = validate_pnml(pnml_input)
    if validation_result == "Valid PNML":
        # Ensure the target directory exists
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Create or overwrite the file in the target directory
        file_path = os.path.join(data_dir, 'reference_model.pnml')
        with open(file_path, 'w') as file:
            file.write(pnml_input)
    
    return validation_result

@eel.expose
def communicate_log_py(log_input):
    try:
        # Define the path for the data directory and file
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_path = os.path.join(data_dir, 'IM_log.csv')
        
        # Write the log_input to the file
        with open(file_path, 'w') as file:
            file.write(log_input)

        return "File saved successfully"
    except Exception as e:
        print("server.py")
        print(f"Error saving file: {e}")
        return "Error saving file"

@eel.expose
def filter_condition(metric_name, condition):
    # Unique key for identifying the condition
    key = f"{metric_name}:{condition}"

    # Parse the range from the string
    low, high = map(float, condition.split(' to '))

    # Check if the condition already exists or needs updating
    if key in filter_conditions:
        # Remove the existing condition if toggling off
        del filter_conditions[key]
        print("server.py")
        print(f"Removed filter condition for {key}")
    else:
        # Add or update the condition
        filter_conditions[key] = lambda df, mn=metric_name, low=low, high=high: (df[mn] >= low) & (df[mn] <= high)
        print("server.py")
        print(f"Added filter condition for {key}")

    # Print current active filters for debugging
    print("server.py")
    print("Current active filters:")
    for k, v in filter_conditions.items():
        print("server.py")
        print(f"{k}: {v.__name__ if hasattr(v, '__name__') else 'anonymous function'}")


# Function to read the CSV data from the file
@eel.expose
def communicate_csv_data():
    try:
        # Construct a list of tuples (metric_name, filter_function) from the filter_conditions
        active_filters = [(key.split(':')[0], filter_conditions[key]) for key in filter_conditions]

        # If no filters are active, this will pass an empty list to get_csv_data, which will return unfiltered data
        csv_data = get_csv_data(active_filters)
        return csv_data
    except Exception as e:
        print("server.py")
        print(f"Error receiving CSV data: {e}")
        return "Error receiving CSV data"


@eel.expose  # Expose function to JavaScript
def say_hello_py(x):
    """Print message from JavaScript on app initialization, then call a JS function."""
    print("server.py")
    print('Hello from %s' % x)  # noqa T001
    eel.say_hello_js('Python {from within say_hello_py()}!')


@eel.expose
def expand_user(folder):
    """Return the full path to display in the UI."""
    return '{}/*'.format(os.path.expanduser(folder))


@eel.expose
def pick_file(folder):
    """Return a random file from the specified folder."""
    folder = os.path.expanduser(folder)
    if os.path.isdir(folder):
        listFiles = [_f for _f in os.listdir(folder) if not os.path.isdir(os.path.join(folder, _f))]
        if len(listFiles) == 0:
            return 'No Files found in {}'.format(folder)
        return random.choice(listFiles)
    else:
        return '{} is not a valid folder'.format(folder)    

def start_eel(develop):
    """Start Eel with either production or development configuration."""

    if develop:
        directory = '..'
        app = None
        page = {'port': 3000}
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'

    eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html'])

    # These will be queued until the first connection is made, but won't be repeated on a page reload
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!')   # Call a JavaScript function (must be after `eel.init()`)

    eel.show_log('https://github.com/samuelhwilliams/Eel/issues/363 (show_log)')

    eel_kwargs = dict(
        host='localhost',
        port=8080,
        size=(1280, 800),
    )
    try:
        eel.start(page, mode=app, **eel_kwargs)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', **eel_kwargs)
        else:
            raise


if __name__ == '__main__':
    import sys

    # Pass any second argument to enable debugging
    start_eel(develop=len(sys.argv) == 2)
