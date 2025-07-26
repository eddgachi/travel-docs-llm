import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
})

// Request interceptor for adding auth token if needed
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle different HTTP status codes
      const { status } = error.response
      if (status === 401) {
        // Handle unauthorized
      } else if (status === 404) {
        // Handle not found
      } else if (status >= 500) {
        // Handle server errors
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Document Generation
  generateDocuments(payload) {
    return api.post('/ask', payload)
  },

  // History
  getHistory(skip = 0, limit = 100) {
    return api.get('/history', { params: { skip, limit } })
  },

  // Recent queries for dashboard
  getRecentQueries(limit = 5) {
    return api.get('/recent-queries', { params: { limit } })
  },

  // Query details
  getQueryDetails(queryId) {
    return api.get(`/query/${queryId}`)
  },

  // Settings
  getSettings() {
    return api.get('/settings')
  },
  createSetting(payload) {
    return api.post('/settings', payload)
  },
  updateSetting(configKey, payload) {
    return api.put(`/settings/${configKey}`, payload)
  },
}
