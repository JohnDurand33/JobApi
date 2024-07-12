from flask import Blueprint, request, jsonify
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

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs"
API_ID = "202e6360"
API_KEY = "f16d3d88464335aaf3fc9cd4ef02b90c"

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