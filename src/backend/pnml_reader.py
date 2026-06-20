import os
import eel
import json
import xml.etree.ElementTree as ET

@eel.expose
def get_pnml_data():
    """
    Reads and returns the raw contents of the reference model PNML file.

    Returns:
        str: The full text content of the PNML file as a string. If the file cannot be read, returns an error message string.

    Interpretation:
        - The returned string contains the XML markup of the Petri Net reference model in PNML format.
        - This data can be parsed to extract process states, transitions, and the structure of the reference model.
        - Use this output for further parsing, visualization, or analysis of the incident management reference process.
        - If an error occurs (e.g., file not found or unreadable), the function returns a string describing the error.

    Usage:
        - Use this function to obtain the raw PNML data for backend processing or frontend visualization.
        - The string can be parsed using XML libraries to extract specific elements or attributes as needed.
    """
    try:
        # Define the path for the data directory and file
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        file_path = os.path.join(data_dir, 'reference_model.pnml')

        # Read the file content
        with open(file_path, 'r') as file:
            pnml_data = file.read()
        
        return pnml_data
    except Exception as e:
        print("pnml_reader.py")
        print(f"Error reading file: {e}")
        return "Error reading file"


@eel.expose
def get_pnml_states():
    """
    Extracts all the states (places) from the PNML file and returns them as a list.
    """
    try:
        # Define the path for the data directory and file
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        file_path = os.path.join(data_dir, 'reference_model.pnml')

        # Check if the file exists
        if not os.path.exists(file_path):
            print("pnml_reader.py")
            print(f"File not found: {file_path}")
            return "Error: File not found"

        # Parse the PNML file using ElementTree
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Debug: print root element and its children
        print("pnml_reader.py")
        print(f"Root element: {root.tag}")
        for child in root:
            print("pnml_reader.py")
            print(f"Child element: {child.tag}")

        # Try to find the net element without namespace
        nets = root.findall(".//net")
        print("pnml_reader.py")
        print(f"Number of nets found without namespace: {len(nets)}")
        
        # Try to find place elements directly under each net element
        states = []
        for net in nets:
            places = net.findall(".//place")
            print("pnml_reader.py")
            print(f"Number of places found without namespace: {len(places)}")
            for place in places:
                name_element = place.find(".//text")
                if name_element is not None and name_element.text:
                    states.append(name_element.text)
                else:
                    print("pnml_reader.py")
                    print(f"No text found for place with ID: {place.get('id')}")

        # If no places found, try with namespace
        if not states:
            namespace = {'pnml': 'http://www.informatik.hu-berlin.de/top/pntd/ptNetb'}
            if root.tag.startswith("{"):
                # Extract the namespace
                uri = root.tag.split("}")[0].strip("{")
                namespace = {'pnml': uri}
            print("pnml_reader.py")
            print(f"Using namespace: {namespace}")

            # Find all place elements in the PNML file using namespace
            places = root.findall(".//pnml:place", namespaces=namespace)
            print("pnml_reader.py")
            print(f"Number of places found with namespace: {len(places)}")

            for place in places:
                name_element = place.find("pnml:name/pnml:text", namespaces=namespace)
                if name_element is not None and name_element.text:
                    states.append(name_element.text)
                else:
                    print("pnml_reader.py")
                    print(f"No text found for place with ID: {place.get('id')}")

        # Debug: print the extracted states
        print("pnml_reader.py")
        print(f"Extracted states: {states}")

        return states

    except Exception as e:
        print("pnml_reader.py")
        print(f"Error reading or parsing file: {e}")
        return "Error reading or parsing file"

# Example usage
if __name__ == "__main__":
    states = get_pnml_states()
    print("pnml_reader.py")
    print(states)
