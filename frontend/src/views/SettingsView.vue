<template>
  <div>
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
            <!-- Form fields (same as before) -->

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

// Update frontend/src/views/SettingsView.vue

<script>
import api from '../services/api'

export default {
  name: 'SettingsView',
  data() {
    return {
      settings: {},
      isLoading: false,
      isSaving: false,
      isTesting: false,
      error: null,
    }
  },
  methods: {
    async fetchSettings() {
      this.isLoading = true
      this.error = null

      try {
        const response = await api.getSettings()
        // Transform array of settings to object
        this.settings = response.data.reduce((acc, curr) => {
          acc[curr.config_key] = curr.config_value
          return acc
        }, {})
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
        // Convert settings object to array of key-value pairs
        const settingsArray = Object.entries(this.settings).map(([key, value]) => ({
          config_key: key,
          config_value: value,
        }))

        // Update each setting
        await Promise.all(settingsArray.map((setting) => api.updateSetting(setting.config_key, setting)))

        this.$toast.success('Settings saved successfully!', {
          position: 'top-right',
          duration: 3000,
        })
      } catch (error) {
        console.error('Error saving settings:', error)
        this.error = this.getErrorMessage(error)
      } finally {
        this.isSaving = false
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
