<template>
  <div>
    <!-- Hero Banner -->
    <div class="hero-banner mb-4">
      <h1 class="hero-title" style="font-size: 2.2rem; border-bottom: none; padding-bottom: 0; margin-bottom: 0.5rem;">Portal Administration</h1>
      <p class="hero-subtitle mb-0 text-muted">Monitor placement metrics, approve registered companies, review drive applications, and manage the student directory database.</p>
    </div>

    <!-- STATS ROW -->
    <div class="row g-3 mb-4">
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-3 h-100">
          <div class="stat-val">{{ stats.total_students }}</div>
          <div class="stat-lbl">Total Students</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-3 h-100" style="border-left-color: #2b6cb0 !important;">
          <div class="stat-val">{{ stats.total_companies }}</div>
          <div class="stat-lbl">Registered Companies</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-3 h-100" style="border-left-color: #2e7d32 !important;">
          <div class="stat-val">{{ stats.total_drives }}</div>
          <div class="stat-lbl">Placement Drives</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-3 h-100" style="border-left-color: #f57c00 !important;">
          <div class="stat-val">{{ stats.placement_rate }}%</div>
          <div class="stat-lbl">Student Placement Rate</div>
        </div>
      </div>
    </div>

    <!-- ANALYTICS CHARTS ROW -->
    <div class="row mb-4">
      <div class="col-md-8 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0"><i class="fa-solid fa-chart-column me-2"></i>Branch-wise Placement Statistics</h5>
          </div>
          <div class="card-body">
            <canvas id="branchChart" style="max-height: 250px;"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0"><i class="fa-solid fa-chart-pie me-2"></i>Drive Status Distribution</h5>
          </div>
          <div class="card-body">
            <canvas id="statusChart" style="max-height: 250px;"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- SEARCH & SEARCH RESULTS -->
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0"><i class="fa-solid fa-magnifying-glass me-2"></i>Unified Entity Search</h5>
      </div>
      <div class="card-body">
        <div class="input-group mb-3">
          <span class="input-group-text"><i class="fa-solid fa-magnifying-glass text-muted"></i></span>
          <input type="text" class="form-control" placeholder="Search students or companies by name or email..." v-model="searchQuery" @input="performSearch">
        </div>
        
        <div v-if="searching" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          <span class="ms-2 text-muted">Searching database...</span>
        </div>
        
        <div v-else-if="searchQuery && searchResults.students.length === 0 && searchResults.companies.length === 0" class="text-center py-2 text-muted">
          No matches found for "{{ searchQuery }}"
        </div>
        
        <!-- Search Results Grid -->
        <div class="row" v-else-if="searchResults.students.length > 0 || searchResults.companies.length > 0">
          <!-- Student Matches -->
          <div class="col-md-6" v-if="searchResults.students.length > 0">
            <h6 class="fw-bold border-bottom pb-2 mb-2"><i class="fa-solid fa-user-graduate me-1 text-primary"></i>Student Matches</h6>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between align-items-center" v-for="s in searchResults.students" :key="s.id">
                <div>
                  <strong>{{ s.name }}</strong> ({{ s.branch }})
                  <div class="small text-muted">{{ s.email }} | CGPA: {{ s.cgpa }}</div>
                </div>
                <div>
                  <button :class="['btn', 'btn-xs', s.is_blacklisted ? 'btn-danger' : 'btn-outline-danger']" @click="blacklistStudent(s.id)">
                    {{ s.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                  </button>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- Company Matches -->
          <div class="col-md-6" v-if="searchResults.companies.length > 0">
            <h6 class="fw-bold border-bottom pb-2 mb-2"><i class="fa-solid fa-building me-1 text-primary"></i>Company Matches</h6>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between align-items-center" v-for="c in searchResults.companies" :key="c.id">
                <div>
                  <strong>{{ c.name }}</strong>
                  <div class="small text-muted">{{ c.email }} | HR: {{ c.hr_contact }}</div>
                </div>
                <div>
                  <button :class="['btn', 'btn-xs', c.is_blacklisted ? 'btn-danger' : 'btn-outline-danger']" @click="blacklistCompany(c.id)">
                    {{ c.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- MAIN ADMIN TABS -->
    <div class="card shadow-sm">
      <div class="card-header bg-white p-0">
        <ul class="nav nav-tabs nav-fill border-0">
          <li class="nav-item">
            <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'companies' }]" @click="activeTab = 'companies'">
              <i class="fa-solid fa-building me-1"></i> Company Registrations
            </button>
          </li>
          <li class="nav-item">
            <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'drives' }]" @click="activeTab = 'drives'">
              <i class="fa-solid fa-briefcase me-1"></i> Drive Approvals
            </button>
          </li>
          <li class="nav-item">
            <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'students' }]" @click="activeTab = 'students'">
              <i class="fa-solid fa-user-graduate me-1"></i> Student Directory
            </button>
          </li>
        </ul>
      </div>
      
      <div class="card-body p-4">
        <!-- COMPANIES APPROVAL REGISTER -->
        <div v-if="activeTab === 'companies'">
          <div v-if="companies.length === 0" class="text-center py-4 text-muted">
            No registered companies found
          </div>
          <div class="table-responsive" v-else>
            <table class="table table-hover align-middle border">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Contact Info</th>
                  <th>Website</th>
                  <th class="text-center">Approval Status</th>
                  <th class="text-center">System Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="comp in companies" :key="comp.id">
                  <td class="fw-bold">{{ comp.name }}</td>
                  <td>
                    <span class="d-block small">HR: {{ comp.hr_contact }}</span>
                    <span class="d-block small text-muted">{{ comp.email }}</span>
                  </td>
                  <td>
                    <a :href="comp.website" target="_blank" v-if="comp.website">{{ comp.website }}</a>
                    <span class="text-muted" v-else>-</span>
                  </td>
                  <td class="text-center">
                    <span class="badge bg-success" v-if="comp.is_approved">Approved</span>
                    <span class="badge bg-warning text-dark" v-else>Pending</span>
                  </td>
                  <td class="text-center">
                    <div class="d-flex justify-content-center gap-2">
                      <button class="btn btn-success btn-xs" v-if="!comp.is_approved" @click="approveCompany(comp.id)">
                        <i class="fa-solid fa-check"></i> Approve
                      </button>
                      <button class="btn btn-danger btn-xs" v-if="!comp.is_approved" @click="rejectCompany(comp.id)">
                        <i class="fa-solid fa-xmark"></i> Reject
                      </button>
                      
                      <!-- Blacklist / Active controls if approved -->
                      <template v-if="comp.is_approved">
                        <button :class="['btn', 'btn-xs', comp.is_blacklisted ? 'btn-success' : 'btn-danger']" @click="blacklistCompany(comp.id)">
                          <i class="fa-solid fa-ban me-1"></i> {{ comp.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                        </button>
                        <button :class="['btn', 'btn-xs', comp.is_active_account === false ? 'btn-outline-success' : 'btn-outline-secondary']" @click="toggleCompanyActive(comp.id)">
                          {{ comp.is_active_account === false ? 'Reactivate' : 'Deactivate' }}
                        </button>
                      </template>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- PLACEMENT DRIVE APPROVALS -->
        <div v-if="activeTab === 'drives'">
          <div v-if="drives.length === 0" class="text-center py-4 text-muted">
            No placement drives listed
          </div>
          <div class="table-responsive" v-else>
            <table class="table table-hover align-middle border">
              <thead>
                <tr>
                  <th>Job details</th>
                  <th>Eligibilities</th>
                  <th>Deadline</th>
                  <th class="text-center">State</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in drives" :key="drive.id">
                  <td>
                    <strong class="d-block">{{ drive.job_title }}</strong>
                    <small class="text-muted">{{ drive.company_name }}</small>
                  </td>
                  <td>
                    <div class="small">Branch: {{ drive.branch_eligibility }}</div>
                    <div class="small">Min CGPA: {{ drive.cgpa_eligibility }}</div>
                  </td>
                  <td>{{ formatDateShort(drive.deadline) }}</td>
                  <td class="text-center">
                    <span :class="['badge', getDriveStatusBadge(drive.status)]">{{ drive.status }}</span>
                  </td>
                  <td class="text-center">
                    <div class="d-flex justify-content-center gap-2">
                      <button class="btn btn-success btn-xs" v-if="drive.status === 'Pending'" @click="approveDrive(drive.id)">
                        <i class="fa-solid fa-check"></i> Approve
                      </button>
                      <button class="btn btn-danger btn-xs" v-if="drive.status === 'Pending'" @click="rejectDrive(drive.id)">
                        <i class="fa-solid fa-xmark"></i> Reject
                      </button>
                      <button class="btn btn-dark btn-xs" v-if="drive.status === 'Approved'" @click="closeDrive(drive.id)">
                        <i class="fa-solid fa-lock"></i> Close Drive
                      </button>
                      <span class="text-muted small" v-if="drive.status === 'Closed' || drive.status === 'Rejected'">No action</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- STUDENT DIRECTORY -->
        <div v-if="activeTab === 'students'">
          <div v-if="students.length === 0" class="text-center py-4 text-muted">
            No students registered in portal
          </div>
          <div class="table-responsive" v-else>
            <table class="table table-hover align-middle border">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Academic Info</th>
                  <th class="text-center">Blacklist Status</th>
                  <th class="text-center">Account Control</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stud in students" :key="stud.id">
                  <td class="fw-bold">
                    {{ stud.name }}
                    <small class="d-block text-muted">{{ stud.email }}</small>
                  </td>
                  <td>
                    <span class="d-block small">Branch: {{ stud.branch }}</span>
                    <span class="d-block small fw-bold text-success">CGPA: {{ stud.cgpa }} | Class: {{ stud.graduation_year }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge bg-danger" v-if="stud.is_blacklisted">Blacklisted</span>
                    <span class="badge bg-success" v-else>Good Standing</span>
                  </td>
                  <td class="text-center">
                    <div class="d-flex justify-content-center gap-2">
                      <button :class="['btn', 'btn-xs', stud.is_blacklisted ? 'btn-success' : 'btn-danger']" @click="blacklistStudent(stud.id)">
                        <i class="fa-solid fa-ban me-1"></i> {{ stud.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                      </button>
                      <button :class="['btn', 'btn-xs', stud.is_active_account === false ? 'btn-outline-success' : 'btn-outline-secondary']" @click="toggleStudentActive(stud.id)">
                        {{ stud.is_active_account === false ? 'Reactivate' : 'Deactivate' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeTab: 'companies', // 'companies', 'drives', 'students'
      stats: {
        total_students: 0,
        total_companies: 0,
        total_drives: 0,
        total_applications: 0,
        placement_rate: 0,
        branch_distribution: [],
        drive_statuses: {}
      },
      companies: [],
      drives: [],
      students: [],
      
      // Search
      searchQuery: '',
      searching: false,
      searchResults: {
        students: [],
        companies: []
      },
      
      // Chart instances
      branchChart: null,
      statusChart: null
    };
  },
  methods: {
    async fetchStats() {
      try {
        const res = await fetch('/api/admin/stats');
        if (res.ok) {
          this.stats = await res.json();
          this.initCharts();
        }
      } catch (err) {
        console.error("Error fetching stats:", err);
      }
    },
    async fetchCompanies() {
      try {
        const res = await fetch('/api/admin/companies');
        if (res.ok) {
          const comps = await res.json();
          // We will fetch users to check if active/deactivated
          // For simplicity, we can enhance model details or fetch users list
          // Let's toggle states dynamically in the backend and return detailed models.
          this.companies = comps;
        }
      } catch (err) {
        console.error(err);
      }
    },
    async fetchDrives() {
      try {
        const res = await fetch('/api/admin/drives');
        if (res.ok) {
          this.drives = await res.json();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async fetchStudents() {
      try {
        const res = await fetch('/api/admin/students');
        if (res.ok) {
          this.students = await res.json();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async approveCompany(compId) {
      try {
        const res = await fetch(`/api/admin/companies/${compId}/approve`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchCompanies();
          this.fetchStats();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async rejectCompany(compId) {
      if (!confirm("Are you sure you want to reject this company registration? This will delete their profile.")) return;
      try {
        const res = await fetch(`/api/admin/companies/${compId}/reject`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchCompanies();
          this.fetchStats();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async blacklistCompany(compId) {
      try {
        const res = await fetch(`/api/admin/companies/${compId}/blacklist`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchCompanies();
          this.performSearch(); // Refresh search if running
        }
      } catch (err) {
        console.error(err);
      }
    },
    async toggleCompanyActive(compId) {
      try {
        const res = await fetch(`/api/admin/companies/${compId}/toggle-status`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          // Update local state
          const comp = this.companies.find(c => c.id === compId);
          if (comp) comp.is_active_account = data.is_active;
          this.fetchCompanies();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async blacklistStudent(studId) {
      try {
        const res = await fetch(`/api/admin/students/${studId}/blacklist`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchStudents();
          this.performSearch(); // Refresh search if running
        }
      } catch (err) {
        console.error(err);
      }
    },
    async toggleStudentActive(studId) {
      try {
        const res = await fetch(`/api/admin/students/${studId}/toggle-status`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchStudents();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async approveDrive(driveId) {
      try {
        const res = await fetch(`/api/admin/drives/${driveId}/approve`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchDrives();
          this.fetchStats();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async rejectDrive(driveId) {
      try {
        const res = await fetch(`/api/admin/drives/${driveId}/reject`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchDrives();
          this.fetchStats();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async closeDrive(driveId) {
      try {
        const res = await fetch(`/api/admin/drives/${driveId}/close`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
          this.$emit('trigger-alert', data.message, 'success');
          this.fetchDrives();
          this.fetchStats();
        }
      } catch (err) {
        console.error(err);
      }
    },
    async performSearch() {
      const query = this.searchQuery.trim();
      if (!query) {
        this.searchResults = { students: [], companies: [] };
        return;
      }
      this.searching = true;
      try {
        const res = await fetch(`/api/admin/search?q=${encodeURIComponent(query)}`);
        if (res.ok) {
          this.searchResults = await res.json();
        }
      } catch (err) {
        console.error(err);
      } finally {
        this.searching = false;
      }
    },
    initCharts() {
      // Wait for DOM to load canvas
      this.$nextTick(() => {
        const branchCtx = document.getElementById('branchChart');
        const statusCtx = document.getElementById('statusChart');
        
        if (!branchCtx || !statusCtx) return;
        
        // 1. Branch Chart (Bar Chart)
        if (this.branchChart) this.branchChart.destroy();
        
        const branchLabels = this.stats.branch_distribution.map(d => d.branch);
        const branchStudents = this.stats.branch_distribution.map(d => d.students);
        const branchSelected = this.stats.branch_distribution.map(d => d.selected);
        
        this.branchChart = new Chart(branchCtx, {
          type: 'bar',
          data: {
            labels: branchLabels,
            datasets: [
              {
                label: 'Total Registered Students',
                data: branchStudents,
                backgroundColor: 'rgba(74, 85, 104, 0.4)',
                borderColor: '#4a5568',
                borderWidth: 1
              },
              {
                label: 'Selected/Placed Students',
                data: branchSelected,
                backgroundColor: 'rgba(26, 54, 93, 0.8)',
                borderColor: '#1a365d',
                borderWidth: 1
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: { stepSize: 1, font: { family: 'Calibri' } }
              },
              x: {
                ticks: { font: { family: 'Calibri' } }
              }
            },
            plugins: {
              legend: { labels: { font: { family: 'Calibri' } } }
            }
          }
        });
        
        // 2. Drive Status Chart (Doughnut Chart)
        if (this.statusChart) this.statusChart.destroy();
        
        const statusLabels = Object.keys(this.stats.drive_statuses);
        const statusData = Object.values(this.stats.drive_statuses);
        
        this.statusChart = new Chart(statusCtx, {
          type: 'doughnut',
          data: {
            labels: statusLabels,
            datasets: [{
              data: statusData,
              backgroundColor: [
                '#f57c00', // Pending - Orange
                '#2e7d32', // Approved - Green
                '#c62828', // Rejected - Red
                '#4a5568'  // Closed - Slate
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: { font: { family: 'Calibri' } }
              }
            }
          }
        });
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
  watch: {
    activeTab(newTab) {
      if (newTab === 'companies') this.fetchCompanies();
      else if (newTab === 'drives') this.fetchDrives();
      else if (newTab === 'students') this.fetchStudents();
    }
  },
  mounted() {
    this.fetchStats();
    this.fetchCompanies();
  }
}
</script>
