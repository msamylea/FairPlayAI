from ai.analysis import analyze_policy
from utilities import parse_output
import json

def route_policy(input_data):
     
    try:
        analysis_result = analyze_policy(input_data)

        if isinstance(analysis_result, dict):
            if "error" in analysis_result:
                print(f"[route_policy] Error in analysis: {analysis_result['error']}")
            return analysis_result
        elif isinstance(analysis_result, str):
            print("[route_policy] Analysis result is a string, attempting to parse as JSON")
            try:
                parsed_result = parse_output.parse_output_json(analysis_result)
                if parsed_result:
                    print(f"[route_policy] Parsed result type: {type(parsed_result)}")
                    print(f"[route_policy] Parsed result content: {str(parsed_result)[:1000]}")
                    return parsed_result
                else:
                    print("[route_policy] Failed to parse string result as JSON")
                    return {"error": "Failed to parse string result as JSON", "raw_content": analysis_result[:1000]}
            except json.JSONDecodeError as e:
                print(f"[route_policy] Error parsing string result as JSON: {str(e)}")
                return {"error": f"Error parsing result as JSON: {str(e)}", "raw_content": analysis_result[:1000]}
            except Exception as e:
                print(f"[route_policy] Unexpected error parsing string result: {str(e)}")
                return {"error": f"Unexpected error parsing result: {str(e)}", "raw_content": analysis_result[:1000]}
        elif isinstance(analysis_result, list):
            print("[route_policy] Analysis result is a list, wrapping in a dictionary")
            return {"analysis": analysis_result, "raw_analysis": analysis_result}
        else:
            print(f"[route_policy] Unexpected result type: {type(analysis_result)}")
            return {"error": f"Unexpected result type: {type(analysis_result)}", "raw_content": str(analysis_result)[:1000]}
    except Exception as e:
        print(f"[route_policy] Error in analysis: {str(e)}")
        return {"error": f"An error occurred during analysis: {str(e)}"}