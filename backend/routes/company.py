from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import os
from backend.models.db_models import db, User, CompanyProfile, PlacementDrive, Application, Notification, cache

company_bp = Blueprint('company', __name__)

def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            return jsonify({'message': 'Company access required.'}), 403
        return f(*args, **kwargs)
    return decorated_function


@company_bp.route('/api/company/profile', methods=['GET'])
@login_required
@company_required
def get_profile():
    profile = current_user.company_profile
    return jsonify(profile.to_dict()), 200


@company_bp.route('/api/company/profile', methods=['POST'])
@login_required
@company_required
def update_profile():
    profile = current_user.company_profile
    data = request.get_json() or {}
    
    profile.name = data.get('name', profile.name)
    profile.hr_contact = data.get('hr_contact', profile.hr_contact)
    profile.website = data.get('website', profile.website)
    profile.description = data.get('description', profile.description)
    
    db.session.commit()
    return jsonify({
        'message': 'Profile updated successfully.',
        'profile': profile.to_dict()
    }), 200


@company_bp.route('/api/company/drives', methods=['POST'])
@login_required
@company_required
def create_drive():
    profile = current_user.company_profile
    if not profile.is_approved:
        return jsonify({'message': 'Your company profile is pending admin approval. You cannot create drives yet.'}), 403
        
    data = request.get_json() or {}
    job_title = data.get('job_title') or ""
    job_description = data.get('job_description') or ""
    branch_eligibility = data.get('branch_eligibility', 'All')
    cgpa_eligibility = data.get('cgpa_eligibility', 0.0)
    year_eligibility = data.get('year_eligibility')
    deadline_str = data.get('deadline')
    
    try:
        cgpa_val = float(cgpa_eligibility) if cgpa_eligibility else 0.0
    except ValueError:
        cgpa_val = 0.0

    try:
        year_val = int(year_eligibility) if year_eligibility else 2026
    except ValueError:
        year_val = 2026

    try:
        deadline_val = datetime.fromisoformat(deadline_str.replace('Z', '+00:00')) if deadline_str else datetime.utcnow()
    except ValueError:
        deadline_val = datetime.utcnow()
        
    new_drive = PlacementDrive(
        company_id=profile.id,
        job_title=job_title,
        job_description=job_description,
        branch_eligibility=branch_eligibility,
        cgpa_eligibility=cgpa_val,
        year_eligibility=year_val,
        deadline=deadline_val,
        status='Pending'
    )
    
    db.session.add(new_drive)
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({
        'message': 'Placement drive created and is awaiting admin approval.',
        'drive': new_drive.to_dict()
    }), 201


@company_bp.route('/api/company/drives', methods=['GET'])
@login_required
@company_required
def get_own_drives():
    profile = current_user.company_profile
    drives = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives]), 200


@company_bp.route('/api/company/drives/<int:drive_id>/applications', methods=['GET'])
@login_required
@company_required
def get_drive_applications(drive_id):
    profile = current_user.company_profile
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first()
    if not drive:
        return jsonify({'message': 'Placement drive not found or does not belong to your company.'}), 404
        
    apps = Application.query.filter_by(drive_id=drive_id).all()
    return jsonify([a.to_dict() for a in apps]), 200


@company_bp.route('/api/company/applications/<int:app_id>/status', methods=['POST'])
@login_required
@company_required
def update_application_status(app_id):
    profile = current_user.company_profile
    app = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == profile.id
    ).first()
    
    if not app:
        return jsonify({'message': 'Application not found.'}), 404
        
    data = request.get_json() or {}
    status = data.get('status')
    
    if status not in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        return jsonify({'message': 'Invalid status option.'}), 400
        
    app.status = status
    
    # Notify Student
    notif = Notification(
        user_id=app.student.user_id,
        message=f'Your application for {app.drive.job_title} at {profile.name} status updated to: {status}.'
    )
    db.session.add(notif)
    db.session.commit()
    
    if status == 'Selected':
        if cache:
            cache.delete('admin_dashboard_stats')
            
    return jsonify({
        'message': f'Application status updated to: {status}.',
        'application': app.to_dict()
    }), 200


@company_bp.route('/api/company/applications/<int:app_id>/schedule', methods=['POST'])
@login_required
@company_required
def schedule_interview(app_id):
    profile = current_user.company_profile
    app = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == profile.id
    ).first()
    
    if not app:
        return jsonify({'message': 'Application not found.'}), 404
        
    data = request.get_json() or {}
    interview_time_str = data.get('interview_scheduled_at')
    
    try:
        interview_time = datetime.fromisoformat(interview_time_str.replace('Z', '+00:00')) if interview_time_str else datetime.utcnow()
    except ValueError:
        interview_time = datetime.utcnow()
        
    app.interview_scheduled_at = interview_time
    
    # Notify Student
    notif = Notification(
        user_id=app.student.user_id,
        message=f'Interview scheduled for {app.drive.job_title} at {profile.name} on {interview_time.strftime("%d-%b-%Y %I:%M %p")}.'
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify({
        'message': 'Interview scheduled successfully.',
        'application': app.to_dict()
    }), 200
