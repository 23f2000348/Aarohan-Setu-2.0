const options = {
    moduleCache: {
        vue: Vue
    },
    async getFile(url) {
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`Failed to load component: ${url} (Status: ${res.status})`);
        }
        return {
            getContentData: (asBinary) => asBinary ? res.arrayBuffer() : res.text()
        };
    },
    addStyle(textContent) {
        const style = document.createElement('style');
        style.textContent = textContent;
        const ref = document.head.getElementsByTagName('style')[0] || null;
        document.head.insertBefore(style, ref);
    },
    log(type, ...args) {
        console[type](...args);
    }
};

const { loadModule } = window['vue3-sfc-loader'];

// Creating Vue App
const app = Vue.createApp({
    data() {
        return {
            currentUser: null,
            userProfile: null,
            notifications: [],
            currentView: 'home',
            alertMessage: '',
            alertType: 'alert-info',
            notifInterval: null
        };
    },
    computed: {
        currentViewComponent() {
            switch (this.currentView) {
                case 'home':
                    return 'home-page';
                case 'auth':
                    return 'auth-page';
                case 'student':
                    return 'student-dashboard';
                case 'company':
                    return 'company-dashboard';
                case 'admin':
                    return 'admin-dashboard';
                default:
                    return 'home-page';
            }
        }
    },
    methods: {
        triggerAlert(message, type = 'info') {
            this.alertMessage = message;
            this.alertType = `alert-${type}`;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },
        clearAlert() {
            this.alertMessage = '';
        },
        changeView(view) {
            this.currentView = view;
            this.clearAlert();
        },
        async fetchCurrentUser() {
            try {
                const res = await fetch('/api/user');
                const data = await res.json();
                if (data.authenticated) {
                    this.currentUser = data.user;
                    this.userProfile = data.profile;
                    this.currentView = data.user.role;
                    
                    this.startNotificationsPolling();
                } else {
                    this.currentUser = null;
                    this.userProfile = null;
                    this.currentView = 'home';
                    this.stopNotificationsPolling();
                }
            } catch (err) {
                console.error("Error fetching current user:", err);
            }
        },
        async handleLoginSuccess(user, profile) {
            this.currentUser = user;
            this.userProfile = profile;
            this.currentView = user.role;
            this.triggerAlert(`Welcome back, ${profile ? profile.name : 'Administrator'}!`, 'success');
            
            this.startNotificationsPolling();
        },
        async handleLogout() {
            try {
                const res = await fetch('/api/logout', { method: 'POST' });
                if (res.ok) {
                    this.currentUser = null;
                    this.userProfile = null;
                    this.notifications = [];
                    this.currentView = 'home';
                    this.stopNotificationsPolling();
                    this.triggerAlert('You have logged out successfully.', 'success');
                }
            } catch (err) {
                console.error("Error during logout:", err);
            }
        },
        async fetchNotifications() {
            if (!this.currentUser) return;
            try {
                const res = await fetch('/api/notifications');
                if (res.ok) {
                    this.notifications = await res.json();
                }
            } catch (err) {
                console.error("Error fetching notifications:", err);
            }
        },
        async markNotificationRead(notifId) {
            try {
                const res = await fetch(`/api/notifications/${notifId}/read`, { method: 'POST' });
                if (res.ok) {
                    const notif = this.notifications.find(n => n.id === notifId);
                    if (notif) notif.is_read = true;
                }
            } catch (err) {
                console.error("Error marking notification read:", err);
            }
        },
        startNotificationsPolling() {
            this.fetchNotifications();
            this.stopNotificationsPolling();
            this.notifInterval = setInterval(() => {
                this.fetchNotifications();
            }, 10000);
        },
        stopNotificationsPolling() {
            if (this.notifInterval) {
                clearInterval(this.notifInterval);
                this.notifInterval = null;
            }
        }
    },
    mounted() {
        this.fetchCurrentUser();
    },
    beforeUnmount() {
        this.stopNotificationsPolling();
    }
});


app.component('navigation-bar', Vue.defineAsyncComponent(() => loadModule('/components/Navbar.vue', options)));
app.component('home-page', Vue.defineAsyncComponent(() => loadModule('/components/Home.vue', options)));
app.component('auth-page', Vue.defineAsyncComponent(() => loadModule('/components/Auth.vue', options)));
app.component('student-dashboard', Vue.defineAsyncComponent(() => loadModule('/components/StudentDashboard.vue', options)));
app.component('company-dashboard', Vue.defineAsyncComponent(() => loadModule('/components/CompanyDashboard.vue', options)));
app.component('admin-dashboard', Vue.defineAsyncComponent(() => loadModule('/components/AdminDashboard.vue', options)));

app.mount('#app');
