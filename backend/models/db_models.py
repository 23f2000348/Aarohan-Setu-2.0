from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_caching import Cache

db = SQLAlchemy()
cache = Cache()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    resume_path = db.Column(db.String(256), nullable=True)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'branch': self.branch,
            'cgpa': self.cgpa,
            'graduation_year': self.graduation_year,
            'resume_path': self.resume_path,
            'is_blacklisted': self.is_blacklisted,
            'email': self.user.email if self.user else ''
        }


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'hr_contact': self.hr_contact,
            'website': self.website,
            'description': self.description,
            'is_approved': self.is_approved,
            'is_blacklisted': self.is_blacklisted,
            'email': self.user.email if self.user else ''
        }


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    branch_eligibility = db.Column(db.String(256), default='All', nullable=False)  # CSV values or 'All'
    cgpa_eligibility = db.Column(db.Float, default=0.0, nullable=False)
    year_eligibility = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # 'Pending', 'Approved', 'Rejected', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else '',
            'job_title': self.job_title,
            'job_description': self.job_description,
            'branch_eligibility': self.branch_eligibility,
            'cgpa_eligibility': self.cgpa_eligibility,
            'year_eligibility': self.year_eligibility,
            'deadline': self.deadline.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied', nullable=False)  # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    interview_scheduled_at = db.Column(db.DateTime, nullable=True)
    offer_letter_path = db.Column(db.String(256), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'student_cgpa': self.student.cgpa if self.student else 0.0,
            'student_branch': self.student.branch if self.student else '',
            'drive_id': self.drive_id,
            'drive_title': self.drive.job_title if self.drive else '',
            'company_name': self.drive.company.name if self.drive and self.drive.company else '',
            'status': self.status,
            'applied_at': self.applied_at.isoformat(),
            'interview_scheduled_at': self.interview_scheduled_at.isoformat() if self.interview_scheduled_at else None,
            'offer_letter_path': self.offer_letter_path
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
