## Import the necessary modules
import json
import os

## Logic for loading and reading from a JSON file. 
## The function must return only the items
def load_items(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data["items"]

## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    result = []
    for item in items:
        if item["status"] == "unclaimed":
            result.append(item)
    return result
    

## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    folder = os.path.dirname(filename)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with open(filename, 'w') as f:
        json.dump(result, f, indent=4)