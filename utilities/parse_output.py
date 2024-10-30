import re
import json
import json_repair
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extract_json_from_string(s):
    match = re.search(r'\[[\s\S]*\]', s)
    if match:
        return match.group(0)
    return None

def parse_output_json(output):
    print("Entered parse_output_json")
    print(f"Received output: {output[:100]}...")  # Log first 100 characters

    if isinstance(output, (list, dict)):
        print("Input is already a list or dict, returning as is.")
        return output

    if not isinstance(output, str):
        print(f"Unexpected input type: {type(output)}")
        return None

    # Function to try parsing JSON
    def try_json_parse(json_str):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    # 1. Try parsing the entire string as JSON
    parsed = try_json_parse(output)
    print("Parsed: ", parsed)   
    if parsed:
        print("Parsed JSON: ", parsed)
        return parsed

    # 2. Try to extract JSON from markdown code blocks
    json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', output)
    if json_block_match:
        json_str = json_block_match.group(1)
        parsed = try_json_parse(json_str)
        if parsed:
            print("Parsed JSON block: ", parsed)
            return parsed

    # 3. Try to extract anything that looks like a JSON object or array
    json_like_match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', output)
    if json_like_match:
        json_str = json_like_match.group(0)
        parsed = try_json_parse(json_str)
        if parsed:
            print("Parsed JSON-like: ", parsed)
            return parsed

    # 4. If all else fails, try to repair and parse the JSON
    try:
        repaired_json = json_repair.loads(output)
        print("Repaired JSON: ", repaired_json)
        return repaired_json
    except Exception as e:
        print(f"Error: {e}")

    print("Failed to parse JSON in all attempts.")
    return None