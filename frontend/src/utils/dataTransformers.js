/**
 * Data transformation utilities to convert between frontend and backend data formats
 */

// Transform frontend patient data to backend format
export const transformPatientToBackend = (frontendPatient) => {
  // Handle both new patient creation and existing patient updates
  const demographics = frontendPatient.demographics || {};
  const medicalBackground = frontendPatient.medicalBackground || {};
  
  // Split name into first and last name
  const fullName = demographics.name || frontendPatient.name || '';
  const nameParts = fullName.trim().split(' ');
  const firstName = nameParts[0] || '';
  const lastName = nameParts.slice(1).join(' ') || '';

  return {
    medical_record_number: frontendPatient.id || `MRN_${Date.now()}`,
    first_name: firstName,
    last_name: lastName,
    date_of_birth: demographics.dateOfBirth || frontendPatient.dateOfBirth,
    gender: (demographics.gender || frontendPatient.gender || 'unknown').toLowerCase(),
    email: demographics.email || frontendPatient.email || null,
    phone: demographics.phone || frontendPatient.phone || null,
    address: demographics.address || frontendPatient.address || null,
    // Handle emergency contact fields properly
    emergency_contact_name: demographics.emergencyContact || frontendPatient.emergencyContact || null,
    emergency_contact_phone: demographics.emergencyContactPhone || frontendPatient.emergencyContactPhone || null,
    emergency_contact_relationship: demographics.emergencyContactRelation || frontendPatient.emergencyContactRelation || null,
    // Add missing fields for SQLite storage
    marital_status: demographics.maritalStatus || frontendPatient.maritalStatus || null,
    occupation: demographics.occupation || frontendPatient.occupation || null,
    medical_history: [
      medicalBackground.pastMedicalHistory,
      medicalBackground.pastSurgicalHistory,
      medicalBackground.familyHistory,
      medicalBackground.socialHistory
    ].filter(Boolean).join('\n\n') || '',
    allergies: medicalBackground.allergies ? 
      medicalBackground.allergies.map(a => `${a.allergen}: ${a.reaction} (${a.severity})`).join('; ') : '',
    current_medications: medicalBackground.medications ? 
      medicalBackground.medications.map(m => `${m.name} ${m.dosage} ${m.frequency}`).join('; ') : ''
  };
};

// Transform backend patient data to frontend format
export const transformPatientFromBackend = (backendPatient) => {
  const transformed = {
    id: backendPatient.id || backendPatient.medical_record_number,
    demographics: {
      name: `${backendPatient.first_name} ${backendPatient.last_name}`.trim(),
      dateOfBirth: backendPatient.date_of_birth,
      gender: capitalizeFirst(backendPatient.gender || 'unknown'),
      phone: backendPatient.phone || '',
      email: backendPatient.email || '',
      address: backendPatient.address || '',
      // Handle emergency contact fields separately
      emergencyContact: backendPatient.emergency_contact_name || '',
      emergencyContactPhone: backendPatient.emergency_contact_phone || '',
      emergencyContactRelation: backendPatient.emergency_contact_relationship || '',
      // Add missing fields
      maritalStatus: backendPatient.marital_status || '',
      occupation: backendPatient.occupation || '',
      insuranceInfo: {} // Not in backend schema
    },
    medicalBackground: {
      allergies: parseAllergies(backendPatient.allergies),
      medications: parseMedications(backendPatient.current_medications),
      chronicConditions: [], // Would need to be derived from episodes/diagnoses
      pastMedicalHistory: extractMedicalHistory(backendPatient.medical_history, 'medical'),
      pastSurgicalHistory: extractMedicalHistory(backendPatient.medical_history, 'surgical'),
      familyHistory: extractMedicalHistory(backendPatient.medical_history, 'family'),
      socialHistory: extractMedicalHistory(backendPatient.medical_history, 'social')
    },
    createdAt: backendPatient.created_at,
    updatedAt: backendPatient.updated_at
  };
  return transformed;
};

// Transform frontend episode data to backend format
export const transformEpisodeToBackend = (frontendEpisode, patientId) => {
  return {
    patient_id: patientId || frontendEpisode.patientId,
    chief_complaint: frontendEpisode.chiefComplaint || '',
    status: mapFrontendStatusToBackend(frontendEpisode.status || 'active'),
    encounter_type: mapCategoryToEncounterType(frontendEpisode.category),
    priority: 'routine', // Default
    symptoms: frontendEpisode.tags ? frontendEpisode.tags.join(', ') : '',
    clinical_notes: '',
    assessment_notes: '',
    plan_notes: '',
    start_date: frontendEpisode.createdAt,
    end_date: frontendEpisode.resolvedAt || null,
    provider_id: 'system',
    location: null
  };
};

