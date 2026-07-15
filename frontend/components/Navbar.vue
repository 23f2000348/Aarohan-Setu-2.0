<template>
  <nav class="navbar navbar-expand-lg navbar-light sticky-top">
    <div class="container">
      <!-- Brand Logo -->
      <a class="navbar-brand d-flex align-items-center" href="#" @click.prevent="goToHome">
        <i class="fa-solid fa-graduation-cap me-2"></i>
        <span>Aarohan Setu 2.0</span>
      </a>

      <!-- Toggler for Mobile -->
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent" aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Links -->
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="currentUser">
          <!-- Role Indicator -->
          <li class="nav-item">
            <span class="nav-link disabled text-muted text-uppercase">
              <i class="fa-solid fa-user-shield me-1"></i> {{ currentUser.role }} Portal
            </span>
          </li>
        </ul>

        <div class="d-flex align-items-center" v-if="currentUser">
          <!-- Notifications Bell Dropdown -->
          <div class="dropdown me-3 position-relative">
            <button class="btn btn-outline-secondary position-relative p-2 rounded-circle d-flex align-items-center justify-content-center" type="button" id="notifDropdown" data-bs-toggle="dropdown" aria-expanded="false" style="width: 40px; height: 40px;">
              <i class="fa-regular fa-bell" style="font-size: 1.15rem;"></i>
              <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" v-if="unreadCount > 0" style="font-size: 0.65rem; padding: 0.25rem 0.45rem;">
                {{ unreadCount }}
              </span>
            </button>
            
            <ul class="dropdown-menu dropdown-menu-end shadow-lg py-0 border-0 overflow-hidden" aria-labelledby="notifDropdown" style="width: 320px; max-height: 380px; overflow-y: auto; right: 0; left: auto;">
              <li class="bg-primary text-white p-3 d-flex justify-content-between align-items-center">
                <span class="fw-bold"><i class="fa-regular fa-bell me-1"></i> Notifications</span>
                <span class="badge bg-white text-primary rounded-pill">{{ unreadCount }} New</span>
              </li>
              
              <li v-if="notifications.length === 0" class="p-4 text-center text-muted">
                <i class="fa-solid fa-bell-slash d-block fs-3 mb-2 opacity-50"></i>
                No notifications found
              </li>
              
              <template v-else>
                <li v-for="notif in notifications" :key="notif.id" :class="['dropdown-item', 'p-3', 'border-bottom', { 'bg-light': !notif.is_read }]" @click="handleNotifClick(notif)">
                  <div class="d-flex flex-column">
                    <!-- Notification content -->
                    <span v-if="isCsvExport(notif.message)">
                      <i class="fa-solid fa-file-csv text-success me-1"></i> 
                      {{ parseCsvMessage(notif.message) }}
                      <a :href="parseCsvUrl(notif.message)" target="_blank" class="d-block mt-1 fw-bold text-decoration-underline" @click.stop="handleNotifClick(notif)">
                        <i class="fa-solid fa-download me-1"></i> Download CSV File
                      </a>
                    </span>
                    <span v-else>
                      <i class="fa-solid fa-info-circle text-primary me-1"></i>
                      {{ notif.message }}
                    </span>
                    <!-- Time -->
                    <small class="text-muted mt-1" style="font-size: 0.75rem;">
                      <i class="fa-regular fa-clock me-1"></i> {{ formatTime(notif.created_at) }}
                    </small>
                  </div>
                </li>
              </template>
            </ul>
          </div>

          <!-- User Email & Logout -->
          <span class="me-3 text-muted fw-bold d-none d-md-inline" style="font-size: 0.95rem;">
            {{ currentUser.email }}
          </span>
          <button class="btn btn-outline-danger btn-sm" @click="$emit('logout')">
            <i class="fa-solid fa-right-from-bracket me-1"></i> Logout
          </button>
        </div>
        
        <div class="d-flex align-items-center ms-auto" v-else>
          <span class="text-muted fw-bold"><i class="fa-solid fa-lock me-1"></i> Secure Authentication</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  props: {
    currentUser: Object,
    notifications: Array
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(n => !n.is_read).length;
    }
  },
  methods: {
    goToHome() {
      if (this.currentUser) {
        this.$emit('change-view', this.currentUser.role);
      } else {
        this.$emit('change-view', 'home');
      }
    },
    isCsvExport(message) {
      return message.startsWith('CSV_EXPORT_READY|');
    },
    parseCsvMessage(message) {
      return message.split('|')[2];
    },
    parseCsvUrl(message) {
      return message.split('|')[1];
    },
    handleNotifClick(notif) {
      if (!notif.is_read) {
        this.$emit('mark-read', notif.id);
      }
    },
    formatTime(isoString) {
      const date = new Date(isoString);
      return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
}
</script>
