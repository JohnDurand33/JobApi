import requests

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs"
API_ID = "202e6360"
API_KEY = "f16d3d88464335aaf3fc9cd4ef02b90c"

def search_jobs(title, location, salary):
    params = {
        'app_id': API_ID,
        'app_key': API_KEY,
        'results_per_page': 50,
        'what': title,
        'where': location,
        'salary_min': salary
    }
    
    response = requests.get(f"{ADZUNA_API_URL}/us/search/1", params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None