// Transform backend episode data to frontend format
export const transformEpisodeFromBackend = (backendEpisode) => {
  return {
    id: backendEpisode.id,
    patientId: backendEpisode.patient_id,
    chiefComplaint: backendEpisode.chief_complaint,
    category: mapEncounterTypeToCategory(backendEpisode.encounter_type),
    status: mapBackendStatusToFrontend(backendEpisode.status),
    createdAt: backendEpisode.start_date || backendEpisode.created_at,
    resolvedAt: backendEpisode.end_date,
    lastEncounterId: null, // Frontend concept, not in backend
    relatedEpisodeIds: [], // Frontend concept, not in backend
    tags: backendEpisode.symptoms ? backendEpisode.symptoms.split(', ').filter(Boolean) : []
  };
};

// Helper functions
const capitalizeFirst = (str) => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

const parseAllergies = (allergiesText) => {
  if (!allergiesText) return [];
  return allergiesText.split(';').map(allergy => {
    const parts = allergy.trim().split(':');
    if (parts.length >= 2) {
      const allergen = parts[0].trim();
      const reactionPart = parts[1].trim();
      const reactionMatch = reactionPart.match(/^(.+?)\s*\((.+?)\)$/);
      
      if (reactionMatch) {
        return {
          id: `A_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
          allergen,
          reaction: reactionMatch[1].trim(),
          severity: reactionMatch[2].trim(),
          addedDate: new Date().toISOString()
        };
      } else {
        return {
          id: `A_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
          allergen,
          reaction: reactionPart,
          severity: 'unknown',
          addedDate: new Date().toISOString()
        };
      }
    }
    return null;
  }).filter(Boolean);
};

const parseMedications = (medicationsText) => {
  if (!medicationsText) return [];
  return medicationsText.split(';').map(medication => {
    const parts = medication.trim().split(' ');
    if (parts.length >= 1) {
      return {
        id: `M_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        name: parts[0],
        dosage: parts[1] || '',
        frequency: parts.slice(2).join(' ') || '',
        startDate: new Date().toISOString(),
        ongoing: true
      };
    }
    return null;
  }).filter(Boolean);
};

const extractMedicalHistory = (fullHistory, type) => {
  if (!fullHistory) return '';
  const sections = fullHistory.split('\n\n');
  // This is a simple implementation - in reality you'd need more sophisticated parsing
  switch (type) {
    case 'medical':
      return sections[0] || '';
    case 'surgical':
      return sections[1] || '';
    case 'family':
      return sections[2] || '';
    case 'social':
      return sections[3] || '';
    default:
      return '';
  }
};

const mapCategoryToEncounterType = (category) => {
  switch (category) {
    case 'acute':
      return 'outpatient';
    case 'chronic':
      return 'inpatient';
    case 'preventive':
      return 'outpatient';
    case 'emergency':
      return 'emergency';
    default:
      return 'outpatient';
  }
};

const mapEncounterTypeToCategory = (encounterType) => {
  switch (encounterType) {
    case 'outpatient':
      return 'acute';
    case 'inpatient':
      return 'chronic';
    case 'emergency':
      return 'emergency';
    default:
      return 'acute';
  }
};

const mapBackendStatusToFrontend = (backendStatus) => {
  switch (backendStatus) {
    case 'active':
      return 'active';
    case 'in-progress':
      return 'active';
    case 'completed':
      return 'resolved';
    case 'closed':
      return 'resolved';
    case 'chronic':
      return 'chronic-management';
    case 'deleted':
      return 'deleted'; // Keep deleted status for filtering
    default:
      return 'active';
  }
};

const mapFrontendStatusToBackend = (frontendStatus) => {
  switch (frontendStatus) {
    case 'active':
      return 'active';
    case 'resolved':
      return 'completed';
    case 'chronic-management':
      return 'chronic';
    default:
      return 'active';
  }
};

export default {
  transformPatientToBackend,
  transformPatientFromBackend,
  transformEpisodeToBackend,
  transformEpisodeFromBackend
};