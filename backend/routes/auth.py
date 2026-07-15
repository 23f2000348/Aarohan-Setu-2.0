from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from backend.models.db_models import db, User, StudentProfile, CompanyProfile, Notification

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register/student', methods=['POST'])
def register_student():
    data = request.get_json() or {}
    email = data.get('email') or ""
    password = data.get('password') or ""
    name = data.get('name') or ""
    branch = data.get('branch') or ""
    cgpa = data.get('cgpa')
    graduation_year = data.get('graduation_year')
    
    try:
        cgpa_val = float(cgpa) if cgpa else 0.0
        grad_year_val = int(graduation_year) if graduation_year else 2026
    except ValueError:
        cgpa_val = 0.0
        grad_year_val = 2026

    new_user = User(email=email, role='student')
    new_user.set_password(password)
    
    student_prof = StudentProfile(
        user=new_user,
        name=name,
        branch=branch,
        cgpa=cgpa_val,
        graduation_year=grad_year_val
    )
    
    db.session.add(new_user)
    db.session.add(student_prof)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({
        'message': 'Student registered and logged in successfully.',
        'user': new_user.to_dict(),
        'profile': student_prof.to_dict()
    }), 201


@auth_bp.route('/api/register/company', methods=['POST'])
def register_company():
    data = request.get_json() or {}
    email = data.get('email') or ""
    password = data.get('password') or ""
    name = data.get('name') or ""
    hr_contact = data.get('hr_contact') or ""
    website = data.get('website') or ""
    description = data.get('description') or ""
    
    new_user = User(email=email, role='company')
    new_user.set_password(password)
    
    company_prof = CompanyProfile(
        user=new_user,
        name=name,
        hr_contact=hr_contact,
        website=website,
        description=description,
        is_approved=False
    )
    
    db.session.add(new_user)
    db.session.add(company_prof)
    db.session.commit()
    
    return jsonify({
        'message': 'Company registered successfully. Waiting for admin approval.',
        'user': new_user.to_dict()
    }), 201


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email') or ""
    password = data.get('password') or ""
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password.'}), 401
        
    if not user.is_active:
        return jsonify({'message': 'Your account has been deactivated.'}), 403
        
    # Check blacklisting
    if user.role == 'student' and user.student_profile.is_blacklisted:
        return jsonify({'message': 'Your student profile has been blacklisted.'}), 403
        
    if user.role == 'company' and user.company_profile.is_blacklisted:
        return jsonify({'message': 'Your company profile has been blacklisted.'}), 403
        
    login_user(user)
    
    profile = None
    if user.role == 'student':
        profile = user.student_profile.to_dict()
    elif user.role == 'company':
        profile = user.company_profile.to_dict()
        
    return jsonify({
        'message': 'Logged in successfully.',
        'user': user.to_dict(),
        'profile': profile
    }), 200


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200


@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({'authenticated': False}), 200
        
    profile = None
    if current_user.role == 'student':
        profile = current_user.student_profile.to_dict()
    elif current_user.role == 'company':
        profile = current_user.company_profile.to_dict()
        
    return jsonify({
        'authenticated': True,
        'user': current_user.to_dict(),
        'profile': profile
    }), 200


@auth_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications]), 200


@auth_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first()
    if not notif:
        return jsonify({'message': 'Notification not found.'}), 404
    notif.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read.'}), 200
