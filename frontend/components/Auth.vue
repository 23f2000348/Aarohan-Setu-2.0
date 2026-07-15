<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
      <div class="card shadow-lg border-1 mt-3">
        <!-- Card Tabs -->
        <div class="card-header p-0">
          <ul class="nav nav-tabs nav-fill border-0">
            <li class="nav-item">
              <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'login' }]" @click="setTab('login')">
                <i class="fa-solid fa-right-to-bracket me-1"></i> Log In
              </button>
            </li>
            <li class="nav-item">
              <button :class="['nav-link', 'py-3', 'rounded-0', 'border-0', { 'active fw-bold text-primary': activeTab === 'register' }]" @click="setTab('register')">
                <i class="fa-solid fa-user-plus me-1"></i> Register
              </button>
            </li>
          </ul>
        </div>
        
        <!-- Card Body -->
        <div class="card-body p-4">
          <!-- LOG IN FORM -->
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin">
            <h3 class="text-center mb-4">Portal Login</h3>
            
            <div class="mb-3">
              <label for="login-email" class="form-label">Email Address</label>
              <div class="input-group">
                <span class="input-group-text"><i class="fa-solid fa-envelope text-muted"></i></span>
                <input type="text" id="login-email" class="form-control" v-model="loginData.email" placeholder="name@domain.com">
              </div>
            </div>
            
            <div class="mb-4">
              <label for="login-password" class="form-label">Password</label>
              <div class="input-group">
                <span class="input-group-text"><i class="fa-solid fa-lock text-muted"></i></span>
                <input type="password" id="login-password" class="form-control" v-model="loginData.password" placeholder="••••••••">
              </div>
            </div>
            
            <button type="submit" class="btn btn-primary w-100 py-2 fs-5" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i class="fa-solid fa-right-to-bracket me-1" v-else></i> Authenticate
            </button>
          </form>
          
          <!-- REGISTER FORM -->
          <div v-else>
            <h3 class="text-center mb-3">Create Account</h3>
            
            <!-- Role Selection -->
            <div class="d-flex justify-content-center mb-4">
              <div class="btn-group w-100" role="group" aria-label="Role select">
                <input type="radio" class="btn-check" name="role-select" id="role-student" autocomplete="off" value="student" v-model="registerRole">
                <label class="btn btn-outline-primary" for="role-student">
                  <i class="fa-solid fa-user-graduate me-1"></i> Student
                </label>

                <input type="radio" class="btn-check" name="role-select" id="role-company" autocomplete="off" value="company" v-model="registerRole">
                <label class="btn btn-outline-primary" for="role-company">
                  <i class="fa-solid fa-building me-1"></i> Recruiter / Company
                </label>
              </div>
            </div>
            
            <!-- STUDENT REGISTER FORM -->
            <form v-if="registerRole === 'student'" @submit.prevent="handleStudentRegister">
              <div class="mb-3">
                <label for="stud-name" class="form-label">Full Name</label>
                <input type="text" id="stud-name" class="form-control" v-model="studentData.name" placeholder="John Doe">
              </div>

              <div class="mb-3">
                <label for="stud-email" class="form-label">Email Address</label>
                <input type="text" id="stud-email" class="form-control" v-model="studentData.email" placeholder="john.doe@university.edu">
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="stud-branch" class="form-label">Branch / Department</label>
                  <select id="stud-branch" class="form-select" v-model="studentData.branch">
                    <option value="" disabled>Select Branch</option>
                    <option value="Computer Science">Computer Science</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="Electronics & Communication">Electronics & Communication</option>
                    <option value="Electrical Engineering">Electrical Engineering</option>
                    <option value="Mechanical Engineering">Mechanical Engineering</option>
                    <option value="Civil Engineering">Civil Engineering</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label for="stud-year" class="form-label">Graduation Year</label>
                  <input type="text" id="stud-year" class="form-control" v-model="studentData.graduation_year" placeholder="2026">
                </div>
              </div>

              <div class="mb-3">
                <label for="stud-cgpa" class="form-label">Current CGPA</label>
                <input type="text" id="stud-cgpa" class="form-control" v-model="studentData.cgpa" placeholder="8.50">
              </div>

              <div class="row mb-4">
                <div class="col-md-6">
                  <label for="stud-pass" class="form-label">Password</label>
                  <input type="password" id="stud-pass" class="form-control" v-model="studentData.password" placeholder="••••••••">
                </div>
                <div class="col-md-6">
                  <label for="stud-confirm" class="form-label">Confirm Password</label>
                  <input type="password" id="stud-confirm" class="form-control" v-model="studentData.confirmPassword" placeholder="••••••••">
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i class="fa-solid fa-user-plus me-1" v-else></i> Register Student
              </button>
            </form>
            
            <!-- COMPANY REGISTER FORM -->
            <form v-else @submit.prevent="handleCompanyRegister">
              <div class="mb-3">
                <label for="comp-name" class="form-label">Company Name</label>
                <input type="text" id="comp-name" class="form-control" v-model="companyData.name" placeholder="Acme Corporation">
              </div>

              <div class="mb-3">
                <label for="comp-email" class="form-label">Corporate Email</label>
                <input type="text" id="comp-email" class="form-control" v-model="companyData.email" placeholder="hr@acme.com">
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="comp-contact" class="form-label">HR Contact Number</label>
                  <input type="text" id="comp-contact" class="form-control" v-model="companyData.hr_contact" placeholder="+91 9876543210">
                </div>
                <div class="col-md-6">
                  <label for="comp-web" class="form-label">Company Website</label>
                  <input type="text" id="comp-web" class="form-control" v-model="companyData.website" placeholder="https://acme.com">
                </div>
              </div>

              <div class="mb-3">
                <label for="comp-desc" class="form-label">Brief Description</label>
                <textarea id="comp-desc" class="form-control" rows="3" v-model="companyData.description" placeholder="Write about your company operations..."></textarea>
              </div>

              <div class="row mb-4">
                <div class="col-md-6">
                  <label for="comp-pass" class="form-label">Password</label>
                  <input type="password" id="comp-pass" class="form-control" v-model="companyData.password" placeholder="••••••••">
                </div>
                <div class="col-md-6">
                  <label for="comp-confirm" class="form-label">Confirm Password</label>
                  <input type="password" id="comp-confirm" class="form-control" v-model="companyData.confirmPassword" placeholder="••••••••">
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i class="fa-solid fa-user-plus me-1" v-else></i> Register Company
              </button>
            </form>
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
      activeTab: 'login',
      registerRole: 'student',
      loading: false,
      loginData: {
        email: '',
        password: ''
      },
      studentData: {
        email: '',
        password: '',
        confirmPassword: '',
        name: '',
        branch: '',
        cgpa: '',
        graduation_year: '2026'
      },
      companyData: {
        email: '',
        password: '',
        confirmPassword: '',
        name: '',
        hr_contact: '',
        website: '',
        description: ''
      }
    };
  },
  methods: {
    setTab(tab) {
      this.activeTab = tab;
      this.$emit('trigger-alert', '', 'info');
    },
    async handleLogin() {
      this.loading = true;
      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.loginData)
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('login-success', data.user, data.profile);
        } else {
          this.$emit('trigger-alert', data.message || 'Login failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during login.', 'danger');
      } finally {
        this.loading = false;
      }
    },
    async handleStudentRegister() {
      this.loading = true;
      try {
        const res = await fetch('/api/register/student', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.studentData)
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('login-success', data.user, data.profile);
        } else {
          this.$emit('trigger-alert', data.message || 'Registration failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during registration.', 'danger');
      } finally {
        this.loading = false;
      }
    },
    async handleCompanyRegister() {
      this.loading = true;
      try {
        const res = await fetch('/api/register/company', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.companyData)
        });
        const data = await res.json();
        
        if (res.ok) {
          this.$emit('trigger-alert', 'Company registration submitted successfully! Waiting for Admin approval.', 'success');
          this.setTab('login');
          this.loginData.email = this.companyData.email;
          this.loginData.password = '';
        } else {
          this.$emit('trigger-alert', data.message || 'Registration failed.', 'danger');
        }
      } catch (err) {
        console.error(err);
        this.$emit('trigger-alert', 'Network error during registration.', 'danger');
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
