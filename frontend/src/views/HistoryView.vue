<template>
  <div>
    <h2 class="mb-4">Document Generation History</h2>
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
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewDetails(item.id)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-secondary">
                    <i class="fas fa-download"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="history.length === 0">
                <td colspan="6" class="text-center p-5 text-muted">No history found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'HistoryView',
  data() {
    return {
      history: [],
      isLoading: false,
      error: null,
    }
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    viewDetails(id) {
      this.$router.push(`/history/${id}`)
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
          document_format: 'JSON', // Or you can add format to your model
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
  },
  async mounted() {
    await this.fetchHistory()
  },
}
</script>
