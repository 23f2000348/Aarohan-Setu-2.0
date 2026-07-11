from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from backend.models.db_models import db, User, StudentProfile, PlacementDrive, Application, cache
from backend.config import Config

student_bp = Blueprint('student', __name__)

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            return jsonify({'message': 'Student access required.'}), 403
        return f(*args, **kwargs)
    return decorated_function


@student_bp.route('/api/student/profile', methods=['GET'])
@login_required
@student_required
def get_profile():
    profile = current_user.student_profile
    return jsonify(profile.to_dict()), 200


@student_bp.route('/api/student/profile', methods=['POST'])
@login_required
@student_required
def update_profile():
    profile = current_user.student_profile
    data = request.get_json() or {}
    
    profile.name = data.get('name', profile.name)
    profile.branch = data.get('branch', profile.branch)
    profile.cgpa = float(data.get('cgpa', profile.cgpa))
    profile.graduation_year = int(data.get('graduation_year', profile.graduation_year))
    
    db.session.commit()
    return jsonify({
        'message': 'Profile updated successfully.',
        'profile': profile.to_dict()
    }), 200


@student_bp.route('/api/student/resume', methods=['POST'])
@login_required
@student_required
def upload_resume():
    profile = current_user.student_profile
    
    if 'resume' not in request.files:
        return jsonify({'message': 'No resume file provided.'}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file.'}), 400
        
    if file and Config.allowed_file(file.filename):
        filename = f"resume_{profile.id}_{secure_filename(file.filename)}"
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        profile.resume_path = f"/api/resumes/{filename}"
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded successfully.',
            'resume_path': profile.resume_path
        }), 200
        
    return jsonify({'message': 'Invalid file format. Allowed formats: PDF, DOC, DOCX.'}), 400


@student_bp.route('/api/student/drives', methods=['GET'])
@login_required
@student_required
def get_drives():
    profile = current_user.student_profile
    eligible_only = request.args.get('eligible_only', 'false').lower() == 'true'
    search_query = request.args.get('q', '').strip()
    
    # Query approved drives
    query = PlacementDrive.query.filter_by(status='Approved')
    
    if search_query:
        query = query.filter(
            db.or_(
                PlacementDrive.job_title.like(f'%{search_query}%'),
                PlacementDrive.job_description.like(f'%{search_query}%')
            )
        )
        
    drives = query.all()
    
    result = []
    for d in drives:
        # Check eligibility logic
        # 1. CGPA
        cgpa_ok = profile.cgpa >= d.cgpa_eligibility
        # 2. Year
        year_ok = profile.graduation_year == d.year_eligibility
        # 3. Branch
        branch_eligibility_list = [b.strip().lower() for b in d.branch_eligibility.split(',') if b.strip()]
        branch_ok = (
            d.branch_eligibility.lower() == 'all' or 
            'all' in branch_eligibility_list or 
            profile.branch.lower() in branch_eligibility_list
        )
        
        is_eligible = cgpa_ok and year_ok and branch_ok
        
        # Check if already applied
        has_applied = Application.query.filter_by(student_id=profile.id, drive_id=d.id).first() is not None
        
        drive_dict = d.to_dict()
        drive_dict['is_eligible'] = is_eligible
        drive_dict['has_applied'] = has_applied
        
        if eligible_only and not is_eligible:
            continue
            
        result.append(drive_dict)
        
    return jsonify(result), 200


@student_bp.route('/api/student/drives/<int:drive_id>/apply', methods=['POST'])
@login_required
@student_required
def apply_to_drive(drive_id):
    profile = current_user.student_profile
    if profile.is_blacklisted:
        return jsonify({'message': 'Your profile is blacklisted. You cannot apply to placement drives.'}), 403
        
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Placement drive not found.'}), 404
        
    if drive.status != 'Approved':
        return jsonify({'message': 'This placement drive is not open for applications.'}), 400
        
    if drive.deadline < datetime.utcnow():
        return jsonify({'message': 'Application deadline has passed.'}), 400
        
    # Check if student already applied
    existing_app = Application.query.filter_by(student_id=profile.id, drive_id=drive_id).first()
    if existing_app:
        return jsonify({'message': 'You have already applied to this placement drive.'}), 400
        
    # Eligibility validation
    cgpa_ok = profile.cgpa >= drive.cgpa_eligibility
    year_ok = profile.graduation_year == drive.year_eligibility
    branch_eligibility_list = [b.strip().lower() for b in drive.branch_eligibility.split(',') if b.strip()]
    branch_ok = (
        drive.branch_eligibility.lower() == 'all' or 
        'all' in branch_eligibility_list or 
        profile.branch.lower() in branch_eligibility_list
    )
    
    if not (cgpa_ok and year_ok and branch_ok):
        return jsonify({'message': 'You do not meet the eligibility criteria for this placement drive.'}), 403
        
    # Resume verification
    if not profile.resume_path:
        return jsonify({'message': 'Please upload your resume before applying.'}), 400
        
    new_app = Application(
        student_id=profile.id,
        drive_id=drive_id,
        status='Applied'
    )
    
    db.session.add(new_app)
    db.session.commit()
    
    # Invalidate stats cache
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({
        'message': 'Applied to placement drive successfully.',
        'application': new_app.to_dict()
    }), 201


@student_bp.route('/api/student/applications', methods=['GET'])
@login_required
@student_required
def get_applications():
    profile = current_user.student_profile
    apps = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


@student_bp.route('/api/student/applications/export', methods=['POST'])
@login_required
@student_required
def trigger_export():
    from backend.tasks import export_applications_csv
    profile = current_user.student_profile
    
    # Trigger Celery async task
    export_applications_csv.delay(profile.id)
    
    return jsonify({
        'message': 'Your placement applications CSV export task has been triggered. You will be notified in the portal once the export completes.'
    }), 202
