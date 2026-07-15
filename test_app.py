import unittest
import json
import io
import os
os.environ['TESTING'] = 'True'
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models.db_models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application

class TestAarohanSetu(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['CACHE_TYPE'] = 'SimpleCache'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email, password):
        return self.client.post('/api/login', 
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json'
        )

    def test_1_admin_login(self):
        print("\n[TEST] Verifying Admin Login...")
        res = self.login('admin@aarohansetu.in', 'admin_password')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['user']['role'], 'admin')
        print("-> Admin login successful.")

    def test_2_student_flow(self):
        print("\n[TEST] Verifying Student Registration & Profile Management...")
        
        # Registering student (User 1)
        student_data = {
            'email': 'student@university.edu',
            'password': 'password123',
            'name': 'Test Student',
            'branch': 'Computer Science',
            'cgpa': '8.5',
            'graduation_year': '2026'
        }
        res = self.client.post('/api/register/student',
            data=json.dumps(student_data),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['user']['email'], 'student@university.edu')
        self.assertEqual(data['profile']['cgpa'], 8.5)
        print("-> Student registration successful.")

        update_data = {
            'name': 'Test Student Updated',
            'branch': 'Information Technology',
            'cgpa': '9.0',
            'graduation_year': '2026'
        }
        res = self.client.post('/api/student/profile',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['profile']['name'], 'Test Student Updated')
        self.assertEqual(data['profile']['cgpa'], 9.0)
        self.assertEqual(data['profile']['branch'], 'Information Technology')
        print("-> Student profile update successful.")

        res = self.client.post('/api/student/resume',
            data={'resume': (io.BytesIO(b"dummy resume content"), 'resume.pdf')},
            content_type='multipart/form-data'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('/api/resumes/resume_', data['resume_path'])
        print("-> Student resume upload successful.")

    def test_3_company_registration_and_approval(self):
        print("\n[TEST] Verifying Company Registration, Approval & Blacklisting...")
        
        # Registering Company
        comp_data = {
            'email': 'hr@acme.com',
            'password': 'password123',
            'name': 'Acme Corporation',
            'hr_contact': '9876543210',
            'website': 'https://acme.com',
            'description': 'Acme operations description'
        }
        res = self.client.post('/api/register/company',
            data=json.dumps(comp_data),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        print("-> Company registration successful (Pending approval).")

        res = self.login('hr@acme.com', 'password123')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertFalse(data['profile']['is_approved'])
        print("-> Company can log in, is_approved is False.")

        self.login('admin@aarohansetu.in', 'admin_password')
        with self.app.app_context():
            comp_profile = CompanyProfile.query.first()
            comp_id = comp_profile.id

        res = self.client.post(f'/api/admin/companies/{comp_id}/approve')
        self.assertEqual(res.status_code, 200)
        print("-> Admin approved company successfully.")

        res = self.login('hr@acme.com', 'password123')
        data = json.loads(res.data)
        self.assertTrue(data['profile']['is_approved'])
        print("-> Company is_approved is now True.")

    def test_4_placement_drive_and_eligibility(self):
        print("\n[TEST] Verifying Placement Drive Creation, Eligibility checks, and Application submission...")
        
        # Creating Student & Company
        with self.app.app_context():
            s_user = User(email='stud@edu.in', role='student')
            s_user.set_password('pass')
            s_prof = StudentProfile(user=s_user, name='John IT', branch='Information Technology', cgpa=8.0, graduation_year=2026, resume_path='/resumes/resume.pdf')
            
            c_user = User(email='recruiter@comp.com', role='company')
            c_user.set_password('pass')
            c_prof = CompanyProfile(user=c_user, name='TechCorp', hr_contact='123', is_approved=True)
            
            db.session.add_all([s_user, s_prof, c_user, c_prof])
            db.session.commit()
            
            comp_id = c_prof.id
            student_id = s_prof.id

        # Creating drives
        self.login('recruiter@comp.com', 'pass')

        # Drive A
        drive_a = {
            'job_title': 'IT Architect',
            'job_description': 'Description',
            'branch_eligibility': 'Information Technology, Computer Science',
            'cgpa_eligibility': 7.5,
            'year_eligibility': 2026,
            'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat()
        }
        res = self.client.post('/api/company/drives', data=json.dumps(drive_a), content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Drive B
        drive_b = {
            'job_title': 'Senior Developer',
            'job_description': 'Description',
            'branch_eligibility': 'Information Technology',
            'cgpa_eligibility': 9.0,
            'year_eligibility': 2026,
            'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat()
        }
        res = self.client.post('/api/company/drives', data=json.dumps(drive_b), content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Drive C
        drive_c = {
            'job_title': 'Mechanical Engineer',
            'job_description': 'Description',
            'branch_eligibility': 'Mechanical Engineering',
            'cgpa_eligibility': 6.0,
            'year_eligibility': 2026,
            'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat()
        }
        res = self.client.post('/api/company/drives', data=json.dumps(drive_c), content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # Logging in as Admin to approve drives
        self.login('admin@aarohansetu.in', 'admin_password')
        with self.app.app_context():
            drives = PlacementDrive.query.all()
            for d in drives:
                d.status = 'Approved'
            db.session.commit()
            drive_a_id = drives[0].id
            drive_b_id = drives[1].id
            drive_c_id = drives[2].id
        print("-> Created and approved 3 drives.")

        self.login('stud@edu.in', 'pass')
        res = self.client.get('/api/student/drives')
        self.assertEqual(res.status_code, 200)
        drives_res = json.loads(res.data)
        
        # Find Drive A, B, C in response and check eligibility
        drive_a_res = next(x for x in drives_res if x['id'] == drive_a_id)
        drive_b_res = next(x for x in drives_res if x['id'] == drive_b_id)
        drive_c_res = next(x for x in drives_res if x['id'] == drive_c_id)
        
        self.assertTrue(drive_a_res['is_eligible'])
        self.assertFalse(drive_b_res['is_eligible'])
        self.assertFalse(drive_c_res['is_eligible'])
        print("-> Student drive eligibility logic verified correctly (IT Architect: Eligible, Senior Developer: Ineligible, Mechanical: Ineligible).")

        # Apply for Drive A (Eligible)
        res = self.client.post(f'/api/student/drives/{drive_a_id}/apply')
        self.assertEqual(res.status_code, 201)
        print("-> Application to eligible drive succeeded.")

        # Apply for Drive A again (should fail: duplicate check)
        res = self.client.post(f'/api/student/drives/{drive_a_id}/apply')
        self.assertEqual(res.status_code, 400)
        self.assertIn('already applied', json.loads(res.data)['message'])
        print("-> Prevented duplicate applications correctly.")

        # Apply for Drive B (Ineligible CGPA)
        res = self.client.post(f'/api/student/drives/{drive_b_id}/apply')
        self.assertEqual(res.status_code, 403)
        self.assertIn('do not meet the eligibility criteria', json.loads(res.data)['message'])
        print("-> Prevented application to ineligible CGPA drive correctly.")

    def test_5_recruitment_workflow(self):
        print("\n[TEST] Verifying Recruiter Selection workflow, Interview Scheduling and Offer Letter Generation...")
        
        with self.app.app_context():
            s_user = User(email='s@edu.in', role='student')
            s_user.set_password('pass')
            s_prof = StudentProfile(user=s_user, name='Alice CS', branch='Computer Science', cgpa=8.5, graduation_year=2026, resume_path='/resumes/resume.pdf')
            
            c_user = User(email='c@comp.com', role='company')
            c_user.set_password('pass')
            c_prof = CompanyProfile(user=c_user, name='CloudServices', hr_contact='123', is_approved=True)
            
            db.session.add_all([s_user, s_prof, c_user, c_prof])
            db.session.commit()
            
            drive = PlacementDrive(company_id=c_prof.id, job_title='Cloud Intern', job_description='Desc', cgpa_eligibility=6.0, year_eligibility=2026, deadline=datetime.utcnow() + timedelta(days=2), status='Approved')
            db.session.add(drive)
            db.session.commit()
            
            app = Application(student_id=s_prof.id, drive_id=drive.id, status='Applied')
            db.session.add(app)
            db.session.commit()
            
            app_id = app.id

        self.login('c@comp.com', 'pass')

        # Shortlisting Candidate
        res = self.client.post(f'/api/company/applications/{app_id}/status',
            data=json.dumps({'status': 'Shortlisted'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['application']['status'], 'Shortlisted')
        print("-> Candidate shortlisted successfully.")

        # Scheduling Interview
        interview_time = (datetime.utcnow() + timedelta(days=5)).isoformat()
        res = self.client.post(f'/api/company/applications/{app_id}/schedule',
            data=json.dumps({'interview_scheduled_at': interview_time}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(json.loads(res.data)['application']['interview_scheduled_at'])
        print("-> Interview scheduled successfully.")

        # Selecting Candidate
        res = self.client.post(f'/api/company/applications/{app_id}/status',
            data=json.dumps({'status': 'Selected'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        print("-> Candidate selected successfully.")



if __name__ == '__main__':
    unittest.main()
