<template>
  <main class="container-fluid p-4">
    <div class="row">
      <div class="col-lg-8">
        <div class="card mb-4">
          <div class="card-body">
            <h2 class="mb-4">Travel Document Requirements</h2>
            <form @submit.prevent="generateDocuments">
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="origin" class="form-label">From (Origin Country)</label>
                  <input
                    type="text"
                    class="form-control"
                    id="origin"
                    v-model="form.origin"
                    required
                    placeholder="e.g. Kenya"
                  />
                </div>
                <div class="col-md-6">
                  <label for="destination" class="form-label">To (Destination Country)</label>
                  <input
                    type="text"
                    class="form-control"
                    id="destination"
                    v-model="form.destination"
                    required
                    placeholder="e.g. Ireland"
                  />
                </div>
                <div class="col-12">
                  <button type="submit" class="btn btn-primary" :disabled="isGenerating">
                    <span v-if="isGenerating">
                      <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                      Generating...
                    </span>
                    <span v-else> <i class="fas fa-file-alt me-2"></i> Generate Documents </span>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <div v-if="result" class="card">
          <div class="card-body">
            <h3 class="mb-3">Document Requirements</h3>

            <div class="mb-4">
              <h4 class="h5 text-primary"><i class="fas fa-passport me-2"></i> Visa Documents</h4>
              <ul class="list-group list-group-flush">
                <li v-for="(doc, index) in result.visa_documents" :key="'visa-' + index" class="list-group-item">
                  {{ doc }}
                </li>
              </ul>
            </div>

            <div class="mb-4">
              <h4 class="h5 text-primary"><i class="fas fa-id-card me-2"></i> Passport Requirements</h4>
              <ul class="list-group list-group-flush">
                <li
                  v-for="(req, index) in result.passport_requirements"
                  :key="'passport-' + index"
                  class="list-group-item"
                >
                  {{ req }}
                </li>
              </ul>
            </div>

            <div class="mb-4">
              <h4 class="h5 text-primary"><i class="fas fa-file-alt me-2"></i> Additional Documents</h4>
              <ul class="list-group list-group-flush">
                <li
                  v-for="(doc, index) in result.additional_documents"
                  :key="'additional-' + index"
                  class="list-group-item"
                >
                  {{ doc }}
                </li>
              </ul>
            </div>

            <div>
              <h4 class="h5 text-primary"><i class="fas fa-exclamation-triangle me-2"></i> Travel Advisories</h4>
              <ul class="list-group list-group-flush">
                <li v-for="(adv, index) in result.advisories" :key="'advisory-' + index" class="list-group-item">
                  {{ adv }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card mb-4">
          <div class="card-body">
            <h3 class="mb-3">Recent Queries</h3>
            <ul class="list-group list-group-flush">
              <li
                v-for="(query, index) in recentQueries"
                :key="'query-' + index"
                class="list-group-item d-flex justify-content-between align-items-center"
                @click="loadQuery(query)"
                style="cursor: pointer"
              >
                <span>
                  {{ query.origin }} → {{ query.destination }}
                  <small class="d-block text-muted">{{ formatDate(query.created_at) }}</small>
                </span>
                <button class="btn btn-sm btn-outline-primary">
                  <i class="fas fa-redo"></i>
                </button>
              </li>
            </ul>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <h3 class="mb-3">Quick Actions</h3>
            <button class="btn btn-outline-secondary w-100 mb-2">
              <i class="fas fa-file-pdf me-2"></i> Export as PDF
            </button>
            <button class="btn btn-outline-secondary w-100 mb-2">
              <i class="fas fa-envelope me-2"></i> Email Results
            </button>
            <button class="btn btn-outline-secondary w-100"><i class="fas fa-save me-2"></i> Save as Template</button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import api from '../services/api'

export default {
  name: 'DashboardView',
  data() {
    return {
      form: {
        origin: '',
        destination: '',
      },
      isGenerating: false,
      result: null,
      recentQueries: [],
      error: null,
    }
  },
  methods: {
    async generateDocuments() {
      this.isGenerating = true
      this.error = null

      try {
        const response = await api.generateDocuments({
          origin: this.form.origin,
          destination: this.form.destination,
        })
        this.result = response.data

        // Refresh recent queries
        await this.loadRecentQueries()
      } catch (error) {
        console.error('Error generating documents:', error)
        this.error = this.getErrorMessage(error)
      } finally {
        this.isGenerating = false
      }
    },

    async loadQuery(query) {
      try {
        const response = await api.getQueryDetails(query.id)
        this.form.origin = response.data.origin_country
        this.form.destination = response.data.destination_country
        this.result = {
          visa_documents: response.data.visa_documents,
          passport_requirements: response.data.passport_requirements,
          additional_documents: response.data.additional_documents,
          advisories: response.data.travel_advisories,
        }
      } catch (error) {
        console.error('Error loading query:', error)
        this.error = this.getErrorMessage(error)
      }
    },

    async loadRecentQueries() {
      try {
        const response = await api.getRecentQueries()
        this.recentQueries = response.data.map((query) => ({
          id: query.id,
          origin: query.origin_country,
          destination: query.destination_country,
          created_at: query.queried_at,
          result: {
            visa_documents: query.visa_documents,
            passport_requirements: query.passport_requirements,
            additional_documents: query.additional_documents,
            advisories: query.travel_advisories,
          },
        }))
      } catch (error) {
        console.error('Error loading recent queries:', error)
      }
    },

    getErrorMessage(error) {
      if (error.response) {
        return error.response.data.detail || 'An error occurred'
      }
      return error.message || 'An unknown error occurred'
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
  },
  async mounted() {
    await this.loadRecentQueries()
  },
}
</script>
