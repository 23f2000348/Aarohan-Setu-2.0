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
    job_title = data.get('job_title')
    job_description = data.get('job_description')
    branch_eligibility = data.get('branch_eligibility', 'All')
    cgpa_eligibility = data.get('cgpa_eligibility', 0.0)
    year_eligibility = data.get('year_eligibility')
    deadline_str = data.get('deadline')
    
    if not all([job_title, job_description, year_eligibility, deadline_str]):
        return jsonify({'message': 'Job Title, Description, Graduation Year eligibility and Application Deadline are required.'}), 400
        
    try:
        cgpa_val = float(cgpa_eligibility)
        year_val = int(year_eligibility)
        # Parse ISO datetime
        deadline_val = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'message': 'Invalid CGPA, Graduation Year, or Deadline format.'}), 400
        
    new_drive = PlacementDrive(
        company_id=profile.id,
        job_title=job_title,
        job_description=job_description,
        branch_eligibility=branch_eligibility,
        cgpa_eligibility=cgpa_val,
        year_eligibility=year_val,
        deadline=deadline_val,
        status='Pending'  # Must be approved by Admin
    )
    
    db.session.add(new_drive)
    db.session.commit()
    
    # Invalidate stats cache
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
    
    # Invalidate stats cache if selected
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
    
    if not interview_time_str:
        return jsonify({'message': 'Interview date and time is required.'}), 400
        
    try:
        interview_time = datetime.fromisoformat(interview_time_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'message': 'Invalid interview date format.'}), 400
        
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


@company_bp.route('/api/company/applications/<int:app_id>/offer-letter', methods=['POST'])
@login_required
@company_required
def generate_offer_letter(app_id):
    profile = current_user.company_profile
    app = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == profile.id
    ).first()
    
    if not app:
        return jsonify({'message': 'Application not found.'}), 404
        
    if app.status != 'Selected':
        return jsonify({'message': 'Offer letter can only be generated for selected students.'}), 400
        
    # Generate mock offer letter path/reference
    offer_filename = f"offer_{app.student.id}_{app.drive_id}_{int(datetime.utcnow().timestamp())}.txt"
    offer_dir = os.path.join(current_app.config['BASE_DIR'], 'offer_letters')
    os.makedirs(offer_dir, exist_ok=True)
    offer_path = os.path.join(offer_dir, offer_filename)
    
    # Write details to mock offer letter file
    with open(offer_path, 'w', encoding='utf-8') as f:
        f.write(f"OFFER OF PLACEMENT\n")
        f.write(f"==================\n\n")
        f.write(f"Date: {datetime.utcnow().strftime('%d-%B-%Y')}\n\n")
        f.write(f"Dear {app.student.name},\n\n")
        f.write(f"On behalf of {profile.name}, we are pleased to offer you the position of {app.drive.job_title}.\n")
        f.write(f"We were highly impressed by your academic record (CGPA: {app.student.cgpa}) and interview performance.\n\n")
        f.write(f"Key Terms:\n")
        f.write(f"- Position: {app.drive.job_title}\n")
        f.write(f"- Company: {profile.name}\n")
        f.write(f"- HR Contact: {profile.hr_contact}\n")
        f.write(f"- Verification Code: AAROHAN-SETU-{app.id}\n\n")
        f.write(f"Congratulations on your selection!\n\n")
        f.write(f"Sincerely,\n")
        f.write(f"HR Team, {profile.name}\n")
        f.write(f"Aarohan Setu 2.0 Placement Portal Verification\n")
        
    app.offer_letter_path = f"/api/offer-letters/{offer_filename}"
    
    # Notify Student
    notif = Notification(
        user_id=app.student.user_id,
        message=f'Offer letter generated for {app.drive.job_title} at {profile.name}! You can download it now.'
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify({
        'message': 'Offer letter generated successfully.',
        'application': app.to_dict()
    }), 200
