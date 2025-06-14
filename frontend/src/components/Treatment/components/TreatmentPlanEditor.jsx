import React, { useState } from 'react';
import { 
  FileText, 
  Pill, 
  Calendar, 
  User,
  RefreshCw,
  Sparkles,
  Plus,
  X,
  Edit3,
  Check,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const TreatmentPlanEditor = ({ 
  treatmentPlan, 
  prescriptions, 
  onTreatmentPlanChange,
  onPrescriptionsChange,
  isGenerating,
  selectedDiagnosis 
}) => {
  const [showPrescriptionForm, setShowPrescriptionForm] = useState(false);
  const [editingPrescription, setEditingPrescription] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    treatment: true,
    prescriptions: true,
    followUp: true
  });
  const [newPrescription, setNewPrescription] = useState({
    medication: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: ''
  });
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const handleAddPrescription = () => {
    if (newPrescription.medication && newPrescription.dosage) {
      const prescription = {
        id: Date.now(),
        ...newPrescription
      };
      onPrescriptionsChange([...prescriptions, prescription]);
      setNewPrescription({
        medication: '',
        dosage: '',
        frequency: '',
        duration: '',
        instructions: ''
      });
      setShowPrescriptionForm(false);
    }
  };
  
  const handleUpdatePrescription = (id, updates) => {
    onPrescriptionsChange(prescriptions.map(p => 
      p.id === id ? { ...p, ...updates } : p
    ));
    setEditingPrescription(null);
  };
  
  const handleRemovePrescription = (id) => {
    onPrescriptionsChange(prescriptions.filter(p => p.id !== id));
  };
  
  // Parse treatment plan into sections
  const parseTreatmentPlan = (plan) => {
    if (!plan) return [];
    
    const sections = plan.split(/\d+\.\s+/).filter(Boolean);
    return sections.map((section, index) => {
      const lines = section.trim().split('\n');
      const title = lines[0].replace(/:/g, '');
      const content = lines.slice(1).join('\n').trim();
      return { title, content, index };
    });
  };
  
  const treatmentSections = parseTreatmentPlan(treatmentPlan);
  
  return (
    <div className="space-y-6">
      {/* Treatment Plan Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div 
          className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 cursor-pointer"
          onClick={() => toggleSection('treatment')}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-blue-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">Treatment Plan</h3>
              {isGenerating && (
                <div className="ml-3 flex items-center text-blue-600">
                  <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                  <span className="text-sm">Generating AI recommendations...</span>
                </div>
              )}
            </div>
            {expandedSections.treatment ? 
              <ChevronUp className="w-5 h-5 text-gray-500" /> : 
              <ChevronDown className="w-5 h-5 text-gray-500" />
            }
          </div>
        </div>
        
        {expandedSections.treatment && (
          <div className="p-6">
            {treatmentSections.length > 0 ? (
              <div className="space-y-4">
                {treatmentSections.map((section, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs mr-2">
                        {idx + 1}
                      </span>
                      {section.title}
                    </h4>
                    <div className="ml-8">
                      <textarea
                        value={section.content}
                        onChange={(e) => {
                          const newSections = [...treatmentSections];
                          newSections[idx].content = e.target.value;
                          const newPlan = newSections.map((s, i) => 
                            `${i + 1}. ${s.title}:\n${s.content}`
                          ).join('\n\n');
                          onTreatmentPlanChange(newPlan);
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        rows={4}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">
                  {selectedDiagnosis ? 
                    'Treatment plan will be generated based on the selected diagnosis' :
                    'Select a diagnosis to generate a treatment plan'
                  }
                </p>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Prescriptions Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div 
          className="px-6 py-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200 cursor-pointer"
          onClick={() => toggleSection('prescriptions')}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Pill className="w-5 h-5 text-purple-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">Prescriptions</h3>
              <span className="ml-2 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                {prescriptions.length}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowPrescriptionForm(!showPrescriptionForm);
                }}
                className="flex items-center text-purple-600 hover:text-purple-700 text-sm font-medium"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add
              </button>
              {expandedSections.prescriptions ? 
                <ChevronUp className="w-5 h-5 text-gray-500" /> : 
                <ChevronDown className="w-5 h-5 text-gray-500" />
              }
            </div>
          </div>
        </div>
        
        {expandedSections.prescriptions && (
          <div className="p-6">
            {prescriptions.length > 0 && (
              <div className="space-y-3 mb-4">
                {prescriptions.map((rx) => (
                  <div key={rx.id} className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-100">
                    {editingPrescription === rx.id ? (
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <input
                            type="text"
                            value={rx.medication}
                            onChange={(e) => handleUpdatePrescription(rx.id, { medication: e.target.value })}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="Medication"
                          />
                          <input
                            type="text"
                            value={rx.dosage}
                            onChange={(e) => handleUpdatePrescription(rx.id, { dosage: e.target.value })}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="Dosage"
                          />
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setEditingPrescription(null)}
                            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleRemovePrescription(rx.id)}
                            className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{rx.medication}</p>
                          <p className="text-sm text-gray-600 mt-1">
                            {rx.dosage} • {rx.frequency} • {rx.duration}
                          </p>
                          {rx.instructions && (
                            <p className="text-xs text-gray-500 mt-1 italic">{rx.instructions}</p>
                          )}
                        </div>
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={() => setEditingPrescription(rx.id)}
                            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleRemovePrescription(rx.id)}
                            className="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {showPrescriptionForm && (
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <h4 className="font-medium text-gray-900 mb-3">New Prescription</h4>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Medication *
                      </label>
                      <input
                        type="text"
                        value={newPrescription.medication}
                        onChange={(e) => setNewPrescription({ ...newPrescription, medication: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="e.g., Amoxicillin"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Dosage *
                      </label>
                      <input
                        type="text"
                        value={newPrescription.dosage}
                        onChange={(e) => setNewPrescription({ ...newPrescription, dosage: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="e.g., 500mg"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Frequency
                      </label>
                      <input
                        type="text"
                        value={newPrescription.frequency}
                        onChange={(e) => setNewPrescription({ ...newPrescription, frequency: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="e.g., Three times daily"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Duration
                      </label>
                      <input
                        type="text"
                        value={newPrescription.duration}
                        onChange={(e) => setNewPrescription({ ...newPrescription, duration: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="e.g., 7 days"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Special Instructions
                    </label>
                    <input
                      type="text"
                      value={newPrescription.instructions}
                      onChange={(e) => setNewPrescription({ ...newPrescription, instructions: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="e.g., Take with food"
                    />
                  </div>
                  <div className="flex justify-end space-x-2 pt-2">
                    <button
                      onClick={() => setShowPrescriptionForm(false)}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleAddPrescription}
                      disabled={!newPrescription.medication || !newPrescription.dosage}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-300"
                    >
                      Add Prescription
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TreatmentPlanEditor;