/**
 * SQLite-like storage for extended patient fields that aren't in the main Supabase database
 * Stores: maritalStatus, occupation, emergencyContact details
 */

const STORAGE_KEY = 'patient_extensions';

class PatientExtensionsStorage {
  constructor() {
    this.data = this.loadData();
  }

  loadData() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error loading patient extensions:', error);
      return {};
    }
  }

  saveData() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
    } catch (error) {
      console.error('Error saving patient extensions:', error);
    }
  }

  // Store extended fields for a patient
  setPatientExtensions(patientId, extensions) {
    this.data[patientId] = {
      ...this.data[patientId],
      ...extensions,
      updatedAt: new Date().toISOString()
    };
    this.saveData();
  }

  // Get extended fields for a patient
  getPatientExtensions(patientId) {
    return this.data[patientId] || {};
  }

  // Update specific extension field
  updateField(patientId, field, value) {
    if (!this.data[patientId]) {
      this.data[patientId] = {};
    }
    this.data[patientId][field] = value;
    this.data[patientId].updatedAt = new Date().toISOString();
    this.saveData();
  }

  // Delete all extensions for a patient
  deletePatientExtensions(patientId) {
    delete this.data[patientId];
    this.saveData();
  }

  // Merge extensions into patient object
  enrichPatient(patient) {
    const extensions = this.getPatientExtensions(patient.id);
    return {
      ...patient,
      demographics: {
        ...patient.demographics,
        maritalStatus: extensions.maritalStatus || patient.demographics.maritalStatus || '',
        occupation: extensions.occupation || patient.demographics.occupation || '',
        emergencyContact: extensions.emergencyContact || patient.demographics.emergencyContact || '',
        emergencyContactPhone: extensions.emergencyContactPhone || patient.demographics.emergencyContactPhone || '',
        emergencyContactRelation: extensions.emergencyContactRelation || patient.demographics.emergencyContactRelation || ''
      }
    };
  }

  // Extract extensions from patient object for storage
  extractExtensions(patient) {
    const demographics = patient.demographics || {};
    return {
      maritalStatus: demographics.maritalStatus || '',
      occupation: demographics.occupation || '',
      emergencyContact: demographics.emergencyContact || '',
      emergencyContactPhone: demographics.emergencyContactPhone || '',
      emergencyContactRelation: demographics.emergencyContactRelation || ''
    };
  }
}

// Create singleton instance
const patientExtensionsStorage = new PatientExtensionsStorage();

export default patientExtensionsStorage;