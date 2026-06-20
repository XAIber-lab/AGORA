import xml.etree.ElementTree as ET
import eel

@eel.expose
def extract_places_from_pnml():
    """
    Extracts and returns all places from a PNML file.
    
    Args:
    file_path (str): Path to the PNML file.
    
    Returns:
    list of str: A list of places in the order of appearance.
    """
    try:
        file_path = "../data/reference_model.pnml"

        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract all places and their names
        places = [place.find('name/text').text if place.find('name/text') is not None else "Unnamed Place"
                  for place in root.findall('.//place')]

        return places
    except ET.ParseError as e:
        print("database_sec_controls.py")
        print(f"Failed to parse the XML file: {e}")
        return []
    except Exception as e:
        print("database_sec_controls.py")
        print(f"An error occurred: {e}")
        return []

@eel.expose
def write_mapping_to_file(places, state_mapping, file_path="../data/mapping.txt"):
    """
    Writes a mapping of places to state codes into a file.

    Args:
    places (list of str): A list of place names.
    state_mapping (dict): A dictionary mapping place names to state codes.
    file_path (str): Path to the file where the mapping should be saved.
    """
    try:
        # Prepare content to write
        lines = ["{\n"]
        for place in places:
            if place in state_mapping and state_mapping[place]:
                lines.append(f"    '{place}': '{state_mapping[place]}',\n")
        lines.append("}\n")

        # Write to file
        with open(file_path, 'w') as file:
            file.writelines(lines)
            print("database_sec_controls.py")
            print(f"Mapping successfully written to {file_path}")

    except Exception as e:
        print("database_sec_controls.py")
        print(f"An error occurred while writing to the file: {e}")

@eel.expose
def read_mapping_from_file(file_path="../data/mapping.txt"):
    """
    Reads a mapping of places to state codes from a file.

    Args:
        file_path (str): Path to the file from which the mapping should be read.

    Returns:
        dict: A dictionary containing the mapping of place names (str) to state codes (str).
        Example:
            {
                "Detection": "N",
                "Activation": "A",
                ...
            }

    Interpretation:
        - Each key is a place name from the PNML reference model.
        - Each value is the corresponding state code assigned to that place.
        - The mapping is used to translate between human-readable process states and their coded representations in the incident management system.
        - If the mapping file does not exist or cannot be read, the function returns an empty dictionary.

    Usage:
        - Use this output to map process states in analytics, reporting, or compliance calculations.
        - The dictionary can be directly consumed by JavaScript via Eel for frontend logic or visualization.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            mapping_dict = {}
            for line in lines:
                # Skip empty lines and braces
                if line.strip() and line.strip() not in ["{", "}"]:
                    # Assuming the line format is '    'place': 'code','
                    parts = line.strip().replace("'", "").replace(",", "").split(': ')
                    if len(parts) == 2:
                        mapping_dict[parts[0]] = parts[1]
        return mapping_dict
    except FileNotFoundError:
        print("database_sec_controls.py")
        print(f"No mapping file found at {file_path}.")
        return {}
    except Exception as e:
        print("database_sec_controls.py")
        print(f"An error occurred while reading the file: {e}")
        return {}

def main():
    
    print("database_sec_controls.py")
    print(read_mapping_from_file())

if __name__ == "__main__":
    main()
