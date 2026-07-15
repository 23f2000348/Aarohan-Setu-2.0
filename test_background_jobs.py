import unittest
import os
os.environ['TESTING'] = 'True'
import glob
import csv
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models.db_models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Notification
from backend.tasks import send_daily_reminders, send_monthly_activity_report, export_applications_csv

class TestBackgroundJobsAndCaching(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['CACHE_TYPE'] = 'SimpleCache'
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        import backend.tasks
        backend.tasks._flask_app = self.app
        from backend.models.db_models import cache
        if cache:
            cache.clear()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_daily_reminders(self):
        print("\n[JOB TEST] Testing Daily Reminders...")
        
        # 1. Setup Student
        s_user = User(email='student@edu.in', role='student')
        s_user.set_password('password')
        s_prof = StudentProfile(user=s_user, name='Jane CS', branch='Computer Science', cgpa=8.0, graduation_year=2026)
        
        # 2. Setup Company (Approved)
        c_user = User(email='hr@techcorp.com', role='company')
        c_user.set_password('password')
        c_prof = CompanyProfile(user=c_user, name='TechCorp', hr_contact='123456', is_approved=True)
        
        db.session.add_all([s_user, s_prof, c_user, c_prof])
        db.session.commit()

        # 3. Setup Placement Drives
        # Drive A: Closing in 24 hours (should trigger reminder)
        drive_a = PlacementDrive(
            company_id=c_prof.id,
            job_title='Eligible Intern',
            job_description='Test Description',
            branch_eligibility='Computer Science',
            cgpa_eligibility=7.0,
            year_eligibility=2026,
            deadline=datetime.utcnow() + timedelta(hours=24),
            status='Approved'
        )

        # Drive B: Closing in 72 hours
        drive_b = PlacementDrive(
            company_id=c_prof.id,
            job_title='Far Deadline Intern',
            job_description='Test Description',
            branch_eligibility='Computer Science',
            cgpa_eligibility=7.0,
            year_eligibility=2026,
            deadline=datetime.utcnow() + timedelta(hours=72),
            status='Approved'
        )

        # Drive C: Closing in 24 hours(should NOT trigger reminder)
        drive_c = PlacementDrive(
            company_id=c_prof.id,
            job_title='High CGPA Intern',
            job_description='Test Description',
            branch_eligibility='Computer Science',
            cgpa_eligibility=9.0,
            year_eligibility=2026,
            deadline=datetime.utcnow() + timedelta(hours=24),
            status='Approved'
        )

        db.session.add_all([drive_a, drive_b, drive_c])
        db.session.commit()

        # Clearing any existing log file
        log_path = os.path.join(self.app.config['BASE_DIR'], 'logs', 'daily_reminders.log')
        if os.path.exists(log_path):
            os.remove(log_path)

        result = send_daily_reminders()
        print(f"-> Job result: {result}")
        self.assertIn("Sent 1 notifications", result)

        notifications = Notification.query.filter_by(user_id=s_user.id).all()
        self.assertEqual(len(notifications), 1)
        self.assertIn("Eligible Intern", notifications[0].message)
        print("-> DB Notification successfully verified.")

        self.assertTrue(os.path.exists(log_path))
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Eligible Intern", content)
            self.assertIn("High CGPA Intern", content)
            self.assertNotIn("Far Deadline Intern", content)
            self.assertEqual(content.count("Alerted Eligible Student: Jane CS"), 1)
        print("-> Daily Reminders log file successfully verified.")

    def test_monthly_activity_report(self):
        print("\n[JOB TEST] Testing Monthly Activity Report...")

        s_user = User(email='s@edu.in', role='student')
        s_user.set_password('pass')
        s_prof = StudentProfile(user=s_user, name='Alice', branch='Computer Science', cgpa=8.5, graduation_year=2026)
        
        c_user = User(email='c@comp.com', role='company')
        c_user.set_password('pass')
        c_prof = CompanyProfile(user=c_user, name='CloudServices', hr_contact='123', is_approved=True)
        
        db.session.add_all([s_user, s_prof, c_user, c_prof])
        db.session.commit()

        drive = PlacementDrive(
            company_id=c_prof.id,
            job_title='Software Dev',
            job_description='Desc',
            cgpa_eligibility=6.0,
            year_eligibility=2026,
            deadline=datetime.utcnow() + timedelta(days=5),
            status='Approved',
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(drive)
        db.session.commit()

        app = Application(student_id=s_prof.id, drive_id=drive.id, status='Selected', applied_at=datetime.utcnow() - timedelta(days=1))
        db.session.add(app)
        db.session.commit()

        # Clear reports and email log
        reports_dir = os.path.join(self.app.config['BASE_DIR'], 'reports')
        email_log_path = os.path.join(self.app.config['BASE_DIR'], 'logs', 'email_reports.log')
        if os.path.exists(email_log_path):
            os.remove(email_log_path)

        result = send_monthly_activity_report()
        print(f"-> Job result: {result}")
        self.assertIn("Monthly report compiled", result)

        html_files = glob.glob(os.path.join(reports_dir, 'monthly_report_*.html'))
        self.assertGreater(len(html_files), 0)
        with open(html_files[0], 'r', encoding='utf-8') as f:
            html_content = f.read()
            self.assertIn("Aarohan Setu 2.0 - Monthly Activity Report", html_content)
            self.assertIn("New Placement Drives Initiated (Last 30 Days)", html_content)
            self.assertIn("Selected (Offers Made)", html_content)
        print("-> HTML Monthly Report file successfully verified.")

        # Checking Email Log
        self.assertTrue(os.path.exists(email_log_path))
        with open(email_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
            self.assertIn("EMAIL SENT TO: admin@aarohansetu.in", log_content)
            self.assertIn("SUBJECT: Aarohan Setu 2.0 Monthly Activity Report", log_content)
        print("-> Admin email log successfully verified.")

    def test_export_applications_csv(self):
        print("\n[JOB TEST] Testing Async CSV Export...")

        # Clearing existing CSV files in exports folder
        exports_dir = os.path.normpath(os.path.join(self.app.config['BASE_DIR'], '..', 'frontend', 'exports'))
        if os.path.exists(exports_dir):
            for f in glob.glob(os.path.join(exports_dir, 'applications_student_*.csv')):
                try:
                    os.remove(f)
                except OSError:
                    pass

        # Setup Student, Company, Drive, Applications
        s_user = User(email='std@edu.in', role='student')
        s_user.set_password('pass')
        s_prof = StudentProfile(user=s_user, name='Alice Export', branch='Computer Science', cgpa=8.5, graduation_year=2026)
        
        c_user = User(email='cmp@comp.com', role='company')
        c_user.set_password('pass')
        c_prof = CompanyProfile(user=c_user, name='Excel Corp', hr_contact='123', is_approved=True)
        
        db.session.add_all([s_user, s_prof, c_user, c_prof])
        db.session.commit()

        drive1 = PlacementDrive(company_id=c_prof.id, job_title='Data Analyst', job_description='Desc', cgpa_eligibility=6.0, year_eligibility=2026, deadline=datetime.utcnow() + timedelta(days=2), status='Approved')
        drive2 = PlacementDrive(company_id=c_prof.id, job_title='Systems Engineer', job_description='Desc', cgpa_eligibility=6.0, year_eligibility=2026, deadline=datetime.utcnow() + timedelta(days=2), status='Approved')
        db.session.add_all([drive1, drive2])
        db.session.commit()

        app1 = Application(student_id=s_prof.id, drive_id=drive1.id, status='Shortlisted')
        app2 = Application(student_id=s_prof.id, drive_id=drive2.id, status='Applied')
        db.session.add_all([app1, app2])
        db.session.commit()

        # Running CSV export task
        result = export_applications_csv(s_prof.id)
        print(f"-> Job result: {result}")
        self.assertIn("Successfully exported CSV", result)

        exports_dir = os.path.normpath(os.path.join(self.app.config['BASE_DIR'], '..', 'frontend', 'exports'))
        csv_files = glob.glob(os.path.join(exports_dir, f'applications_student_{s_prof.id}_*.csv'))
        self.assertEqual(len(csv_files), 1)

        with open(csv_files[0], mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(rows[0], ['Student ID', 'Student Name', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])
            
            self.assertEqual(rows[1][0], str(s_prof.id))
            self.assertEqual(rows[1][1], 'Alice Export')
            self.assertEqual(rows[1][2], 'Excel Corp')
            self.assertEqual(rows[1][3], 'Data Analyst')
            self.assertEqual(rows[1][4], 'Shortlisted')

            self.assertEqual(rows[2][3], 'Systems Engineer')
            self.assertEqual(rows[2][4], 'Applied')

        print("-> Exported CSV file content successfully verified.")

        notif = Notification.query.filter_by(user_id=s_user.id).first()
        self.assertIsNotNone(notif)
        self.assertTrue(notif.message.startswith("CSV_EXPORT_READY|"))
        print("-> Student download link notification successfully verified.")

    def test_caching_performance(self):
        print("\n[CACHE TEST] Testing Admin Stats API Caching...")

        s_user = User(email='student_cache@edu.in', role='student')
        s_user.set_password('pass')
        s_prof = StudentProfile(user=s_user, name='Cache Stud', branch='Computer Science', cgpa=8.5, graduation_year=2026)
        db.session.add_all([s_user, s_prof])
        db.session.commit()

        login_res = self.client.post('/api/login', json={'email': 'admin@aarohansetu.in', 'password': 'admin_password'})
        self.assertEqual(login_res.status_code, 200)

        res1 = self.client.get('/api/admin/stats')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertEqual(data1['total_students'], 1)

        db.session.add(StudentProfile(
            user=User(email='student_cache2@edu.in', role='student', password_hash='hash'), 
            name='Cache Stud 2', branch='Information Technology', cgpa=9.0, graduation_year=2026
        ))
        db.session.commit()

        self.assertEqual(StudentProfile.query.count(), 2)

        res2 = self.client.get('/api/admin/stats')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2['total_students'], 1)
        print("-> Cached hit verified (returned 1 student despite database having 2).")

        from backend.app import cache
        if cache:
            cache.delete('admin_dashboard_stats')

        res3 = self.client.get('/api/admin/stats')
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertEqual(data3['total_students'], 2)
        print("-> Cache invalidation and reload verified (returned 2 students).")

if __name__ == '__main__':
    unittest.main()
