from celery import Celery
from celery.schedules import crontab
import os
import csv
from datetime import datetime, timedelta

# Create celery application instance
celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
celery_app.conf.timezone = 'Asia/Kolkata'

# Setup schedule for beat
celery_app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'backend.tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # Run daily at 6:00 PM
    },
    'send-monthly-report': {
        'task': 'backend.tasks.send_monthly_activity_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Run first day of month at 9:00 AM
    }
}

# Lazy import helper to prevent circular imports
_flask_app = None
def get_flask_app():
    global _flask_app
    if _flask_app is None:
        from backend.app import create_app
        _flask_app = create_app()
    return _flask_app


@celery_app.task
def export_applications_csv(student_id):
    app = get_flask_app()
    with app.app_context():
        from backend.models.db_models import db, StudentProfile, Application, Notification
        
        student = StudentProfile.query.get(student_id)
        if not student:
            return f"Student {student_id} not found."
            
        # Create exports directory in frontend static root
        exports_dir = os.path.join(app.config['BASE_DIR'], '..', 'frontend', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        filename = f"applications_student_{student_id}_{int(datetime.utcnow().timestamp())}.csv"
        filepath = os.path.join(exports_dir, filename)
        
        # Query applications
        applications = Application.query.filter_by(student_id=student_id).all()
        
        # Write CSV
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Student Name', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])
            
            for a in applications:
                writer.writerow([
                    student.id,
                    student.name,
                    a.drive.company.name if a.drive and a.drive.company else 'N/A',
                    a.drive.job_title if a.drive else 'N/A',
                    a.status,
                    a.applied_at.strftime('%d-%b-%Y')
                ])
                
        # Create notification in database for the student
        download_url = f"/exports/{filename}"
        notif = Notification(
            user_id=student.user_id,
            message=f"Your applications history CSV export is complete. Click here to download."
        )
        # Store download url or reference inside message
        # Let's save a clear message that the frontend can parse or render as a link
        notif.message = f"CSV_EXPORT_READY|{download_url}|Your application history CSV is ready for download."
        
        db.session.add(notif)
        db.session.commit()
        
        return f"Successfully exported CSV for student {student_id} to {filename}"


@celery_app.task
def send_daily_reminders():
    app = get_flask_app()
    with app.app_context():
        from backend.models.db_models import db, StudentProfile, PlacementDrive, Application, Notification
        
        # Find active approved drives closing in the next 48 hours
        now = datetime.utcnow()
        limit = now + timedelta(hours=48)
        
        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'Approved',
            PlacementDrive.deadline > now,
            PlacementDrive.deadline <= limit
        ).all()
        
        if not upcoming_drives:
            print("No upcoming application deadlines in next 48 hours.")
            return "No deadlines found."
            
        reminders_sent = 0
        students = StudentProfile.query.filter_by(is_blacklisted=False).all()
        
        log_lines = [
            f"DAILY DEADLINE REMINDERS LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "============================================================"
        ]
        
        for drive in upcoming_drives:
            log_lines.append(f"\nDrive: {drive.job_title} at {drive.company.name} | Deadline: {drive.deadline.strftime('%d-%b-%Y %I:%M %p')}")
            
            # Check eligibility for each student
            for s in students:
                # Check if already applied
                has_applied = Application.query.filter_by(student_id=s.id, drive_id=drive.id).first() is not None
                if has_applied:
                    continue
                    
                # Eligibility checks
                cgpa_ok = s.cgpa >= drive.cgpa_eligibility
                year_ok = s.graduation_year == drive.year_eligibility
                branch_list = [b.strip().lower() for b in drive.branch_eligibility.split(',') if b.strip()]
                branch_ok = (
                    drive.branch_eligibility.lower() == 'all' or 
                    'all' in branch_list or 
                    s.branch.lower() in branch_list
                )
                
                if cgpa_ok and year_ok and branch_ok:
                    # Eligible student who hasn't applied!
                    # Create UI Notification alert
                    notif = Notification(
                        user_id=s.user_id,
                        message=f"Reminder: The application deadline for {drive.job_title} at {drive.company.name} is closing on {drive.deadline.strftime('%d-%b-%Y')}!"
                    )
                    db.session.add(notif)
                    reminders_sent += 1
                    log_lines.append(f"- Alerted Eligible Student: {s.name} ({s.user.email})")
        
        db.session.commit()
        
        # Write to log file in backend folder
        log_dir = os.path.join(app.config['BASE_DIR'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'daily_reminders.log')
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write("\n".join(log_lines) + "\n\n")
            
        return f"Daily reminders executed. Sent {reminders_sent} notifications."


@celery_app.task
def send_monthly_activity_report():
    app = get_flask_app()
    with app.app_context():
        from backend.models.db_models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
        
        # Fetch Admin
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            return "Admin user not found, report generation aborted."
            
        # Stats for the last 30 days
        now = datetime.utcnow()
        start_date = now - timedelta(days=30)
        
        total_students = StudentProfile.query.count()
        total_companies = CompanyProfile.query.count()
        
        # Drives conducted in the last month
        drives_conducted = PlacementDrive.query.filter(
            PlacementDrive.created_at >= start_date
        ).count()
        
        # Applications and selections
        apps_submitted = Application.query.filter(
            Application.applied_at >= start_date
        ).count()
        
        selected_students = Application.query.filter(
            Application.status == 'Selected',
            Application.applied_at >= start_date
        ).count()
        
        rejected_students = Application.query.filter(
            Application.status == 'Rejected',
            Application.applied_at >= start_date
        ).count()
        
        shortlisted_students = Application.query.filter(
            Application.status == 'Shortlisted',
            Application.applied_at >= start_date
        ).count()
        
        # Generate HTML report
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Times New Roman', Times, serif; color: #333; margin: 20px; }}
                h1 {{ color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }}
                h2 {{ color: #2b6cb0; margin-top: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: left; }}
                th {{ background-color: #f7fafc; font-weight: bold; color: #4a5568; }}
                .highlight {{ font-weight: bold; color: #2b6cb0; }}
                .footer {{ margin-top: 40px; font-size: 12px; color: #718096; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>Aarohan Setu 2.0 - Monthly Activity Report</h1>
            <p>Report generated on: <strong>{datetime.now().strftime('%d-%B-%Y')}</strong></p>
            <p>This report compiles placement cell activity metrics for the past 30 days (from {start_date.strftime('%d-%b-%Y')} to {now.strftime('%d-%b-%Y')}).</p>
            
            <h2>Institute Stats Summary</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Count / Value</th>
                </tr>
                <tr>
                    <td>Total Students Registered</td>
                    <td>{total_students}</td>
                </tr>
                <tr>
                    <td>Total Companies Registered</td>
                    <td>{total_companies}</td>
                </tr>
                <tr>
                    <td>New Placement Drives Initiated (Last 30 Days)</td>
                    <td class="highlight">{drives_conducted}</td>
                </tr>
                <tr>
                    <td>Total Applications Received (Last 30 Days)</td>
                    <td>{apps_submitted}</td>
                </tr>
            </table>

            <h2>Recruitment Status Metrics (Last 30 Days)</h2>
            <table>
                <tr>
                    <th>Application Status</th>
                    <th>Total Students</th>
                </tr>
                <tr>
                    <td style="color: #3182ce; font-weight: bold;">Shortlisted</td>
                    <td>{shortlisted_students}</td>
                </tr>
                <tr>
                    <td style="color: #38a169; font-weight: bold;">Selected (Offers Made)</td>
                    <td class="highlight">{selected_students}</td>
                </tr>
                <tr>
                    <td style="color: #e53e3e; font-weight: bold;">Rejected</td>
                    <td>{rejected_students}</td>
                </tr>
            </table>

            <div class="footer">
                <p>Aarohan Setu 2.0 Placement Portal • Automated Batch Report</p>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report file to reports directory
        reports_dir = os.path.join(app.config['BASE_DIR'], 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_filename = f"monthly_report_{now.strftime('%Y_%m')}.html"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
            
        # Log mock email sending to admin
        log_dir = os.path.join(app.config['BASE_DIR'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        email_log_path = os.path.join(log_dir, 'email_reports.log')
        
        with open(email_log_path, 'a', encoding='utf-8') as email_log:
            email_log.write(f"EMAIL SENT TO: {admin_user.email}\n")
            email_log.write(f"SUBJECT: Aarohan Setu 2.0 Monthly Activity Report - {now.strftime('%B %Y')}\n")
            email_log.write(f"ATTACHMENT: Saved to {report_path}\n")
            email_log.write("--- EMAIL CONTENT ---\n")
            email_log.write(report_html)
            email_log.write("\n========================================================================\n\n")
            
        return f"Monthly report compiled and sent mock email to admin. Report saved at {report_filename}."
