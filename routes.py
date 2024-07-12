from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, JobSearchCriteria, JobApplication
import uuid
from utils import get_user_id
from job_search import perform_job_search
from flask_cors import cross_origin, CORS
import logging
from adzuna import search_jobs
import json
import requests
from werkzeug.utils import secure_filename
import os
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('YOUR_2CAPTCHA_API_KEY')

def solve_captcha(image_path):
    try:
        result = solver.normal(image_path)
        return result['code']
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return None

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs"
API_ID = "202e6360"
API_KEY = "f16d3d88464335aaf3fc9cd4ef02b90c"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

routes = Blueprint('routes', __name__)



@routes.route('/register', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def register():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16)
        new_user = User(email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500


@routes.route('/login', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def login():
    data = request.get_json()
    print('Received data:', data)
    
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    user_data = {
        'user_id': str(user.id),
        'email': user.email
    }
    return jsonify({'message': 'Login successful', 'user': user_data}), 200

@routes.route('/job_search_criteria', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def create_job_search_criteria():
    data = request.get_json()
    user_id = data['user_id']  # Extract user_id correctly
    
    print(f"Received data: {data}")
    print(f"Extracted user_id: {user_id}")

    new_criteria = JobSearchCriteria(
        user_id=user_id,  # Assign user_id as a UUID
        title=data['title'],
        skills=data['skills'],
        location=data['location'],
        salary=data['salary']
    )
    db.session.add(new_criteria)
    db.session.commit()
    print(f"Job search criteria saved: {new_criteria}")
    return jsonify({'message': 'Job search criteria created successfully'}), 201

@routes.route('/job_applications', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def create_job_application():
    data = request.get_json()
    new_application = JobApplication(
        user_id=data['user_id'],
        job_title=data['job_title'],
        company=data['company'],
        location=data['location'],
        status=data['status']
    )
    db.session.add(new_application)
    db.session.commit()
    return jsonify({'message': 'Job application created successfully'}), 201

@routes.route('/automate_jobs', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def automate_jobs():
    data = request.json
    print(f"Received data: {data}")  # Log received data
    email = data.get('email')
    user_id = get_user_id(email)
    
    if not user_id:
        return jsonify({'error': 'User not found'}), 404
    
    criteria_list = JobSearchCriteria.query.filter_by(user_id=user_id).all()
    all_jobs = []

    for criterion in criteria_list:
        print(f"Searching jobs for criteria: {criterion}")  # Debug log
        adzuna_jobs = perform_job_search(criterion)
        print(f"Jobs found: {adzuna_jobs}")  # Debug log
        all_jobs.extend(adzuna_jobs)
    
    print(f"Aggregated job listings: {all_jobs}")  # Debug log
    return jsonify({'job_listings': all_jobs})

def get_user_id(email):
    user = User.query.filter_by(email=email).first()
    return user.id if user else None

@routes.route('/upload_resume', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filepath': filepath}), 201
    return jsonify({'error': 'File type not allowed'}), 400

@routes.route('/uploads/<filename>', methods=['GET'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def get_uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@routes.route('/apply_to_jobs', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'], supports_credentials=True)
def apply_to_jobs():
    data = request.json
    resume_path = data.get('resume_path')
    job_urls = data.get('job_urls')
    
    for job_url in job_urls:
        apply_to_job_with_delay(job_url, resume_path)
    
    return jsonify({'message': 'Job applications submitted'}), 200

def apply_to_job_with_delay(job_url, resume_path):
    import time, random
    delay = random.uniform(1, 5)  # Delay between 1 and 5 seconds
    time.sleep(delay)
    apply_to_job(job_url, resume_path)

def apply_to_job(job_url, resume_path):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = webdriver.Chrome(executable_path='path/to/chromedriver')

    driver.get(job_url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'form')))

        name_field = driver.find_element(By.NAME, 'name')
        name_field.send_keys('Your Name')

        email_field = driver.find_element(By.NAME, 'email')
        email_field.send_keys('your.email@example.com')

        resume_upload = driver.find_element(By.NAME, 'resume')
        resume_upload.send_keys(resume_path)

        submit_button = driver.find_element(By.NAME, 'submit')
        submit_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'confirmation_message')))

        print("Application submitted successfully.")
    except Exception as e:
        print(f"Error during job application: {e}")
    finally:
        driver.quit()