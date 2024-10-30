import logging
from utilities import config, parse_output

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def analyze_policy(input_data):
    with open("prompts/goal_five_analysis.txt", "r") as f:
        prompt = f.read()

    with open("utilities/goal_five.txt", "r") as f:
        goal_5 = f.read()

    if prompt:
        prompt = prompt.replace("{policy}", input_data)
        prompt = prompt.replace("{goal_5}", goal_5)

    response = config.llm.generate_content(prompt)
    response_text = response.text
    logger.info(f"Raw LLM response: {response_text[:500]}...")  # Log first 500 characters

    parsed_response = parse_output.parse_output_json(response_text)
    logger.info(f"Parsed response: {parsed_response}")

    if parsed_response:
        if isinstance(parsed_response, list) and len(parsed_response) == 1:
            parsed_response = parsed_response[0]
        
        if isinstance(parsed_response, dict):
            # Preserve all sections of the parsed response
            return parsed_response
        else:
            logger.warning(f"Parsed response is not a dictionary. Type: {type(parsed_response)}")
    
    # If parsing failed or the result is not as expected, return a default structure
    logger.warning("Failed to parse the LLM response as expected. Using default structure.")
    return {
        "policy_summary": {
            "title": "Failed to parse response",
            "focus_area": "N/A",
            "brief_overview": "Unable to analyze the policy due to parsing error"
        },
        "sdg5_alignment": {
            "overall_score": 0,
            "breakdown": []
        },
        "bias_analysis": {
            "explicit_biases": [],
            "implicit_biases": []
        },
        "cost_effectiveness_analysis": {
            "overall_rating": "N/A",
            "explanation": "Unable to analyze due to parsing error",
            "key_factors": []
        },
        "improvement_recommendations": [],
        "ai_integration_opportunities": [],
        "overall_assessment": {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        },
        "conclusion": {
            "summary": "Unable to analyze the policy due to parsing error",
            "key_takeaways": [],
            "final_recommendation": "Review and reanalyze the policy"
        }
    }