from datetime import datetime
import json
import os

def load_data(path="data.json"):
    if os.path.exists(path):
        with open(path, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"cars": []}
    return {"cars": []}

def save_data(data, path="data.json"):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)