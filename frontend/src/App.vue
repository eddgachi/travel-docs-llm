<template>
  <div
    :class="['app-wrapper', { 'sidebar-open': isSidebarOpen }, theme === 'dark' ? 'bg-dark text-light' : 'bg-light']"
  >
    <aside
      :class="[
        'sidebar',
        theme === 'dark' ? 'bg-black' : 'bg-white',
        'shadow-lg border-end',
        theme === 'dark' ? 'border-secondary' : 'border-light-subtle',
      ]"
    >
      <div class="p-3 d-flex justify-content-between align-items-center border-bottom border-light-subtle">
        <h2 class="h6 mb-0 fw-semibold">Navigation</h2>
        <button
          class="btn btn-sm btn-close d-lg-none"
          @click="isSidebarOpen = false"
          :aria-label="'Close sidebar' + (theme === 'dark' ? '' : 'close-white')"
        ></button>
      </div>
      <div class="p-3 sidebar-nav">
        <ul class="list-unstyled">
          <li>
            <router-link to="/" class="nav-link" :class="theme === 'dark' ? 'text-light' : 'text-dark'"
              ><i class="fas fa-fw fa-home me-2"></i>Document Generator</router-link
            >
          </li>
          <li>
            <router-link to="/history" class="nav-link" :class="theme === 'dark' ? 'text-light' : 'text-dark'"
              ><i class="fas fa-fw fa-history me-2"></i>History</router-link
            >
          </li>
          <li>
            <router-link to="/settings" class="nav-link" :class="theme === 'dark' ? 'text-light' : 'text-dark'"
              ><i class="fas fa-fw fa-cog me-2"></i>Settings</router-link
            >
          </li>
        </ul>
      </div>
    </aside>
    <div v-if="isSidebarOpen" class="sidebar-backdrop d-lg-none" @click="isSidebarOpen = false"></div>

    <div class="main-content">
      <header :class="['shadow-sm sticky-top z-index-sticky', theme === 'dark' ? 'bg-black' : 'bg-white']">
        <div class="container-fluid px-4 py-2">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-sm d-lg-none" @click="isSidebarOpen = !isSidebarOpen" aria-label="Toggle sidebar">
                <i :class="['fas fa-bars', theme === 'dark' ? 'text-light' : 'text-dark']"></i>
              </button>
              <h1 class="h6 mb-0 fw-semibold d-none d-md-inline" :class="theme === 'dark' ? 'text-light' : 'text-dark'">
                <i class="fas fa-passport me-2 text-primary opacity-75"></i> Travel Documents Advisor
              </h1>
              <span class="badge bg-success-subtle text-success-emphasis border border-success-subtle fw-medium">
                <i class="fas fa-check-circle me-1"></i> Connected
              </span>
            </div>
            <div class="flex-grow-1 mx-3 d-none d-lg-block" style="max-width: 400px"></div>
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-sm" @click="toggleTheme" :class="theme === 'dark' ? 'text-warning' : 'text-dark'">
                <i :class="['fas', theme === 'dark' ? 'fa-sun' : 'fa-moon']"></i>
              </button>
              <!-- Add notification bell if needed -->
              <!-- <button class="btn btn-sm position-relative">
                <i class="fas fa-bell"></i>
                <span v-if="unreadNotifications" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                  {{ unreadNotifications }}
                </span>
              </button> -->
            </div>
          </div>
        </div>
      </header>

      <main class="container-fluid p-4">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <footer
        :class="[
          'mt-auto py-3 text-center small text-muted border-top',
          theme === 'dark' ? 'bg-black border-secondary' : 'bg-light border-light-subtle',
        ]"
      >
        © {{ new Date().getFullYear() }} Travel Documents Advisor | Version 1.0.0 |
        <a href="#">Privacy Policy</a>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      theme: 'light',
      isSidebarOpen: false,
      // unreadNotifications: 0, // Uncomment if adding notifications
    }
  },
  methods: {
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      document.body.setAttribute('data-bs-theme', this.theme)
      localStorage.setItem('dashboardTheme', this.theme)
    },
  },
  watch: {
    $route() {
      this.isSidebarOpen = false
    },
  },
  mounted() {
    const savedTheme = localStorage.getItem('dashboardTheme')
    if (savedTheme) {
      this.theme = savedTheme
      document.body.setAttribute('data-bs-theme', this.theme)
    } else {
      document.body.setAttribute('data-bs-theme', this.theme)
    }
  },
}
</script>

<style>
/* --- Global App Styles --- */
html,
body {
  height: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-wrapper {
  display: flex;
  min-height: 100vh;
}

/* --- Sidebar Styles --- */
.sidebar {
  width: 260px;
  position: fixed;
  top: 0;
  left: -260px;
  height: 100vh;
  transition: left 0.3s ease-in-out;
  z-index: 1050;
  overflow-y: auto;
}

.sidebar.open {
  left: 0;
}

.sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}

.sidebar-nav .nav-link {
  padding: 0.5rem 0.8rem;
  margin-bottom: 0.1rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  transition: background-color 0.2s ease, color 0.2s ease;
  display: flex;
  align-items: center;
}

/* Active link styling */
.sidebar-nav .nav-link.router-link-exact-active {
  background-color: var(--bs-primary-bg-subtle);
  color: var(--bs-primary-text-emphasis) !important;
  font-weight: 500;
}
[data-bs-theme='dark'] .sidebar-nav .nav-link.router-link-exact-active {
  background-color: var(--bs-primary);
  color: var(--bs-light) !important;
}

.sidebar-nav .nav-link:hover {
  background-color: var(--bs-secondary-bg);
}
[data-bs-theme='dark'] .sidebar-nav .nav-link:hover {
  background-color: var(--bs-dark-bg-subtle);
}

/* --- Main Content Area --- */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease-in-out;
}

@media (min-width: 992px) {
  .sidebar {
    left: 0;
    z-index: 1000;
  }
  .main-content {
    margin-left: 260px;
  }
  .app-wrapper.sidebar-collapsed .sidebar {
    left: -260px;
  }
  .app-wrapper.sidebar-collapsed .main-content {
    margin-left: 0;
  }
}

/* --- Router Transition --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* --- Helper Styles --- */
.z-index-sticky {
  z-index: 1020;
}

/* Minor adjustments */
body {
  overflow-x: hidden;
}
</style>
