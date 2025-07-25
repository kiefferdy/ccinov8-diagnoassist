// Central API service for backend communication
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Generic request handler
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Patient API methods
  async getPatients() {
    return this.request('/api/v1/patients/');
  }

  async getPatient(id) {
    return this.request(`/api/v1/patients/${id}`);
  }

  async createPatient(patientData) {
    return this.request('/api/v1/patients/', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  async updatePatient(id, patientData) {
    return this.request(`/api/v1/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(patientData),
    });
  }

  async deletePatient(id) {
    return this.request(`/api/v1/patients/${id}`, {
      method: 'DELETE',
    });
  }

  // Episode API methods
  async getEpisodes() {
    return this.request('/api/v1/episodes/');
  }

  async getEpisode(id) {
    return this.request(`/api/v1/episodes/${id}`);
  }

  async getPatientEpisodes(patientId) {
    return this.request(`/api/v1/episodes/?patient_id=${patientId}`);
  }

  async createEpisode(episodeData) {
    return this.request('/api/v1/episodes/', {
      method: 'POST',
      body: JSON.stringify(episodeData),
    });
  }

  async updateEpisode(id, episodeData) {
    return this.request(`/api/v1/episodes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(episodeData),
    });
  }

  async deleteEpisode(id) {
    return this.request(`/api/v1/episodes/${id}`, {
      method: 'DELETE',
    });
  }

  async completeEpisode(id) {
    return this.request(`/api/v1/episodes/${id}/complete`, {
      method: 'PATCH',
    });
  }

  // Treatment API methods
  async getTreatments() {
    return this.request('/api/v1/treatments/');
  }

  async getTreatment(id) {
    return this.request(`/api/v1/treatments/${id}`);
  }

  async createTreatment(treatmentData) {
    return this.request('/api/v1/treatments/', {
      method: 'POST',
      body: JSON.stringify(treatmentData),
    });
  }

  async updateTreatment(id, treatmentData) {
    return this.request(`/api/v1/treatments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(treatmentData),
    });
  }

  async deleteTreatment(id) {
    return this.request(`/api/v1/treatments/${id}`, {
      method: 'DELETE',
    });
  }

  async startTreatment(id) {
    return this.request(`/api/v1/treatments/${id}/start`, {
      method: 'PATCH',
    });
  }

  async completeTreatment(id) {
    return this.request(`/api/v1/treatments/${id}/complete`, {
      method: 'PATCH',
    });
  }

  // Diagnosis API methods
  async getDiagnoses() {
    return this.request('/api/v1/diagnoses/');
  }

  async getDiagnosis(id) {
    return this.request(`/api/v1/diagnoses/${id}`);
  }

  async createDiagnosis(diagnosisData) {
    return this.request('/api/v1/diagnoses/', {
      method: 'POST',
      body: JSON.stringify(diagnosisData),
    });
  }

  async updateDiagnosis(id, diagnosisData) {
    return this.request(`/api/v1/diagnoses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(diagnosisData),
    });
  }

  async deleteDiagnosis(id) {
    return this.request(`/api/v1/diagnoses/${id}`, {
      method: 'DELETE',
    });
  }

  async analyzeSymptoms(symptomsData) {
    return this.request('/api/v1/diagnoses/analyze-symptoms', {
      method: 'POST',
      body: JSON.stringify(symptomsData),
    });
  }

  async confirmDiagnosis(id) {
    return this.request(`/api/v1/diagnoses/${id}/confirm`, {
      method: 'PATCH',
    });
  }

  // FHIR API methods
  async getFhirResources() {
    return this.request('/api/v1/fhir/');
  }

  async getFhirResource(id) {
    return this.request(`/api/v1/fhir/${id}`);
  }

  async createFhirResource(fhirData) {
    return this.request('/api/v1/fhir/', {
      method: 'POST',
      body: JSON.stringify(fhirData),
    });
  }

  async updateFhirResource(id, fhirData) {
    return this.request(`/api/v1/fhir/${id}`, {
      method: 'PUT',
      body: JSON.stringify(fhirData),
    });
  }

  async deleteFhirResource(id) {
    return this.request(`/api/v1/fhir/${id}`, {
      method: 'DELETE',
    });
  }

  async getFhirMetadata() {
    return this.request('/api/v1/fhir/metadata');
  }

  // Health check methods
  async checkHealth() {
    return this.request('/health');
  }

  async getApiStatus() {
    return this.request('/api/status');
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;