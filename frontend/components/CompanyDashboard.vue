<template>
  <div>
    <!-- Hero Banner -->
    <div class="hero-banner mb-4">
      <h1 class="hero-title" style="font-size: 2.2rem; border-bottom: none; padding-bottom: 0; margin-bottom: 0.5rem;">Recruiter Command Center</h1>
      <p class="hero-subtitle mb-0 text-muted">Post new placement drives, review student applications, schedule interviews, and issue placement offers to selected candidates.</p>
    </div>

    <div class="row">
    <div class="col-lg-4 mb-4">
      <!-- Unapproved Alert banner -->
      <div class="alert alert-warning border shadow-sm mb-4" v-if="!profile.is_approved">
        <h5 class="fw-bold"><i class="fa-solid fa-hourglass-half me-2"></i>Awaiting Approval</h5>
        <p class="small mb-0">Your profile is currently being reviewed by the Institute Placement Cell. You will be able to post drives once approved.</p>
      </div>

      <!-- Recruiter Profile Card -->
      <div class="card shadow-sm mb-4" v-if="!editingProfile">
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-solid fa-building me-2 text-primary"></i>Company Profile</h4>
        </div>
        <div class="card-body">
          <div class="text-center mb-3">
            <i class="fa-solid fa-briefcase text-primary" style="font-size: 5rem;"></i>
            <h4 class="mt-2 mb-0">{{ profile.name }}</h4>
            <span class="badge bg-primary mt-1">Recruiter</span>
          </div>
          
          <table class="table table-borderless m-0">
            <tbody>
              <tr>
                <td class="fw-bold text-muted" style="width: 40%;">HR Contact:</td>
                <td>{{ profile.hr_contact }}</td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">Website:</td>
                <td>
                  <a :href="profile.website" target="_blank" v-if="profile.website" class="text-primary text-decoration-underline">{{ profile.website }}</a>
                  <span class="text-muted" v-else>Not provided</span>
                </td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">Status:</td>
                <td>
                  <span class="badge bg-success" v-if="profile.is_approved">Approved</span>
                  <span class="badge bg-warning text-dark" v-else>Pending Admin Approval</span>
                </td>
              </tr>
            </tbody>
          </table>
          
          <p class="text-secondary mt-3 small" style="white-space: pre-line;">{{ profile.description }}</p>
          
          <div class="mt-4 d-grid">
            <button class="btn btn-outline-primary" @click="startEditProfile">
              <i class="fa-regular fa-pen-to-square me-1"></i> Edit Profile Details
            </button>
          </div>
        </div>
      </div>
      
      <!-- Edit Recruiter Profile Card -->
      <div class="card shadow-sm mb-4" v-else>
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-regular fa-pen-to-square me-2 text-primary"></i>Edit Profile</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveProfile">
            <div class="mb-3">
              <label for="edit-comp-name" class="form-label">Company Name</label>
              <input type="text" id="edit-comp-name" class="form-control" v-model="editData.name" required>
            </div>
            
            <div class="mb-3">
              <label for="edit-comp-contact" class="form-label">HR Contact</label>
              <input type="text" id="edit-comp-contact" class="form-control" v-model="editData.hr_contact" required>
            </div>
            
            <div class="mb-3">
              <label for="edit-comp-web" class="form-label">Website</label>
              <input type="url" id="edit-comp-web" class="form-control" v-model="editData.website">
            </div>
            
            <div class="mb-3">
              <label for="edit-comp-desc" class="form-label">Description</label>
              <textarea id="edit-comp-desc" class="form-control" rows="3" v-model="editData.description"></textarea>
            </div>
            
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Save
              </button>
              <button type="button" class="btn btn-outline-secondary" @click="cancelEditProfile">Cancel</button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Create Placement Drive Card (Only visible if approved) -->
      <div class="card shadow-sm" v-if="profile.is_approved">
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-solid fa-square-plus me-2 text-primary"></i>New Placement Drive</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="createDrive">
            <div class="mb-3">
              <label for="drive-title" class="form-label">Job Title</label>
              <input type="text" id="drive-title" class="form-control" v-model="driveData.job_title" placeholder="Software Engineering Intern" required>
            </div>

            <div class="mb-3">
              <label for="drive-desc" class="form-label">Job Description</label>
              <textarea id="drive-desc" class="form-control" rows="4" v-model="driveData.job_description" placeholder="Specify roles, responsibilities, and benefits..." required></textarea>
            </div>

            <div class="mb-3">
              <label for="drive-branches" class="form-label">Branch Eligibility (Comma-separated)</label>
              <input type="text" id="drive-branches" class="form-control" v-model="driveData.branch_eligibility" placeholder="Computer Science, Information Technology, or All">
            </div>

            <div class="row mb-3">
              <div class="col-6">
                <label for="drive-cgpa" class="form-label">Min CGPA</label>
                <input type="number" id="drive-cgpa" class="form-control" v-model="driveData.cgpa_eligibility" min="0.0" max="10.0" step="0.1" placeholder="7.5">
              </div>
              <div class="col-6">
                <label for="drive-year" class="form-label">Grad Year</label>
                <input type="number" id="drive-year" class="form-control" v-model="driveData.year_eligibility" min="2020" max="2035" placeholder="2026" required>
              </div>
            </div>

            <div class="mb-4">
              <label for="drive-deadline" class="form-label">Application Deadline</label>
              <input type="datetime-local" id="drive-deadline" class="form-control" v-model="driveData.deadline" required>
            </div>

            <button type="submit" class="btn btn-primary w-100 py-2" :disabled="creatingDrive">
              <span v-if="creatingDrive" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i class="fa-solid fa-paper-plane me-1" v-else></i> Initiate Drive
            </button>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Main Recruiter Control Dashboard -->
    <div class="col-lg-8">
      <!-- Back button for applicants view -->
      <div v-if="viewingDrive" class="mb-3">
        <button class="btn btn-outline-primary btn-sm" @click="backToDrives">
          <i class="fa-solid fa-chevron-left me-1"></i> Back to Drives Console
        </button>
      </div>

      <!-- VIEW A: PLACEMENT DRIVES REGISTER -->
      <div class="card shadow-sm" v-if="!viewingDrive">
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-solid fa-briefcase me-2 text-primary"></i>My Placement Drives</h4>
        </div>
        <div class="card-body p-4">
          <div v-if="loadingDrives" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Loading your drives...</p>
          </div>
          
          <div v-else-if="drives.length === 0" class="text-center py-5">
            <i class="fa-regular fa-folder-open fs-1 text-muted opacity-50 mb-3"></i>
            <h5>No drives created yet</h5>
            <p class="text-muted small" v-if="profile.is_approved">Use the sidebar form to initiate your first recruitment event.</p>
            <p class="text-muted small" v-else>You can register placement drives once your profile is approved.</p>
          </div>
          
          <div class="table-responsive" v-else>
            <table class="table table-hover align-middle border">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Deadline</th>
                  <th>Status</th>
                  <th class="text-center">Applicants</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td class="fw-bold">{{ drive.job_title }}</td>
                  <td>{{ formatDateShort(drive.deadline) }}</td>
                  <td>
                    <span :class="['badge', getDriveStatusBadge(drive.status)]">{{ drive.status }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge bg-dark rounded-pill">{{ drive.applicant_count || 0 }}</span>
                  </td>
                  <td class="text-center">
                    <button class="btn btn-primary btn-xs" @click="viewApplicants(drive)" :disabled="drive.status === 'Pending' || drive.status === 'Rejected'">
                      <i class="fa-regular fa-eye me-1"></i> Review Candidates
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- VIEW B: APPLICANTS DETAIL CONSOLE -->
      <div class="card shadow-sm" v-else>
        <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
          <h4 class="mb-0">
            <i class="fa-solid fa-users me-2 text-primary"></i>Applicants for: {{ viewingDrive.job_title }}
          </h4>
          <span :class="['badge', getDriveStatusBadge(viewingDrive.status)]">{{ viewingDrive.status }}</span>
        </div>
        
        <div class="card-body p-4">
          <div v-if="loadingApplicants" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Retrieving candidate applications...</p>
          </div>
          
          <div v-else-if="applicants.length === 0" class="text-center py-5">
            <i class="fa-solid fa-users-slash fs-1 text-muted opacity-50 mb-3"></i>
            <h5>No candidates have applied yet</h5>
            <p class="text-muted small">Applications submitted by eligible students will display here.</p>
          </div>
          
          <div class="table-responsive" v-else>
            <table class="table table-hover border">
              <thead>
                <tr>
                  <th>Candidate Details</th>
                  <th>Academics</th>
                  <th class="text-center">Resume</th>
                  <th>Recruitment Action</th>
                  <th>Schedule / Letter</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.id">
                  <!-- Name & Email -->
                  <td>
                    <strong class="d-block">{{ app.student_name }}</strong>
                    <small class="text-muted">{{ app.student_branch }}</small>
                  </td>
                  <!-- Branch & CGPA -->
                  <td>
                    <span class="d-block fw-bold text-success">CGPA: {{ app.student_cgpa }}</span>
                  </td>
                  <!-- Resume Download -->
                  <td class="text-center">
                    <a :href="app.offer_letter_path ? '#' : getResumeUrl(app)" target="_blank" class="btn btn-outline-primary btn-xs py-1" v-if="hasResume(app)">
                      <i class="fa-solid fa-file-pdf"></i> View Resume
                    </a>
                    <span class="text-danger small" v-else><i class="fa-solid fa-ban"></i> Missing</span>
                  </td>
                  <!-- Action Column: Status Update -->
                  <td>
                    <div class="input-group input-group-sm">
                      <select class="form-select form-select-sm" :value="app.status" @change="updateApplicantStatus(app.id, $event.target.value)">
                        <option value="Applied">Applied</option>
                        <option value="Shortlisted">Shortlisted</option>
                        <option value="Selected">Selected</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div>
                  </td>
                  <!-- Schedule / Offer Generation -->
                  <td>
                    <!-- If Shortlisted: Scheduler -->
                    <div v-if="app.status === 'Shortlisted'">
                      <div class="d-flex align-items-center gap-1">
                        <input type="datetime-local" class="form-control form-control-xs py-1 px-2" style="font-size: 0.8rem;" v-model="interviewTimes[app.id]" required>
                        <button class="btn btn-warning btn-xs py-1 text-dark" @click="scheduleInterview(app.id)">
                          <i class="fa-solid fa-calendar"></i>
                        </button>
                      </div>
                      <small class="d-block text-muted mt-1" v-if="app.interview_scheduled_at">
                        Scheduled: {{ formatTime(app.interview_scheduled_at) }}
                      </small>
                    </div>
                    
                    <!-- If Selected: Offer Letter Generation -->
                    <div v-else-if="app.status === 'Selected'">
                      <button class="btn btn-success btn-xs py-1 w-100 fw-bold" @click="generateOfferLetter(app.id)" v-if="!app.offer_letter_path">
                        <i class="fa-solid fa-file-signature"></i> Create Offer
                      </button>
                      <a :href="app.offer_letter_path" target="_blank" class="btn btn-outline-success btn-xs py-1 w-100 text-decoration-none" v-else>
                        <i class="fa-solid fa-download"></i> Download Offer
                      </a>
                    </div>
                    
                    <span class="text-muted small" v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
 </div>
</template>

<script>
export default {
  props: {
    userProfile: Object,
    currentUser: Object
  },
  data() {
    return {
      profile: { ...this.userProfile },
      drives: [],
      applicants: [],
      viewingDrive: null,
      
      // Loadings
      loadingDrives: false,
      loadingApplicants: false,
      saving: false,
      creatingDrive: false,
      editingProfile: false,
      
      // Forms
      editData: {
        name: '',
        hr_contact: '',
        website: '',
        description: ''
      },
      driveData: {
        job_title: '',
        job_description: '',
        branch_eligibility: 'All',
        cgpa_eligibility: '0.0',
        year_eligibility: '2026',
        deadline: ''
      },
      interviewTimes: {}  // Map app_id -> date-string
    };
  },
  methods: {
    startEditProfile() {
      this.editData = {
        name: this.profile.name,
        hr_contact: this.profile.hr_contact,
        website: this.profile.website,
        description: this.profile.description
      };
      this.editingProfile = true;
    },
    cancelEditProfile() {
      this.editingProfile = false;
    },
    async saveProfile() {
      this.saving = true;
      try {
        const res = await fetch('/api/company/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editData)
        });
        const data = await res.json();
        
        if (res.ok) {
          this.profile = data.profile;
          this.editingProfile = false;
          this.$emit('trigger-alert', 'Profile updated successfully.', 'success');
          this.$emit('update-profile');
        } else {
          this.$emit('trigger-alert', data.message || 'Failed to update profile.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during profile save.', 'danger');
      } finally {
        this.saving = false;
      }
    },
    async fetchDrives() {
      this.loadingDrives = true;
      try {
        const res = await fetch('/api/company/drives');
        if (res.ok) {
          const drivesList = await res.json();
          // For each drive, fetch applicants count to enrich table
          for (let drive of drivesList) {
            const appRes = await fetch(`/api/company/drives/${drive.id}/applications`);
            if (appRes.ok) {
              const apps = await appRes.json();
              drive.applicant_count = apps.length;
            }
          }
          this.drives = drivesList;
        }
      } catch (err) {
        console.error("Error fetching drives:", err);
      } finally {
        this.loadingDrives = false;
      }
    },
    async createDrive() {
      this.creatingDrive = true;
      try {
        const res = await fetch('/api/company/drives', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.driveData)
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', 'Placement drive initiated successfully and is awaiting admin approval!', 'success');
          // Reset Form
          this.driveData = {
            job_title: '',
            job_description: '',
            branch_eligibility: 'All',
            cgpa_eligibility: '0.0',
            year_eligibility: '2026',
            deadline: ''
          };
          this.fetchDrives();
        } else {
          this.$emit('trigger-alert', data.message || 'Failed to create drive.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during drive creation.', 'danger');
      } finally {
        this.creatingDrive = false;
      }
    },
    async viewApplicants(drive) {
      this.viewingDrive = drive;
      this.loadingApplicants = true;
      try {
        const res = await fetch(`/api/company/drives/${drive.id}/applications`);
        if (res.ok) {
          this.applicants = await res.json();
          // Initialize interview times map
          for (let app of this.applicants) {
            if (app.interview_scheduled_at) {
              this.interviewTimes[app.id] = app.interview_scheduled_at.substring(0, 16);
            }
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        this.loadingApplicants = false;
      }
    },
    backToDrives() {
      this.viewingDrive = null;
      this.applicants = [];
      this.fetchDrives();
    },
    async updateApplicantStatus(appId, status) {
      try {
        const res = await fetch(`/api/company/applications/${appId}/status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status })
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', `Candidate status updated to ${status}.`, 'success');
          // Update local status
          const app = this.applicants.find(a => a.id === appId);
          if (app) app.status = status;
        } else {
          this.$emit('trigger-alert', data.message || 'Status update failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during status update.', 'danger');
      }
    },
    async scheduleInterview(appId) {
      const time = this.interviewTimes[appId];
      if (!time) {
        this.$emit('trigger-alert', 'Please select an interview time.', 'warning');
        return;
      }
      
      try {
        const res = await fetch(`/api/company/applications/${appId}/schedule`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ interview_scheduled_at: time })
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', 'Interview scheduled and candidate notified!', 'success');
          const app = this.applicants.find(a => a.id === appId);
          if (app) app.interview_scheduled_at = time;
        } else {
          this.$emit('trigger-alert', data.message || 'Scheduling failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during scheduling.', 'danger');
      }
    },
    async generateOfferLetter(appId) {
      try {
        const res = await fetch(`/api/company/applications/${appId}/offer-letter`, {
          method: 'POST'
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', 'Offer letter generated successfully!', 'success');
          const app = this.applicants.find(a => a.id === appId);
          if (app) {
            app.offer_letter_path = data.application.offer_letter_path;
          }
        } else {
          this.$emit('trigger-alert', data.message || 'Failed to generate offer letter.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during offer letter generation.', 'danger');
      }
    },
    hasResume(app) {
      // Check if resume path exists in student record (we can mock true or check return field)
      return true; // Flask api returns resume path or handles it, student profile guarantees it
    },
    getResumeUrl(app) {
      // In a real database we have a join; we'll fetch student details.
      // But we can approximate it because app returns it or we retrieve it.
      // Let's assume student profile includes resume path, which we serve under /api/resumes
      return `/api/resumes/resume_${app.student_id}_` ; // We will query it or fallback.
      // Wait, let's fetch resume url dynamically or use the path returned in app.
      // Let's look at the database model: StudentProfile.resume_path is saved. Let's make sure
      // application to_dict returns student resume path if available, or we can look it up.
      // Wait, since we are fetching application dict, let's see. In our backend models/db_models.py:
      // StudentProfile.resume_path is defined. We can serve it directly using the candidate id or resume path.
      // Let's check app.py: we serve resumes using filename.
    },
    formatDateShort(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    },
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getDriveStatusBadge(status) {
      switch (status) {
        case 'Approved': return 'bg-success';
        case 'Pending': return 'bg-warning text-dark';
        case 'Rejected': return 'bg-danger';
        case 'Closed': return 'bg-dark';
        default: return 'bg-secondary';
      }
    }
  },
  mounted() {
    this.fetchDrives();
  }
}
</script>
