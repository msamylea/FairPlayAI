import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus
import base64
import tempfile
import html

# Load environment variables from .env file 
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

base_url = "https://api.legiscan.com/"

api_key = os.getenv("LEGISCAN_KEY")
if not api_key:
    print("API key not found. Please check your .env file.")
    exit()

def get_bills(topic, state):
    query = quote_plus(topic)

    payload = {
        "key": api_key,
        "op": "getSearch",
        "state": state,
        "query": query,
        "year": 2
    }

    try:
        response = requests.get(base_url, params=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

    if response.status_code == 200:
        try:
            data = response.json()
            search_result = data.get('searchresult', {})
            bills = [search_result[key] for key in search_result if key.isdigit()]
            cleaned_bills = []
            for bill in bills:
                title = bill.get('title', '')
                # Clean up the title to remove non-UTF-8 characters and decode HTML entities
                cleaned_title = html.unescape(title.encode('utf-8', 'ignore').decode('utf-8'))
                cleaned_bills.append({"bill_id": bill.get('bill_id'), "title": cleaned_title})
            return cleaned_bills
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return []
    else:
        print(f"Failed to fetch the search results. Status code: {response.status_code}")
        return []

def get_bill_pdf(bill_id):
    # First, get the bill details
    bill_payload = {
        "key": api_key,
        "op": "getBill",
        "id": bill_id
    }

    bill_response = requests.get(base_url, params=bill_payload)

    if bill_response.status_code == 200:
        bill_data = bill_response.json().get('bill', {})
        print(bill_data)
        # Now get the bill text
        text_docs = bill_data.get('texts', [])
        if text_docs:
            doc_id = text_docs[0].get('doc_id')  # Get the first available text document
            
            if doc_id:
                text_payload = {
                    "key": api_key,
                    "op": "getBillText",
                    "id": doc_id
                }

                text_response = requests.get(base_url, params=text_payload)
                
                if text_response.status_code == 200:
                    text_data = text_response.json().get('text', {})
                    bill_text_base64 = text_data.get('doc', '')  # This is the base64 encoded document
                    
                    # Decode the base64-encoded text
                    bill_text_pdf = base64.b64decode(bill_text_base64)
                    
                    # Create a temporary file to save the PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        temp_pdf.write(bill_text_pdf)
                        return temp_pdf.name
                else:
                    print(f"Failed to fetch bill text for doc_id: {doc_id}. Status code: {text_response.status_code}")
                    return None
            else:
                print(f"Doc ID not found in texts for bill_id: {bill_id}")
                return None
        else:
            print(f"No texts found for bill_id: {bill_id}")
            return None
    else:
        print(f"Failed to fetch bill data for bill_id: {bill_id}. Status code: {bill_response.status_code}")
        return None