import requests
from models import JobSearchCriteria
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
ADZUNA_API_ID = os.getenv('ADZUNA_API_ID')
ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')

# List of allowed job titles
ALLOWED_JOB_TITLES = [
    "junior software developer", "junior software engineer", "fullstack engineer",
    "junior fullstack engineer", "python developer", "junior python developer",
    "junior javascript developer", "junior react engineer", "react engineer",
    "javascript developer", "junior react developer", "react developer",
    "flask developer", "junior flask developer", "software engineer",
    "flask engineer", "junior flask engineer", "junior full stack engineer",
    "full stack engineer"
]

# List of unwanted keywords
UNWANTED_KEYWORDS = ["senior", "sr", "lead", "director", "java", "c++"]
EXCLUDED_TECHNOLOGIES = ["java", "c++"]

def perform_job_search(criteria):
    params = {
        'app_id': ADZUNA_API_ID,
        'app_key': ADZUNA_API_KEY,
        'results_per_page': 50,
        'what': criteria.title,
        'content-type': 'application/json',
    }

    # Log the parameters and credentials
    print(f"Searching jobs with parameters: {params}")
    print(f"ADZUNA_API_ID: {ADZUNA_API_ID}, ADZUNA_API_KEY: {ADZUNA_API_KEY}")

    # Search for Richmond, VA
    params_richmond = params.copy()
    params_richmond['where'] = 'Richmond, VA'
    response_richmond = requests.get(ADZUNA_API_URL, params=params_richmond)
    print(f"Richmond search response status: {response_richmond.status_code}")
    print(f"Richmond search response text: {response_richmond.text}")
    
    try:
        data_richmond = response_richmond.json()
    except ValueError as e:
        print(f"Error decoding Richmond response JSON: {e}")
        data_richmond = {}

    # Search for remote jobs
    params_remote = params.copy()
    params_remote['where'] = 'remote'
    response_remote = requests.get(ADZUNA_API_URL, params=params_remote)
    print(f"Remote search response status: {response_remote.status_code}")
    print(f"Remote search response text: {response_remote.text}")
    
    try:
        data_remote = response_remote.json()
    except ValueError as e:
        print(f"Error decoding Remote response JSON: {e}")
        data_remote = {}

    jobs = []

    def process_job_listings(data):
        for job in data.get('results', []):
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            if any(title in job_title for title in ALLOWED_JOB_TITLES) and \
               not any(keyword in job_title for keyword in UNWANTED_KEYWORDS) and \
               not any(tech in job_description for tech in EXCLUDED_TECHNOLOGIES):
                jobs.append({
                    'title': job.get('title'),
                    'company': job.get('company', {}).get('display_name'),
                    'location': job.get('location', {}).get('display_name'),
                    'salary': job.get('salary_min', 'N/A'),  # Default to 'N/A' if salary is not provided
                    'redirect_url': job.get('redirect_url')
                })

    process_job_listings(data_richmond)
    process_job_listings(data_remote)

    return jobs