<template>
  <div>
    <!-- Hero Section -->
    <div class="row align-items-center py-5 my-3 position-relative overflow-hidden" style="border-radius: var(--radius-lg); background: linear-gradient(135deg, #f0e6d6 0%, #fcf6eb 50%, #eef3fa 100%); border: 1px solid var(--border-color); padding: 3.5rem;">
      <div class="col-lg-7 pe-lg-5 mb-4 mb-lg-0">
        <span class="badge bg-warning mb-3" style="font-size: 0.8rem; padding: 0.5rem 1rem;">Official Placement Portal</span>
        <h1 class="display-4 fw-800 text-primary mb-3" style="font-family: 'Outfit', sans-serif; font-weight: 800; letter-spacing: -0.04em; line-height: 1.15;">
          Bridging Talent <br>With <span class="text-accent" style="color: var(--accent-color) !important;">Opportunities</span>
        </h1>
        <p class="lead text-secondary mb-4" style="font-size: 1.15rem; line-height: 1.7;">
          Aarohan Setu 2.0 is the official campus placement channel, connecting outstanding academic minds with global technology leaders and elite enterprises. Accelerate your career search with streamlined profile registries and real-time drive application logs.
        </p>
        <div class="d-flex gap-3">
          <button class="btn btn-primary btn-lg" @click="$emit('change-view', 'auth')">
            <i class="fa-solid fa-right-to-bracket me-2"></i> Enter Portal
          </button>
          <a href="#features-section" class="btn btn-outline-secondary btn-lg">
            Learn More <i class="fa-solid fa-chevron-down ms-1" style="font-size: 0.8rem;"></i>
          </a>
        </div>
      </div>
      <div class="col-lg-5 text-center position-relative">
        <!-- Interactive Illustrative Graphic Container -->
        <div class="p-4" style="background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px); border-radius: var(--radius-lg); border: 1px solid rgba(255, 255, 255, 0.6); box-shadow: var(--shadow-lg);">
          <div class="py-5">
            <i class="fa-solid fa-graduation-cap text-accent mb-4" style="font-size: 6rem; filter: drop-shadow(0 10px 15px rgba(202, 138, 4, 0.3));"></i>
            <h3 class="fw-bold text-primary mb-1">Aarohan Setu 2.0</h3>
            <p class="text-muted small mb-0">PLACEMENT PORTAL & REGISTRY PLATFORM</p>
          </div>
          <div class="row g-2 text-start mt-3">
            <div class="col-6">
              <div class="p-3 bg-white rounded border d-flex align-items-center">
                <i class="fa-solid fa-user-graduate text-success me-2 fs-4"></i>
                <div>
                  <span class="d-block small text-muted">Placed Rate</span>
                  <strong class="text-primary">95.4%</strong>
                </div>
              </div>
            </div>
            <div class="col-6">
              <div class="p-3 bg-white rounded border d-flex align-items-center">
                <i class="fa-solid fa-building text-info me-2 fs-4"></i>
                <div>
                  <span class="d-block small text-muted">Partners</span>
                  <strong class="text-primary">150+</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Counter Bar -->
    <div class="row g-3 mb-5 mt-4">
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-4 h-100 text-center">
          <div class="stat-val text-primary" style="font-size: 2.5rem;">95.4%</div>
          <div class="stat-lbl">Overall Placement Ratio</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-4 h-100 text-center" style="border-left-color: var(--accent-color) !important;">
          <div class="stat-val text-primary" style="font-size: 2.5rem;">150+</div>
          <div class="stat-lbl">Premium Recruitment Partners</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-4 h-100 text-center" style="border-left-color: #0f766e !important;">
          <div class="stat-val text-primary" style="font-size: 2.5rem;">42 LPA</div>
          <div class="stat-lbl">Highest Package Offered</div>
        </div>
      </div>
      <div class="col-sm-6 col-md-3">
        <div class="card stat-card shadow-sm p-4 h-100 text-center" style="border-left-color: #b91c1c !important;">
          <div class="stat-val text-primary" style="font-size: 2.5rem;">2026</div>
          <div class="stat-lbl">Active Graduating Batch</div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div id="features-section" class="py-4 mb-5">
      <div class="text-center mb-5">
        <span class="text-uppercase text-accent fw-bold small tracking-wide">Explore Features</span>
        <h2 class="display-6 fw-bold mt-1 text-primary">Consolidated Workspace For Every Stakeholder</h2>
        <p class="text-muted mx-auto" style="max-width: 600px;">Streamlined, functional design customized to cater to students, corporate recruiters, and placement directors.</p>
      </div>

      <div class="row g-4">
        <!-- Feature 1: Student -->
        <div class="col-md-4">
          <div class="card border p-4 h-100 shadow-sm transition-hover">
            <div class="mb-3">
              <span class="p-3 rounded-circle d-inline-flex align-items-center justify-content-center" style="background-color: var(--accent-light); width: 60px; height: 60px;">
                <i class="fa-solid fa-user-graduate text-accent fs-3"></i>
              </span>
            </div>
            <h3 class="fw-bold text-primary mb-3">For Students</h3>
            <ul class="list-unstyled text-secondary small" style="line-height: 2;">
              <li><i class="fa-solid fa-check text-success me-2"></i> Register and upload professional resumes.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Instant real-time eligibility check.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> One-click drive applications.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Notifications of scheduled interviews.</li>
            </ul>
          </div>
        </div>

        <!-- Feature 2: Corporate -->
        <div class="col-md-4">
          <div class="card border p-4 h-100 shadow-sm transition-hover">
            <div class="mb-3">
              <span class="p-3 rounded-circle d-inline-flex align-items-center justify-content-center" style="background-color: rgba(15, 118, 110, 0.1); width: 60px; height: 60px;">
                <i class="fa-solid fa-building text-success fs-3" style="color: #0f766e !important;"></i>
              </span>
            </div>
            <h3 class="fw-bold text-primary mb-3">For Corporate HRs</h3>
            <ul class="list-unstyled text-secondary small" style="line-height: 2;">
              <li><i class="fa-solid fa-check text-success me-2"></i> Request recruiter account approvals.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Launch custom job placement drives.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Shortlist and schedule interviews.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Autogenerate signed verification offers.</li>
            </ul>
          </div>
        </div>

        <!-- Feature 3: Admin -->
        <div class="col-md-4">
          <div class="card border p-4 h-100 shadow-sm transition-hover">
            <div class="mb-3">
              <span class="p-3 rounded-circle d-inline-flex align-items-center justify-content-center" style="background-color: rgba(15, 23, 42, 0.08); width: 60px; height: 60px;">
                <i class="fa-solid fa-user-shield text-primary fs-3"></i>
              </span>
            </div>
            <h3 class="fw-bold text-primary mb-3">For Portal Admins</h3>
            <ul class="list-unstyled text-secondary small" style="line-height: 2;">
              <li><i class="fa-solid fa-check text-success me-2"></i> Approve company registries.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Authorize active placement drives.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Control student blacklisting.</li>
              <li><i class="fa-solid fa-check text-success me-2"></i> Real-time placement analytics dashboards.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Corporate Partner Carousel Grid -->
    <div class="py-4 border-top">
      <h5 class="text-center text-muted text-uppercase mb-4" style="font-size: 0.8rem; letter-spacing: 0.1em;">OUR ELITE PLACEMENT RECRUITERS</h5>
      <div class="row g-2 justify-content-center">
        <div class="col-4 col-md-2" v-for="comp in companies" :key="comp">
          <div class="p-3 bg-white rounded border text-center font-monospace text-muted shadow-xs text-uppercase" style="font-size: 0.85rem; font-weight: 700; border-color: rgba(226, 218, 206, 0.4) !important;">
            <i class="fa-solid fa-briefcase me-1 text-accent opacity-50"></i> {{ comp }}
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
      companies: ['Acme Corp', 'TechCorp', 'Excel Corp', 'CloudServices', 'CyberSecurity', 'AppDynamix']
    };
  }
}
</script>
