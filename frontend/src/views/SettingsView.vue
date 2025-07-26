<template>
  <div>
    <!-- Notification Alert -->
    <div v-if="showNotification" class="notification-alert" :class="notificationClass">
      {{ notificationMessage }}
      <button type="button" class="btn-close" @click="showNotification = false"></button>
    </div>

    <h2 class="mb-4">LLM Settings</h2>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger mb-4">
      <i class="fas fa-exclamation-circle me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchSettings">Retry</button>
    </div>

    <!-- Settings Form -->
    <div v-else>
      <div class="card">
        <div class="card-body">
          <form @submit.prevent="saveSettings">
            <div class="row g-3">
              <!-- API Key -->
              <div class="col-md-12">
                <label for="google_api_key" class="form-label">Google API Key</label>
                <input
                  type="password"
                  class="form-control"
                  id="google_api_key"
                  v-model="settings.google_api_key"
                  placeholder="Enter your Google API key"
                />
                <small class="text-muted">Required for Gemini API access</small>
              </div>

              <!-- LLM Model -->
              <div class="col-md-6">
                <label for="llm_model" class="form-label">LLM Model</label>
                <select class="form-select" id="llm_model" v-model="settings.llm_model">
                  <option value="gemini-1.5-flash-latest">Gemini 1.5 Flash</option>
                  <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro</option>
                  <option value="gemini-1.0-pro-latest">Gemini 1.0 Pro</option>
                </select>
              </div>

              <!-- Temperature -->
              <div class="col-md-6">
                <label for="llm_temperature" class="form-label">Temperature</label>
                <input
                  type="number"
                  class="form-control"
                  id="llm_temperature"
                  v-model.number="settings.llm_temperature"
                  min="0"
                  max="1"
                  step="0.1"
                />
                <small class="text-muted">Controls randomness (0-1)</small>
              </div>

              <!-- Max Tokens -->
              <div class="col-md-6">
                <label for="llm_max_tokens" class="form-label">Max Tokens</label>
                <input
                  type="number"
                  class="form-control"
                  id="llm_max_tokens"
                  v-model.number="settings.llm_max_tokens"
                  min="1"
                  max="8192"
                />
              </div>

              <!-- Response Language -->
              <div class="col-md-6">
                <label for="default_response_language" class="form-label">Response Language</label>
                <input
                  type="text"
                  class="form-control"
                  id="default_response_language"
                  v-model="settings.default_response_language"
                  placeholder="e.g., English"
                />
              </div>

              <!-- Enable History -->
              <div class="col-md-6">
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="enable_history"
                    v-model="settings.enable_history"
                    true-value="true"
                    false-value="false"
                  />
                  <label class="form-check-label" for="enable_history">Enable Query History</label>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-4">
              <button type="submit" class="btn btn-primary" :disabled="isSaving">
                <template v-if="isSaving">
                  <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Saving...
                </template>
                <template v-else> <i class="fas fa-save me-2"></i> Save Settings </template>
              </button>

              <button type="button" class="btn btn-outline-secondary" @click="testConnection" :disabled="isTesting">
                <template v-if="isTesting">
                  <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Testing...
                </template>
                <template v-else> <i class="fas fa-plug me-2"></i> Test Connection </template>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'SettingsView',
  data() {
    return {
      settings: {
        google_api_key: '',
        llm_model: 'gemini-1.5-flash-latest',
        llm_temperature: 0.3,
        llm_max_tokens: 1024,
        default_response_language: 'English',
        enable_history: 'true',
      },
      isLoading: false,
      isSaving: false,
      isTesting: false,
      error: null,
      showNotification: false,
      notificationMessage: '',
      notificationClass: 'alert-success',
    }
  },
  methods: {
    showNotificationMessage(message, type = 'success') {
      this.notificationMessage = message
      this.notificationClass = `alert-${type}`
      this.showNotification = true
      setTimeout(() => {
        this.showNotification = false
      }, 3000)
    },

    async fetchSettings() {
      this.isLoading = true
      this.error = null

      try {
        const response = await api.getSettings()
        const loadedSettings = response.data.reduce((acc, curr) => {
          acc[curr.config_key] = curr.config_value
          return acc
        }, {})

        this.settings = {
          ...this.settings,
          ...loadedSettings,
        }
      } catch (error) {
        console.error('Error fetching settings:', error)
        this.error = this.getErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async saveSettings() {
      this.isSaving = true
      this.error = null

      try {
        const settingsArray = Object.entries(this.settings).map(([key, value]) => ({
          config_key: key,
          config_value: value.toString(),
        }))

        await Promise.all(settingsArray.map((setting) => api.updateSetting(setting.config_key, setting)))

        this.showNotificationMessage('Settings saved successfully!')
      } catch (error) {
        console.error('Error saving settings:', error)
        this.error = this.getErrorMessage(error)
        this.showNotificationMessage('Failed to save settings', 'danger')
      } finally {
        this.isSaving = false
      }
    },

    async testConnection() {
      this.isTesting = true
      this.error = null

      try {
        const response = await api.testConnection()
        this.showNotificationMessage(`Connection successful! Model: ${response.data.model}`)
      } catch (error) {
        console.error('Error testing connection:', error)
        this.error = this.getErrorMessage(error)
        this.showNotificationMessage('Connection test failed', 'danger')
      } finally {
        this.isTesting = false
      }
    },

    getErrorMessage(error) {
      if (error.response) {
        return error.response.data.detail || 'An error occurred'
      }
      return error.message || 'An unknown error occurred'
    },
  },
  async mounted() {
    await this.fetchSettings()
  },
}
</script>

<style scoped>
.notification-alert {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  padding: 1rem 1.5rem;
  border-radius: 0.25rem;
  animation: slideIn 0.3s ease-out;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.notification-alert .btn-close {
  margin-left: 1rem;
}

@keyframes slideIn {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.form-switch .form-check-input {
  width: 2.5em;
  height: 1.5em;
}
</style>
