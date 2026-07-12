<template>
  <div>
    <!-- Hero Banner -->
    <div class="hero-banner mb-4">
      <h1 class="hero-title" style="font-size: 2.2rem; border-bottom: none; padding-bottom: 0; margin-bottom: 0.5rem;">Welcome back, {{ profile.name }}</h1>
      <p class="hero-subtitle mb-0 text-muted">Explore and apply for placement drives, track your application status, and manage your academic profile registry in one place.</p>
    </div>

    <div class="row">
    <div class="col-lg-4 mb-4">
      <!-- View Profile Card -->
      <div class="card shadow-sm mb-4" v-if="!editingProfile">
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-solid fa-id-card me-2 text-primary"></i>My Profile</h4>
        </div>
        <div class="card-body">
          <div class="text-center mb-3">
            <i class="fa-solid fa-circle-user text-primary" style="font-size: 5rem;"></i>
            <h4 class="mt-2 mb-0">{{ profile.name }}</h4>
            <span class="badge bg-secondary mt-1">Student</span>
          </div>
          
          <table class="table table-borderless m-0">
            <tbody>
              <tr>
                <td class="fw-bold text-muted" style="width: 40%;">Email:</td>
                <td>{{ profile.email }}</td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">Branch:</td>
                <td>{{ profile.branch }}</td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">CGPA:</td>
                <td class="fw-bold text-success">{{ profile.cgpa }} / 10.0</td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">Graduation:</td>
                <td>Class of {{ profile.graduation_year }}</td>
              </tr>
              <tr>
                <td class="fw-bold text-muted">Resume:</td>
                <td>
                  <a :href="profile.resume_path" target="_blank" v-if="profile.resume_path" class="fw-bold text-primary">
                    <i class="fa-solid fa-file-pdf me-1"></i> View Resume
                  </a>
                  <span class="text-danger fw-bold" v-else>
                    <i class="fa-solid fa-triangle-exclamation me-1"></i> Not Uploaded
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div class="mt-4 d-grid gap-2">
            <button class="btn btn-outline-primary" @click="startEditProfile">
              <i class="fa-regular fa-pen-to-square me-1"></i> Edit Profile Details
            </button>
          </div>
        </div>
      </div>
      
      <!-- Edit Profile Card -->
      <div class="card shadow-sm mb-4" v-else>
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-regular fa-pen-to-square me-2 text-primary"></i>Edit Profile</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveProfile">
            <div class="mb-3">
              <label for="edit-name" class="form-label">Full Name</label>
              <input type="text" id="edit-name" class="form-control" v-model="editData.name" required>
            </div>
            
            <div class="mb-3">
              <label for="edit-branch" class="form-label">Branch / Department</label>
              <select id="edit-branch" class="form-select" v-model="editData.branch" required>
                <option value="Computer Science">Computer Science</option>
                <option value="Information Technology">Information Technology</option>
                <option value="Electronics & Communication">Electronics & Communication</option>
                <option value="Electrical Engineering">Electrical Engineering</option>
                <option value="Mechanical Engineering">Mechanical Engineering</option>
                <option value="Civil Engineering">Civil Engineering</option>
              </select>
            </div>
            
            <div class="row mb-3">
              <div class="col-6">
                <label for="edit-cgpa" class="form-label">CGPA</label>
                <input type="number" id="edit-cgpa" class="form-control" v-model="editData.cgpa" min="0.00" max="10.00" step="0.01" required>
              </div>
              <div class="col-6">
                <label for="edit-year" class="form-label">Grad Year</label>
                <input type="number" id="edit-year" class="form-control" v-model="editData.graduation_year" min="2020" max="2035" required>
              </div>
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
      
      <!-- Resume Upload Card -->
      <div class="card shadow-sm">
        <div class="card-header bg-white py-3">
          <h4 class="mb-0"><i class="fa-solid fa-cloud-arrow-up me-2 text-primary"></i>Upload Resume</h4>
        </div>
        <div class="card-body">
          <p class="text-muted small">Upload your latest resume (PDF, DOC, or DOCX formats allowed). You must have a resume uploaded to apply for drives.</p>
          
          <form @submit.prevent="handleResumeUpload" enctype="multipart/form-data">
            <div class="mb-3">
              <input type="file" ref="resumeFile" class="form-control" required @change="onFileSelected">
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="uploading">
              <span v-if="uploading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i class="fa-solid fa-cloud-arrow-up me-1" v-else></i> Upload File
            </button>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Main Board: Drives and Applications -->
    <div class="col-lg-8">
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-white p-0">
          <ul class="nav nav-tabs nav-fill border-0">
            <li class="nav-item">
              <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'drives' }]" @click="activeTab = 'drives'">
                <i class="fa-solid fa-briefcase me-1"></i> Available Drives
              </button>
            </li>
            <li class="nav-item">
              <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'applications' }]" @click="activeTab = 'applications'">
                <i class="fa-solid fa-clock-rotate-left me-1"></i> My History ({{ myApplications.length }})
              </button>
            </li>
          </ul>
        </div>
        
        <div class="card-body p-4">
          <!-- TABS CONTENT: PLACEMENT DRIVES -->
          <div v-if="activeTab === 'drives'">
            <!-- Search & Filters -->
            <div class="row g-3 mb-4 align-items-center">
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text"><i class="fa-solid fa-magnifying-glass text-muted"></i></span>
                  <input type="text" class="form-control" placeholder="Search by job title or company..." v-model="searchQuery" @input="fetchDrives">
                </div>
              </div>
              <div class="col-md-6 text-md-end">
                <div class="form-check form-switch d-inline-block">
                  <input class="form-check-input" type="checkbox" role="switch" id="eligibleCheck" v-model="eligibleOnly" @change="fetchDrives">
                  <label class="form-check-label fw-bold text-primary" for="eligibleCheck">Show Eligible Only</label>
                </div>
              </div>
            </div>
            
            <!-- Loading Indicator -->
            <div v-if="loadingDrives" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="mt-2 text-muted">Scanning placement registry...</p>
            </div>
            
            <!-- Empty state -->
            <div v-else-if="drives.length === 0" class="text-center py-5">
              <i class="fa-solid fa-folder-open fs-1 text-muted opacity-50 mb-3"></i>
              <h5>No placement drives found</h5>
              <p class="text-muted small">Try adjusting your search criteria or toggling the eligibility filter.</p>
            </div>
            
            <!-- Drives Registry List -->
            <div v-else>
              <div v-for="drive in drives" :key="drive.id" class="card border shadow-sm p-4 mb-3 position-relative">
                <!-- Eligibility Header Banner -->
                <div class="position-absolute top-0 end-0 m-3">
                  <span class="badge bg-success" v-if="drive.is_eligible"><i class="fa-solid fa-circle-check me-1"></i> Eligible</span>
                  <span class="badge bg-danger" v-else><i class="fa-solid fa-circle-xmark me-1"></i> Ineligible</span>
                </div>

                <div class="pe-5">
                  <h4 class="mb-1">{{ drive.job_title }}</h4>
                  <h5 class="text-muted mb-2"><i class="fa-solid fa-building me-1"></i> {{ drive.company_name }}</h5>
                </div>
                
                <p class="card-text mt-3 text-secondary" style="white-space: pre-line;">{{ drive.job_description }}</p>
                
                <!-- Eligibility criteria details -->
                <div class="row g-2 bg-light p-3 rounded border my-3">
                  <div class="col-sm-4 text-center border-end">
                    <span class="d-block small text-muted text-uppercase">Branch Required</span>
                    <strong class="text-primary">{{ drive.branch_eligibility }}</strong>
                  </div>
                  <div class="col-sm-4 text-center border-end">
                    <span class="d-block small text-muted text-uppercase">Min CGPA</span>
                    <strong class="text-primary">{{ drive.cgpa_eligibility }}</strong>
                  </div>
                  <div class="col-sm-4 text-center">
                    <span class="d-block small text-muted text-uppercase">Graduation Batch</span>
                    <strong class="text-primary">Class of {{ drive.year_eligibility }}</strong>
                  </div>
                </div>

                <div class="d-flex justify-content-between align-items-center mt-3">
                  <span class="text-danger fw-bold small">
                    <i class="fa-regular fa-clock me-1"></i> Apply Before: {{ formatDate(drive.deadline) }}
                  </span>
                  
                  <!-- Action Buttons -->
                  <div v-if="drive.has_applied">
                    <button class="btn btn-secondary btn-sm" disabled>
                      <i class="fa-solid fa-circle-check me-1"></i> Already Applied
                    </button>
                  </div>
                  <div v-else-if="!drive.is_eligible">
                    <button class="btn btn-outline-danger btn-sm" @click="showIneligibilityReason(drive)">
                      <i class="fa-solid fa-ban me-1"></i> Criteria Mismatch
                    </button>
                  </div>
                  <div v-else-if="!profile.resume_path">
                    <button class="btn btn-outline-warning btn-sm" disabled>
                      <i class="fa-solid fa-triangle-exclamation me-1"></i> Upload Resume to Apply
                    </button>
                  </div>
                  <div v-else>
                    <button class="btn btn-primary btn-sm" @click="applyForDrive(drive.id)" :disabled="applyingId === drive.id">
                      <span v-if="applyingId === drive.id" class="spinner-border spinner-border-sm me-2" role="status"></span>
                      <i class="fa-solid fa-paper-plane me-1" v-else></i> Submit Application
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- TABS CONTENT: HISTORY & APPLICATIONS -->
          <div v-else>
            <!-- Export CSV and Control Header -->
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h4 class="mb-0"><i class="fa-solid fa-clock-rotate-left text-primary me-2"></i>Application Log</h4>
              <button class="btn btn-outline-success btn-sm fw-bold" @click="exportCSV" :disabled="exporting">
                <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i class="fa-solid fa-file-csv me-1" v-else></i> Export Log as CSV
              </button>
            </div>
            
            <!-- Loading Indicator -->
            <div v-if="loadingHistory" class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="mt-2 text-muted">Retrieving placement record...</p>
            </div>
            
            <!-- Empty state -->
            <div v-else-if="myApplications.length === 0" class="text-center py-5">
              <i class="fa-regular fa-clipboard fs-1 text-muted opacity-50 mb-3"></i>
              <h5>No submitted applications</h5>
              <p class="text-muted small">Your applied placement drives will display here.</p>
            </div>
            
            <!-- History Table -->
            <div class="table-responsive" v-else>
              <table class="table table-hover align-middle border">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Job Title</th>
                    <th>Date Applied</th>
                    <th>Status</th>
                    <th class="text-center">Action / Offers</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in myApplications" :key="app.id">
                    <td class="fw-bold">{{ app.company_name }}</td>
                    <td>{{ app.drive_title }}</td>
                    <td>{{ formatDateShort(app.applied_at) }}</td>
                    <td>
                      <span :class="['badge', getStatusBadgeClass(app.status)]">{{ app.status }}</span>
                    </td>
                    <td class="text-center">
                      <!-- Display Interview schedules -->
                      <div v-if="app.interview_scheduled_at && app.status === 'Shortlisted'" class="mb-1">
                        <small class="d-block text-warning fw-bold">
                          <i class="fa-solid fa-calendar-check me-1"></i> Interview: {{ formatTime(app.interview_scheduled_at) }}
                        </small>
                      </div>
                      
                      <!-- Display Offer Letters -->
                      <div v-if="app.offer_letter_path">
                        <a :href="app.offer_letter_path" target="_blank" class="btn btn-success btn-xs py-1 px-2 fw-bold text-white text-decoration-none" style="font-size: 0.8rem;">
                          <i class="fa-solid fa-file-signature me-1"></i> Download Offer
                        </a>
                      </div>
                      <span class="text-muted small" v-else-if="app.status === 'Selected'"><i class="fa-solid fa-spinner fa-spin me-1"></i> Awaiting Offer</span>
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
      activeTab: 'drives', // 'drives', 'applications'
      profile: { ...this.userProfile },
      drives: [],
      myApplications: [],
      searchQuery: '',
      eligibleOnly: false,
      
      // Loadings
      loadingDrives: false,
      loadingHistory: false,
      saving: false,
      uploading: false,
      exporting: false,
      applyingId: null,
      
      // Editing
      editingProfile: false,
      editData: {
        name: '',
        branch: '',
        cgpa: '',
        graduation_year: ''
      },
      selectedFile: null
    };
  },
  methods: {
    startEditProfile() {
      this.editData = {
        name: this.profile.name,
        branch: this.profile.branch,
        cgpa: this.profile.cgpa,
        graduation_year: this.profile.graduation_year
      };
      this.editingProfile = true;
    },
    cancelEditProfile() {
      this.editingProfile = false;
    },
    async saveProfile() {
      this.saving = true;
      try {
        const res = await fetch('/api/student/profile', {
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
          this.fetchDrives(); // Re-fetch drives to update eligibility indicators
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
    onFileSelected(event) {
      this.selectedFile = event.target.files[0];
    },
    async handleResumeUpload() {
      const fileInput = this.$refs.resumeFile;
      if (!this.selectedFile) {
        this.$emit('trigger-alert', 'Please select a file to upload.', 'warning');
        return;
      }
      
      this.uploading = true;
      const formData = new FormData();
      formData.append('resume', this.selectedFile);
      
      try {
        const res = await fetch('/api/student/resume', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        
        if (res.ok) {
          this.profile.resume_path = data.resume_path;
          this.$emit('trigger-alert', 'Resume uploaded successfully!', 'success');
          this.$emit('update-profile');
          fileInput.value = ''; // Clear file input
          this.selectedFile = null;
        } else {
          this.$emit('trigger-alert', data.message || 'Resume upload failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during resume upload.', 'danger');
      } finally {
        this.uploading = false;
      }
    },
    async fetchDrives() {
      this.loadingDrives = true;
      try {
        const q = encodeURIComponent(this.searchQuery);
        const res = await fetch(`/api/student/drives?eligible_only=${this.eligibleOnly}&q=${q}`);
        if (res.ok) {
          this.drives = await res.json();
        }
      } catch (err) {
        console.error("Error fetching drives:", err);
      } finally {
        this.loadingDrives = false;
      }
    },
    async fetchHistory() {
      this.loadingHistory = true;
      try {
        const res = await fetch('/api/student/applications');
        if (res.ok) {
          this.myApplications = await res.json();
        }
      } catch (err) {
        console.error("Error fetching history:", err);
      } finally {
        this.loadingHistory = false;
      }
    },
    async applyForDrive(driveId) {
      this.applyingId = driveId;
      try {
        const res = await fetch(`/api/student/drives/${driveId}/apply`, {
          method: 'POST'
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', 'Application submitted successfully!', 'success');
          this.fetchDrives();
          this.fetchHistory();
        } else {
          this.$emit('trigger-alert', data.message || 'Application failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during application.', 'danger');
      } finally {
        this.applyingId = null;
      }
    },
    async exportCSV() {
      this.exporting = true;
      try {
        const res = await fetch('/api/student/applications/export', {
          method: 'POST'
        });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
        } else {
          this.$emit('trigger-alert', data.message || 'Export failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during export.', 'danger');
      } finally {
        this.exporting = false;
      }
    },
    showIneligibilityReason(drive) {
      let reasons = [];
      if (this.profile.cgpa < drive.cgpa_eligibility) {
        reasons.push(`CGPA is below required ${drive.cgpa_eligibility} (Current: ${this.profile.cgpa})`);
      }
      if (this.profile.graduation_year !== drive.year_eligibility) {
        reasons.push(`Graduation year class mismatch (Drive: ${drive.year_eligibility}, Profile: ${this.profile.graduation_year})`);
      }
      const branchList = drive.branch_eligibility.split(',').map(b => b.trim().toLowerCase());
      const branchOk = drive.branch_eligibility.toLowerCase() === 'all' || branchList.includes('all') || branchList.includes(this.profile.branch.toLowerCase());
      
      if (!branchOk) {
        reasons.push(`Branch mismatch (Eligible: ${drive.branch_eligibility}, Profile: ${this.profile.branch})`);
      }
      
      this.$emit('trigger-alert', `Eligibility Mismatch Details:<br>- ${reasons.join('<br>- ')}`, 'warning');
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
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
    getStatusBadgeClass(status) {
      switch (status) {
        case 'Applied': return 'bg-primary';
        case 'Shortlisted': return 'bg-warning text-dark';
        case 'Selected': return 'bg-success';
        case 'Rejected': return 'bg-danger';
        default: return 'bg-secondary';
      }
    }
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'drives') {
        this.fetchDrives();
      } else {
        this.fetchHistory();
      }
    }
  },
  mounted() {
    this.fetchDrives();
    this.fetchHistory();
  }
}
</script>
