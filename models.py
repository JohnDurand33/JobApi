from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    job_search_criteria = relationship("JobSearchCriteria", back_populates="user")
    job_applications = relationship("JobApplication", back_populates="user")

class JobSearchCriteria(db.Model):
    __tablename__ = 'JobSearchCriteria'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('Users.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    skills = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    salary = db.Column(db.String, nullable=False)
    remote = db.Column(Boolean, nullable=False, default=False)  # Add this line
    user = relationship("User", back_populates="job_search_criteria")

class JobApplication(db.Model):
    __tablename__ = 'JobApplications'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('Users.id'), nullable=False)
    job_title = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    job_id = db.Column(db.String, nullable=False)  # Add job_id to avoid duplicates
    user = relationship("User", back_populates="job_applications")

User.job_search_criteria = relationship("JobSearchCriteria", order_by=JobSearchCriteria.id, back_populates="user")
User.job_applications = relationship("JobApplication", order_by=JobApplication.id, back_populates="user")