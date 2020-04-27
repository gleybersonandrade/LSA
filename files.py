"""LSA IO functions"""

# System imports
import json


def read_file(file):
    """Read JSON file function"""
    with open(file) as json_data:
        model = json.load(json_data)["model"]
        features = [feature["code"] for feature in model
                    if feature["type"] == "Feature"]
        return features


def write_file(data, file):
    """Write JSON file function"""
    with open(file, 'w') as outfile:  
        json.dump(data, outfile, indent=4)
