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

def default_occupancy():
    # default occupancy json file setting (set all occupancy to 0)
    initial_data = {"slots":[{"slot_id": i, "occupancy": 0} for i in range(1, 6)]}
    with open("occupancy.json", "w") as f:
        json.dump(initial_data, f, indent=4)
    print("Created default occupancy.json")