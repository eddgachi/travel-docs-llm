<template>
  <div>
    <h2 class="mb-4">Document Generation History</h2>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger mb-4">
      <i class="fas fa-exclamation-circle me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchHistory">Retry</button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>Date</th>
                <th>From</th>
                <th>To</th>
                <th>Documents</th>
                <th>Format</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in history" :key="item.id">
                <td>{{ formatDate(item.generated_at) }}</td>
                <td>{{ item.origin }}</td>
                <td>{{ item.destination }}</td>
                <td>
                  <span class="badge bg-primary-subtle text-primary-emphasis">
                    {{ item.visa_documents.length }} Visa
                  </span>
                  <span class="badge bg-info-subtle text-info-emphasis ms-1">
                    {{ item.passport_requirements.length }} Passport
                  </span>
                </td>
                <td>{{ item.document_format }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="openModal(item)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-secondary">
                    <i class="fas fa-download"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="history.length === 0 && !isLoading">
                <td colspan="6" class="text-center p-5 text-muted">No history found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Document Details: {{ currentItem.origin }} → {{ currentItem.destination }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="currentItem">
              <div class="mb-4">
                <p class="text-muted mb-2">Generated on: {{ formatDate(currentItem.generated_at) }}</p>
              </div>

              <div class="mb-4">
                <h4 class="h5 text-primary"><i class="fas fa-passport me-2"></i> Visa Documents</h4>
                <ul class="list-group list-group-flush">
                  <li v-for="(doc, index) in currentItem.visa_documents" :key="'visa-' + index" class="list-group-item">
                    {{ doc }}
                  </li>
                </ul>
              </div>

              <div class="mb-4">
                <h4 class="h5 text-primary"><i class="fas fa-id-card me-2"></i> Passport Requirements</h4>
                <ul class="list-group list-group-flush">
                  <li
                    v-for="(req, index) in currentItem.passport_requirements"
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
                    v-for="(doc, index) in currentItem.additional_documents"
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
                  <li
                    v-for="(adv, index) in currentItem.travel_advisories"
                    :key="'advisory-' + index"
                    class="list-group-item"
                  >
                    {{ adv }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="downloadAsJson">
              <i class="fas fa-download me-2"></i> Download as JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap'
import api from '../services/api'

export default {
  name: 'HistoryView',
  data() {
    return {
      history: [],
      isLoading: false,
      error: null,
      currentItem: {
        origin: '',
        destination: '',
        generated_at: '',
        visa_documents: [],
        passport_requirements: [],
        additional_documents: [],
        travel_advisories: [],
      },
      detailsModal: null,
    }
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    openModal(item) {
      this.currentItem = item
      if (!this.detailsModal) {
        this.detailsModal = new Modal(document.getElementById('detailsModal'))
      }
      this.detailsModal.show()
    },
    async fetchHistory() {
      this.isLoading = true
      this.error = null

      try {
        const response = await api.getHistory()
        this.history = response.data.map((item) => ({
          id: item.id,
          origin: item.origin_country,
          destination: item.destination_country,
          generated_at: item.queried_at,
          visa_documents: item.visa_documents,
          passport_requirements: item.passport_requirements,
          additional_documents: item.additional_documents,
          travel_advisories: item.travel_advisories,
          document_format: 'JSON',
        }))
      } catch (error) {
        console.error('Error fetching history:', error)
        this.error = this.getErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },
    getErrorMessage(error) {
      if (error.response) {
        return error.response.data.detail || 'An error occurred'
      }
      return error.message || 'An unknown error occurred'
    },
    downloadAsJson() {
      if (!this.currentItem) return

      const data = {
        origin: this.currentItem.origin,
        destination: this.currentItem.destination,
        generated_at: this.currentItem.generated_at,
        visa_documents: this.currentItem.visa_documents,
        passport_requirements: this.currentItem.passport_requirements,
        additional_documents: this.currentItem.additional_documents,
        travel_advisories: this.currentItem.travel_advisories,
      }

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `travel-docs-${this.currentItem.origin}-to-${this.currentItem.destination}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    },
  },
  async mounted() {
    await this.fetchHistory()
  },
}
</script>

<style scoped>
.modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
.list-group-item {
  padding: 0.75rem 1.25rem;
}
</style>
