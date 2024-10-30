import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

key = os.getenv("GOOGLE_CIVIC")

def get_representatives(address):
    try:
        base_url = f"https://www.googleapis.com/civicinfo/v2/representatives?key={key}&address={address}&includeOffices=true&roles=legislatorUpperBody&roles=legislatorLowerBody"
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    return response.json()
