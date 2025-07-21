import React, { useState, useEffect } from 'react';
import { X, User, Phone, Mail, Home, Calendar, Shield, Heart, Pill, 
         AlertCircle, Clock, Plus, Trash2, Edit2, Save, UserCheck,
         Stethoscope, Activity, FileText, Info, RefreshCw } from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';
import { syncPatientDataFromEncounters } from '../../utils/patientDataSync';

const EditPatientModal = ({ patient, onClose }) => {
  const { updatePatientDemographics, updatePatientMedicalBackground } = usePatient();
  const { getPatientEpisodes } = useEpisode();
  const { getEpisodeEncounters } = useEncounter();
  
  // Initialize form data with patient information
  const [formData, setFormData] = useState({
    demographics: {
      name: patient.demographics.name || '',
      dateOfBirth: patient.demographics.dateOfBirth || '',
      gender: patient.demographics.gender || '',
      phone: patient.demographics.phone || '',
      email: patient.demographics.email || '',
      address: patient.demographics.address || '',
      emergencyContact: patient.demographics.emergencyContact || '',
      emergencyContactPhone: patient.demographics.emergencyContactPhone || '',
      emergencyContactRelation: patient.demographics.emergencyContactRelation || '',
      occupation: patient.demographics.occupation || '',
      maritalStatus: patient.demographics.maritalStatus || ''
    },
    medicalBackground: {
      bloodType: patient.medicalBackground?.bloodType || '',
      allergies: patient.medicalBackground?.allergies || [],
      medications: patient.medicalBackground?.medications || [],
      chronicConditions: patient.medicalBackground?.chronicConditions || [],
      pastMedicalHistory: patient.medicalBackground?.pastMedicalHistory || '',
      pastSurgicalHistory: patient.medicalBackground?.pastSurgicalHistory || '',
      familyHistory: patient.medicalBackground?.familyHistory || '',
      socialHistory: patient.medicalBackground?.socialHistory || '',
      immunizations: patient.medicalBackground?.immunizations || [],
      vitalSigns: patient.medicalBackground?.vitalSigns || {
        height: '',
        weight: '',
        bmi: ''
      }
    }
  });
  
  const [activeTab, setActiveTab] = useState('demographics');
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [showAutoUpdateInfo, setShowAutoUpdateInfo] = useState(false);
  const [syncedData, setSyncedData] = useState({ conditions: 0, medications: 0 });
  
  // Analyze encounters to extract auto-updated information
  useEffect(() => {
    const analyzeEncountersForUpdates = () => {
      const episodes = getPatientEpisodes(patient.id);
      const allEncounters = episodes.flatMap(ep => getEpisodeEncounters(ep.id));
      
      // Extract conditions from assessments
      const conditionsFromEncounters = new Set();
      const medicationsFromEncounters = new Set();
      
      allEncounters.forEach(encounter => {
        // Extract diagnoses/conditions
        if (encounter.soap?.assessment?.diagnoses) {
          encounter.soap.assessment.diagnoses.forEach(dx => {
            if (dx.icd10 && dx.description) {
              conditionsFromEncounters.add(JSON.stringify({
                condition: dx.description,
                icd10: dx.icd10,
                diagnosedDate: encounter.date,
                fromEncounter: encounter.id
              }));
            }
          });
        }
        
        // Extract medications from plans
        if (encounter.soap?.plan?.medications) {
          encounter.soap.plan.medications.forEach(med => {
            medicationsFromEncounters.add(JSON.stringify({
              name: med.name,
              dosage: med.dosage,
              frequency: med.frequency,
              startDate: encounter.date,
              fromEncounter: encounter.id
            }));
          });
        }
      });
      
      // Convert back from Set to Array
      const autoConditions = Array.from(conditionsFromEncounters).map(c => JSON.parse(c));
      const autoMedications = Array.from(medicationsFromEncounters).map(m => JSON.parse(m));
      
      // Check for auto-updated fields
      if (autoConditions.length > 0 || autoMedications.length > 0) {
        setShowAutoUpdateInfo(true);
      }
    };
    
    analyzeEncountersForUpdates();
  }, [patient.id, getPatientEpisodes, getEpisodeEncounters]);
  
  // Handle input changes
  const handleDemographicChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      demographics: { ...prev.demographics, [field]: value }
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };
  
  const handleMedicalChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      medicalBackground: { ...prev.medicalBackground, [field]: value }
    }));
  };
  
  const handleVitalSignChange = (field, value) => {
    const newVitalSigns = { ...formData.medicalBackground.vitalSigns, [field]: value };
    
    // Auto-calculate BMI if height and weight are provided
    if (field === 'height' || field === 'weight') {
      const height = field === 'height' ? value : formData.medicalBackground.vitalSigns.height;
      const weight = field === 'weight' ? value : formData.medicalBackground.vitalSigns.weight;
      
      if (height && weight) {
        const heightInMeters = parseFloat(height) / 100; // Convert cm to meters
        const bmi = (parseFloat(weight) / (heightInMeters * heightInMeters)).toFixed(1);
        newVitalSigns.bmi = bmi;
      }
    }
    
    handleMedicalChange('vitalSigns', newVitalSigns);
  };
  
  // Handle allergy operations
  const addAllergy = () => {
    const newAllergy = {
      id: `A${Date.now()}`,
      allergen: '',
      reaction: '',
      severity: 'mild',
      addedDate: new Date().toISOString()
    };
    handleMedicalChange('allergies', [...formData.medicalBackground.allergies, newAllergy]);
  };
  
  const updateAllergy = (id, field, value) => {
    const updated = formData.medicalBackground.allergies.map(a =>
      a.id === id ? { ...a, [field]: value } : a
    );
    handleMedicalChange('allergies', updated);
  };
  
  const removeAllergy = (id) => {
    handleMedicalChange('allergies', formData.medicalBackground.allergies.filter(a => a.id !== id));
  };
  
  // Handle medication operations
  const addMedication = () => {
    const newMedication = {
      id: `M${Date.now()}`,
      name: '',
      dosage: '',
      frequency: '',
      ongoing: true,
      startDate: new Date().toISOString()
    };
    handleMedicalChange('medications', [...formData.medicalBackground.medications, newMedication]);
  };
  
  const updateMedication = (id, field, value) => {
    const updated = formData.medicalBackground.medications.map(m =>
      m.id === id ? { ...m, [field]: value } : m
    );
    handleMedicalChange('medications', updated);
  };
  
  const removeMedication = (id) => {
    handleMedicalChange('medications', formData.medicalBackground.medications.filter(m => m.id !== id));
  };
  
  // Handle chronic condition operations
  const addCondition = () => {
    const newCondition = {
      id: `C${Date.now()}`,
      condition: '',
      icd10: '',
      diagnosedDate: new Date().toISOString(),
      status: 'active'
    };
    handleMedicalChange('chronicConditions', [...formData.medicalBackground.chronicConditions, newCondition]);
  };
  
  const updateCondition = (id, field, value) => {
    const updated = formData.medicalBackground.chronicConditions.map(c =>
      c.id === id ? { ...c, [field]: value } : c
    );
    handleMedicalChange('chronicConditions', updated);
  };
  
  const removeCondition = (id) => {
    handleMedicalChange('chronicConditions', formData.medicalBackground.chronicConditions.filter(c => c.id !== id));
  };
  
  // Sync data from encounters
  const syncFromEncounters = () => {
    const episodes = getPatientEpisodes(patient.id);
    const syncedData = syncPatientDataFromEncounters(patient, episodes, getEpisodeEncounters);
    
    // Update form data with synced data
    setFormData(prev => ({
      ...prev,
      medicalBackground: {
        ...prev.medicalBackground,
        chronicConditions: syncedData.chronicConditions,
        medications: syncedData.medications
      }
    }));
    
    // Count synced items
    const syncedConditionsCount = syncedData.chronicConditions.filter(c => c.fromEncounter).length;
    const syncedMedicationsCount = syncedData.medications.filter(m => m.fromEncounter).length;
    
    setSyncedData({
      conditions: syncedConditionsCount,
      medications: syncedMedicationsCount
    });
    
    if (window.showNotification) {
      window.showNotification(
        `Synced ${syncedConditionsCount} conditions and ${syncedMedicationsCount} medications from encounters`,
        'success'
      );
    }
  };

  // Validation function
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.demographics.name.trim()) {
      newErrors.name = 'Patient name is required';
    }
    
    if (!formData.demographics.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    }
    
    if (!formData.demographics.gender) {
      newErrors.gender = 'Gender is required';
    }
    
    // Validate allergies
    formData.medicalBackground.allergies.forEach((allergy, index) => {
      if (allergy.allergen && !allergy.reaction) {
        newErrors[`allergy-${index}`] = 'Reaction is required for allergies';
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Save function
  const handleSave = async () => {
    if (!validateForm()) {
      if (window.showNotification) {
        window.showNotification('Please fix the errors before saving', 'error');
      }
      return;
    }
    
    setIsSaving(true);
    
    try {
      // Update demographics
      updatePatientDemographics(patient.id, formData.demographics);
      
      // Update medical background
      updatePatientMedicalBackground(patient.id, formData.medicalBackground);
      
      // Update last visit date if there are recent encounters
      const episodes = getPatientEpisodes(patient.id);
      const allEncounters = episodes.flatMap(ep => getEpisodeEncounters(ep.id));
      if (allEncounters.length > 0) {
        const lastEncounter = allEncounters.sort((a, b) => new Date(b.date) - new Date(a.date))[0];
        updatePatientDemographics(patient.id, { ...formData.demographics, lastVisit: lastEncounter.date });
      } else {
        updatePatientDemographics(patient.id, formData.demographics);
      }
      
      if (window.showNotification) {
        window.showNotification('Patient information updated successfully', 'success');
      }
      
      // Close modal after a short delay
      setTimeout(() => {
        onClose();
      }, 500);
      
    } catch (error) {
      console.error('Error saving patient data:', error);
      if (window.showNotification) {
        window.showNotification('Failed to save patient information', 'error');
      }
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center">
            <Edit2 className="w-6 h-6 mr-3" />
            <h2 className="text-xl font-bold">Edit Patient Information</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            disabled={isSaving}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Auto-update Info Banner */}
        {showAutoUpdateInfo && (
          <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
            <div className="flex items-start">
              <Info className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Some information (diagnoses, medications) is automatically updated from encounter documentation. 
                  These fields reflect the most recent data from patient encounters.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Tab Navigation */}
        <div className="border-b border-gray-200 bg-gray-50">
          <nav className="flex px-6">
            <button
              onClick={() => setActiveTab('demographics')}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'demographics'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-500 border-transparent hover:text-gray-700'
              }`}
            >
              <User className="w-4 h-4 inline mr-2" />
              Demographics
            </button>
            <button
              onClick={() => setActiveTab('medical')}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'medical'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-500 border-transparent hover:text-gray-700'
              }`}
            >
              <Heart className="w-4 h-4 inline mr-2" />
              Medical Information
            </button>
          </nav>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'demographics' && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <User className="w-5 h-5 mr-2 text-gray-600" />
                  Basic Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.demographics.name}
                      onChange={(e) => handleDemographicChange('name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.name ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Date of Birth <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"                      value={formData.demographics.dateOfBirth}
                      onChange={(e) => handleDemographicChange('dateOfBirth', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.dateOfBirth ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.dateOfBirth && (
                      <p className="mt-1 text-sm text-red-600">{errors.dateOfBirth}</p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Gender <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.demographics.gender}
                      onChange={(e) => handleDemographicChange('gender', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.gender ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                      <option value="Prefer not to say">Prefer not to say</option>
                    </select>
                    {errors.gender && (
                      <p className="mt-1 text-sm text-red-600">{errors.gender}</p>
                    )}
                  </div>                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Marital Status
                    </label>
                    <select
                      value={formData.demographics.maritalStatus}
                      onChange={(e) => handleDemographicChange('maritalStatus', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Occupation
                    </label>
                    <input
                      type="text"
                      value={formData.demographics.occupation}
                      onChange={(e) => handleDemographicChange('occupation', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Teacher, Engineer, etc."
                    />
                  </div>
                </div>
              </div>              
              {/* Contact Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Phone className="w-5 h-5 mr-2 text-gray-600" />
                  Contact Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={formData.demographics.phone}
                      onChange={(e) => handleDemographicChange('phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={formData.demographics.email}
                      onChange={(e) => handleDemographicChange('email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="patient@email.com"
                    />
                  </div>                  
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Address
                    </label>
                    <textarea
                      value={formData.demographics.address}
                      onChange={(e) => handleDemographicChange('address', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="123 Main St, City, State ZIP"
                    />
                  </div>
                </div>
              </div>
              
              {/* Emergency Contact */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <UserCheck className="w-5 h-5 mr-2 text-gray-600" />
                  Emergency Contact
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      value={formData.demographics.emergencyContact}
                      onChange={(e) => handleDemographicChange('emergencyContact', e.target.value)}                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="John Doe"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Relationship
                    </label>
                    <input
                      type="text"
                      value={formData.demographics.emergencyContactRelation}
                      onChange={(e) => handleDemographicChange('emergencyContactRelation', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Spouse, Parent, etc."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={formData.demographics.emergencyContactPhone}
                      onChange={(e) => handleDemographicChange('emergencyContactPhone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="(555) 987-6543"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}          
          {activeTab === 'medical' && (
            <div className="space-y-6">
              {/* Sync from Encounters Button */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-blue-900 mb-1">Sync from Encounters</h4>
                    <p className="text-xs text-blue-700">
                      Automatically extract diagnoses and medications from documented encounters
                    </p>
                    {(syncedData.conditions > 0 || syncedData.medications > 0) && (
                      <p className="text-xs text-blue-600 mt-1">
                        Last sync: {syncedData.conditions} conditions, {syncedData.medications} medications
                      </p>
                    )}
                  </div>
                  <button
                    onClick={syncFromEncounters}
                    className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center text-sm"
                  >
                    <RefreshCw className="w-4 h-4 mr-1" />
                    Sync Now
                  </button>
                </div>
              </div>
              
              {/* Vital Signs & Basic Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-gray-600" />
                  Vital Signs & Basic Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Height (cm)
                    </label>
                    <input
                      type="number"
                      value={formData.medicalBackground.vitalSigns.height}
                      onChange={(e) => handleVitalSignChange('height', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="170"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Weight (kg)
                    </label>
                    <input
                      type="number"
                      value={formData.medicalBackground.vitalSigns.weight}
                      onChange={(e) => handleVitalSignChange('weight', e.target.value)}                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="70"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      BMI (auto-calculated)
                    </label>
                    <input
                      type="text"
                      value={formData.medicalBackground.vitalSigns.bmi}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50"
                      placeholder="Auto"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Blood Type
                    </label>
                    <select
                      value={formData.medicalBackground.bloodType}
                      onChange={(e) => handleMedicalChange('bloodType', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Unknown</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Allergies */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
                  Allergies
                </h3>
                {formData.medicalBackground.allergies.length === 0 ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                    <p className="text-green-800">No known allergies</p>
                  </div>
                ) : (
                  <div className="space-y-3 mb-4">
                    {formData.medicalBackground.allergies.map((allergy, index) => (
                      <div key={allergy.id} className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Allergen
                            </label>
                            <input                              type="text"
                              value={allergy.allergen}
                              onChange={(e) => updateAllergy(allergy.id, 'allergen', e.target.value)}
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-transparent"
                              placeholder="e.g., Penicillin"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Reaction
                            </label>
                            <input
                              type="text"
                              value={allergy.reaction}
                              onChange={(e) => updateAllergy(allergy.id, 'reaction', e.target.value)}
                              className={`w-full px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-red-500 focus:border-transparent ${
                                errors[`allergy-${index}`] ? 'border-red-500' : 'border-gray-300'
                              }`}
                              placeholder="e.g., Hives"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Severity
                            </label>
                            <select
                              value={allergy.severity}
                              onChange={(e) => updateAllergy(allergy.id, 'severity', e.target.value)}
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            >
                              <option value="mild">Mild</option>                              <option value="moderate">Moderate</option>
                              <option value="severe">Severe</option>
                            </select>
                          </div>
                          <div className="flex items-end">
                            <button
                              onClick={() => removeAllergy(allergy.id)}
                              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        {errors[`allergy-${index}`] && (
                          <p className="mt-2 text-sm text-red-600">{errors[`allergy-${index}`]}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  onClick={addAllergy}
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Allergy
                </button>
              </div>
              
              {/* Current Medications */}
              <div>                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Pill className="w-5 h-5 mr-2 text-blue-600" />
                  Current Medications
                </h3>
                {formData.medicalBackground.medications.filter(m => m.ongoing).length === 0 ? (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                    <p className="text-gray-600">No current medications</p>
                  </div>
                ) : (
                  <div className="space-y-3 mb-4">
                    {formData.medicalBackground.medications
                      .filter(m => m.ongoing)
                      .map((medication) => (
                        <div key={medication.id} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                            <div className="md:col-span-2">
                              <label className="block text-xs font-medium text-gray-700 mb-1">
                                Medication Name
                              </label>
                              <input
                                type="text"
                                value={medication.name}
                                onChange={(e) => updateMedication(medication.id, 'name', e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., Metformin"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-gray-700 mb-1">
                                Dosage
                              </label>                              <input
                                type="text"
                                value={medication.dosage}
                                onChange={(e) => updateMedication(medication.id, 'dosage', e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="500mg"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-gray-700 mb-1">
                                Frequency
                              </label>
                              <input
                                type="text"
                                value={medication.frequency}
                                onChange={(e) => updateMedication(medication.id, 'frequency', e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Twice daily"
                              />
                            </div>
                            <div className="flex items-end">
                              <button
                                onClick={() => removeMedication(medication.id)}
                                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                          {medication.fromEncounter && (
                            <p className="text-xs text-blue-600 mt-2 flex items-center">
                              <RefreshCw className="w-3 h-3 mr-1" />
                              Auto-synced from encounter
                            </p>
                          )}
                        </div>
                      ))}
                  </div>                )}
                <button
                  onClick={addMedication}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Medication
                </button>
              </div>
              
              {/* Chronic Conditions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Heart className="w-5 h-5 mr-2 text-purple-600" />
                  Chronic Conditions
                  {showAutoUpdateInfo && (
                    <Info className="w-4 h-4 ml-2 text-blue-600" title="Auto-updated from encounters" />
                  )}
                </h3>
                {formData.medicalBackground.chronicConditions.length === 0 ? (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                    <p className="text-gray-600">No chronic conditions documented</p>
                  </div>
                ) : (
                  <div className="space-y-3 mb-4">
                    {formData.medicalBackground.chronicConditions.map((condition) => (
                      <div key={condition.id} className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                          <div className="md:col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Condition                            </label>
                            <input
                              type="text"
                              value={condition.condition}
                              onChange={(e) => updateCondition(condition.id, 'condition', e.target.value)}
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              placeholder="e.g., Type 2 Diabetes"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              ICD-10 Code
                            </label>
                            <input
                              type="text"
                              value={condition.icd10}
                              onChange={(e) => updateCondition(condition.id, 'icd10', e.target.value)}
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              placeholder="E11.9"
                            />
                          </div>
                          <div className="flex items-end">
                            <button
                              onClick={() => removeCondition(condition.id)}
                              className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors text-sm"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        {condition.fromEncounter && (
                          <p className="text-xs text-purple-600 mt-2 flex items-center">
                            <RefreshCw className="w-3 h-3 mr-1" />
                            Auto-synced from encounter
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  onClick={addCondition}
                  className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Condition
                </button>
              </div>
              
              {/* Medical History */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-gray-600" />
                  Medical History
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Past Medical History
                    </label>
                    <textarea
                      value={formData.medicalBackground.pastMedicalHistory}
                      onChange={(e) => handleMedicalChange('pastMedicalHistory', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"                      placeholder="Document significant past medical history, hospitalizations..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Past Surgical History
                    </label>
                    <textarea
                      value={formData.medicalBackground.pastSurgicalHistory}
                      onChange={(e) => handleMedicalChange('pastSurgicalHistory', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="List previous surgeries with dates..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Family History
                    </label>
                    <textarea
                      value={formData.medicalBackground.familyHistory}
                      onChange={(e) => handleMedicalChange('familyHistory', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Document significant family medical history..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">                      Social History
                    </label>
                    <textarea
                      value={formData.medicalBackground.socialHistory}
                      onChange={(e) => handleMedicalChange('socialHistory', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Document tobacco, alcohol, drug use, occupation, living situation..."
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={isSaving}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
          >
            {isSaving ? (              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditPatientModal;