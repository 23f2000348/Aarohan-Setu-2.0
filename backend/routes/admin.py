from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from backend.models.db_models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, cache

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'message': 'Administrator access required.'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/api/admin/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    if cache:
        cached_stats = cache.get('admin_dashboard_stats')
        if cached_stats:
            return jsonify(cached_stats), 200

    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    
    # Calculate placement rate (selected students / total students * 100)
    selected_students_count = db.session.query(Application.student_id).filter_by(status='Selected').distinct().count()
    placement_rate = round((selected_students_count / total_students * 100), 2) if total_students > 0 else 0.0
    
    # Branch distributions
    branches = db.session.query(StudentProfile.branch).distinct().all()
    branch_distribution = []
    for branch_tuple in branches:
        branch_name = branch_tuple[0]
        student_count = StudentProfile.query.filter_by(branch=branch_name).count()
        selected_count = db.session.query(Application.student_id)\
            .join(StudentProfile)\
            .filter(StudentProfile.branch == branch_name, Application.status == 'Selected')\
            .distinct().count()
        branch_distribution.append({
            'branch': branch_name,
            'students': student_count,
            'selected': selected_count
        })

    # Drive statuses
    drive_statuses = {
        'Pending': PlacementDrive.query.filter_by(status='Pending').count(),
        'Approved': PlacementDrive.query.filter_by(status='Approved').count(),
        'Rejected': PlacementDrive.query.filter_by(status='Rejected').count(),
        'Closed': PlacementDrive.query.filter_by(status='Closed').count()
    }
    
    stats_data = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'placement_rate': placement_rate,
        'branch_distribution': branch_distribution,
        'drive_statuses': drive_statuses
    }
    
    if cache:
        cache.set('admin_dashboard_stats', stats_data, timeout=60)
        
    return jsonify(stats_data), 200


@admin_bp.route('/api/admin/companies', methods=['GET'])
@login_required
@admin_required
def get_companies():
    companies = CompanyProfile.query.all()
    return jsonify([c.to_dict() for c in companies]), 200


@admin_bp.route('/api/admin/companies/<int:comp_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_company(comp_id):
    company = CompanyProfile.query.get(comp_id)
    if not company:
        return jsonify({'message': 'Company profile not found.'}), 404
        
    company.is_approved = True
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({'message': f'Company "{company.name}" has been approved.'}), 200


@admin_bp.route('/api/admin/companies/<int:comp_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_company(comp_id):
    company = CompanyProfile.query.get(comp_id)
    if not company:
        return jsonify({'message': 'Company profile not found.'}), 404
        
    user = company.user
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({'message': 'Company registration has been rejected.'}), 200


@admin_bp.route('/api/admin/companies/<int:comp_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_company(comp_id):
    company = CompanyProfile.query.get(comp_id)
    if not company:
        return jsonify({'message': 'Company profile not found.'}), 404
        
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    return jsonify({
        'message': f'Company "{company.name}" blacklist status set to {company.is_blacklisted}.',
        'is_blacklisted': company.is_blacklisted
    }), 200


@admin_bp.route('/api/admin/companies/<int:comp_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_company_active(comp_id):
    company = CompanyProfile.query.get(comp_id)
    if not company or not company.user:
        return jsonify({'message': 'Company user not found.'}), 404
        
    user = company.user
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({
        'message': f'Company user active status set to {user.is_active}.',
        'is_active': user.is_active
    }), 200


@admin_bp.route('/api/admin/students', methods=['GET'])
@login_required
@admin_required
def get_students():
    students = StudentProfile.query.all()
    return jsonify([s.to_dict() for s in students]), 200


@admin_bp.route('/api/admin/students/<int:stud_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_student(stud_id):
    student = StudentProfile.query.get(stud_id)
    if not student:
        return jsonify({'message': 'Student profile not found.'}), 404
        
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    return jsonify({
        'message': f'Student "{student.name}" blacklist status set to {student.is_blacklisted}.',
        'is_blacklisted': student.is_blacklisted
    }), 200


@admin_bp.route('/api/admin/students/<int:stud_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_student_active(stud_id):
    student = StudentProfile.query.get(stud_id)
    if not student or not student.user:
        return jsonify({'message': 'Student user not found.'}), 404
        
    user = student.user
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({
        'message': f'Student user active status set to {user.is_active}.',
        'is_active': user.is_active
    }), 200


@admin_bp.route('/api/admin/drives', methods=['GET'])
@login_required
@admin_required
def get_drives():
    drives = PlacementDrive.query.all()
    return jsonify([d.to_dict() for d in drives]), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Placement drive not found.'}), 404
        
    drive.status = 'Approved'
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({'message': f'Placement drive "{drive.job_title}" has been approved.'}), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Placement drive not found.'}), 404
        
    drive.status = 'Rejected'
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({'message': f'Placement drive "{drive.job_title}" registration rejected.'}), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/close', methods=['POST'])
@login_required
@admin_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Placement drive not found.'}), 404
        
    drive.status = 'Closed'
    db.session.commit()
    
    if cache:
        cache.delete('admin_dashboard_stats')
        
    return jsonify({'message': f'Placement drive "{drive.job_title}" is now closed.'}), 200


@admin_bp.route('/api/admin/applications', methods=['GET'])
@login_required
@admin_required
def get_applications():
    apps = Application.query.all()
    return jsonify([a.to_dict() for a in apps]), 200


@admin_bp.route('/api/admin/search', methods=['GET'])
@login_required
@admin_required
def search_entities():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'students': [], 'companies': []}), 200
        
    # Search students by name or email
    students = StudentProfile.query.join(User).filter(
        db.or_(StudentProfile.name.like(f'%{q}%'), User.email.like(f'%{q}%'))
    ).all()
    
    # Search companies by name or email
    companies = CompanyProfile.query.join(User).filter(
        db.or_(CompanyProfile.name.like(f'%{q}%'), User.email.like(f'%{q}%'))
    ).all()
    
    return jsonify({
        'students': [s.to_dict() for s in students],
        'companies': [c.to_dict() for c in companies]
    }), 200
