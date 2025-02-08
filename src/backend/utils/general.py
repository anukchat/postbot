import json
import re


def clean_json_string(json_string):
    # Fix invalid backslashes by replacing single \ with double \\ (except valid escapes)
    json_string = re.sub(r'(?<!\\)\\(?![\"\\/bfnrt])', r'\\\\', json_string)
    return json_string

def safe_json_loads(json_string):
    try:
        json_string = clean_json_string(json_string)
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return None