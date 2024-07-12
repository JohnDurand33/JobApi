import requests
from models import JobSearchCriteria
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
ADZUNA_API_ID = os.getenv('ADZUNA_API_ID')
ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')

def perform_job_search(criteria):
    params = {
        'app_id': ADZUNA_API_ID,
        'app_key': ADZUNA_API_KEY,
        'results_per_page': 50,
        'what': criteria.title,
        'where': criteria.location,
        'salary_min': criteria.salary,
    }

    print(f"Requesting Adzuna API with params: {params}")  # Debug log

    response = requests.get(ADZUNA_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Adzuna API response: {data}")  # Debug log

        jobs = []
        for job in data.get('results', []):
            jobs.append({
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name'),
                'location': job.get('location', {}).get('display_name'),
                'salary': job.get('salary_min', 'N/A'),  # Default to 'N/A' if salary is not provided
                'redirect_url': job.get('redirect_url')
            })
        
        return jobs
    else:
        print(f"Adzuna API request failed with status code: {response.status_code}")  # Debug log
        return []