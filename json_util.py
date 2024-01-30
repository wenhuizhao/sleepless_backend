import json

def parse_json(s):
    if not "{" in s:
        return None
    s = s[next(idx for idx, c in enumerate(s) if c in "{["):]
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        return json.loads(s[:e.pos])

def extract_json(s):
    try:
        json_data = parse_json(s)
        return json_data
    except json.JSONDecodeError:
        return None

