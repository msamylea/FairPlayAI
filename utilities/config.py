import os
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

genai.configure(api_key=os.environ.get('GENAI_API_KEY'))

llm = genai.GenerativeModel("models/gemini-1.5-pro")

