import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import HistoryView from '../views/HistoryView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'Dashboard' }, // Add titles for browser tab
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { title: 'Sync History' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { title: 'Settings' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Or createWebHashHistory
  routes,
  linkActiveClass: 'active', // Add Bootstrap's 'active' class to active router links
})

// Update browser tab title
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} | Travel Docs LLM+` : 'Travel Docs LLM+ Dashboard'
  next()
})

export default router
