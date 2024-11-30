import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()

API_USERNAME = os.getenv("LLAMA_API_USERNAME")
API_PASSWORD = os.getenv("LLAMA_API_PASSWORD")

if not API_USERNAME or not API_PASSWORD:
    raise EnvironmentError("Umgebungsvariablen LLAMA_API_USERNAME und LLAMA_API_PASSWORD sind nicht gesetzt.")

API_URL = "https://wigpu01l.f4.htw-berlin.de:4000/api/generate"
API_AUTH = HTTPBasicAuth(API_USERNAME,API_PASSWORD)

def query_llama(prompt):
    headers = {
        "content-type": "application/json"
    }
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(
        API_URL, 
        json=payload, 
        headers=headers, 
        auth=API_AUTH, 
        verify=False  
    )
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    
    else:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")