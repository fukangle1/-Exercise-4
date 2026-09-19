## Import the necessary modules

## Import the function from the module parse_data
import json
from ollama import chat
from parse_data import load_items, get_unclaimed_items, save_result


## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = """You are a campus lost-and-found assistant.
You must only use the items given in the database below.
Not all details of an item must match to be a possible match.
Only items that are unclaimed should be considered.

You must reply with ONLY a JSON object, nothing else. The structure must be exactly:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}

Rules:
- "matches" contains all possible matching item IDs
- "confidence" must be exactly one of: LOW, MEDIUM, HIGH
- If there is no match, return an empty list for matches

Available items in the lost-and-found database:
""" + json.dumps(available_items)
    
    user_prompt = description
    return system_prompt, user_prompt
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response["message"]["content"]


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    return json.loads(response_text)


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if not isinstance(result["confidence"], str):
        return False
    if result["confidence"] not in ["LOW", "MEDIUM", "HIGH"]:
        return False
    
    valid_ids = []
    for item in available_items:
        valid_ids.append(item["id"])
    
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            return False
    
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("MATCH RESULT")
    print("-" * 50)
    print("Confidence:", result["confidence"])
    print()
    print("Possible matches:")
    print()
    
    if len(result["matches"]) == 0:
        print("No matches found.")
    else:
        for match_id in result["matches"]:
            for item in available_items:
                if item["id"] == match_id:
                    print("ID:", item["id"])
                    print("Item:", item["item"])
                    print("Color:", item["color"])
                    print("Location:", item["location"])
                    print("Date found:", item["date"])
                    print()
                    break
    

## Control center for the entire program.
def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()
    
    description = input("Describe the item you lost: ")
    print()
    print("Searching for possible matches...")
    print()
    
    items = load_items("found_items.json")
    unclaimed = get_unclaimed_items(items)
    
    system_prompt, user_prompt = build_prompt(description, unclaimed)
    
    try:
        response = ask_qwen(system_prompt, user_prompt)
        result = parse_response(response)
    except:
        result = {"matches": [], "confidence": "LOW"}
    
    if not validate_result(result, unclaimed):
        result = {"matches": [], "confidence": "LOW"}
    
    display_matches(result, unclaimed)
    
    save_result(result, "output/match_result.json")
    print("Result saved to output/match_result.json")


if __name__ == "__main__":
    main()