import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  TestTube, 
  ChevronRight, 
  ChevronLeft,
  Plus,
  Check,
  X,
  Info,
  Filter,
  ArrowUpDown,
  AlertCircle,
  Edit3,
  FileText,
  Brain,
  Search,
  Pill,
  Heart,
  Activity,
  Stethoscope,
  Calendar
} from 'lucide-react';

const RecommendedTests = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [activeTab, setActiveTab] = useState('diagnostics'); // 'diagnostics' or 'therapeutics'
  const [recommendedTests, setRecommendedTests] = useState([]);
  const [selectedTests, setSelectedTests] = useState([]);
  const [therapeuticPlan, setTherapeuticPlan] = useState({
    medications: [],
    procedures: [],
    referrals: [],
    followUp: '',
    patientEducation: ''
  });
  const [showCustomTestModal, setShowCustomTestModal] = useState(false);
  const [customTest, setCustomTest] = useState({
    name: '',
    category: 'Other',
    priority: 'medium',
    purpose: '',
    expectedFindings: '',
    turnaroundTime: '',
    specialInstructions: ''
  });
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [sortBy, setSortBy] = useState('priority');
  const [searchTerm, setSearchTerm] = useState('');  
  useEffect(() => {
    if (patientData.selectedTests && patientData.selectedTests.length > 0) {
      setSelectedTests(patientData.selectedTests);
    }
    
    if (patientData.therapeuticPlan) {
      setTherapeuticPlan(patientData.therapeuticPlan);
    }
    
    // Generate test recommendations based on diagnosis
    if (patientData.doctorDiagnosis) {
      generateRecommendations();
    }
  }, []);
  
  const generateRecommendations = () => {
    // Sample recommended tests based on common diagnoses
    const commonTests = [
      {
        id: 'cbc',
        name: 'Complete Blood Count (CBC) with Differential',
        category: 'Laboratory',
        priority: 'high',
        purpose: 'Assess infection markers, anemia, platelet count',
        turnaroundTime: '1-2 hours',
        cost: '$'
      },
      {
        id: 'cxr',
        name: 'Chest X-Ray (PA and Lateral)',
        category: 'Imaging',
        priority: 'high',
        purpose: 'Evaluate for pneumonia, effusion, or other lung pathology',
        turnaroundTime: '30 minutes',
        cost: '$$'
      },
      {
        id: 'bmp',
        name: 'Basic Metabolic Panel',
        category: 'Laboratory',
        priority: 'medium',
        purpose: 'Assess electrolytes, kidney function, glucose',
        turnaroundTime: '1-2 hours',
        cost: '$'
      }
    ];
    
    setRecommendedTests(commonTests);
  };  
  const handleTestToggle = (test) => {
    const isSelected = selectedTests.some(t => t.id === test.id);
    if (isSelected) {
      setSelectedTests(selectedTests.filter(t => t.id !== test.id));
    } else {
      setSelectedTests([...selectedTests, test]);
    }
  };
  
  const handleAddMedication = () => {
    const newMed = {
      id: Date.now(),
      name: '',
      dosage: '',
      frequency: '',
      duration: '',
      route: 'oral'
    };
    setTherapeuticPlan({
      ...therapeuticPlan,
      medications: [...therapeuticPlan.medications, newMed]
    });
  };
  
  const updateMedication = (id, field, value) => {
    setTherapeuticPlan({
      ...therapeuticPlan,
      medications: therapeuticPlan.medications.map(med =>
        med.id === id ? { ...med, [field]: value } : med
      )
    });
  };
  
  const removeMedication = (id) => {
    setTherapeuticPlan({
      ...therapeuticPlan,
      medications: therapeuticPlan.medications.filter(med => med.id !== id)
    });
  };
  
  const handleContinue = () => {
    // Save both diagnostic and therapeutic plans
    updatePatientData('selectedTests', selectedTests);
    updatePatientData('therapeuticPlan', therapeuticPlan);
    setCurrentStep('test-results');
  };
  
  const handleBack = () => {
    setCurrentStep('diagnostic-analysis');
  };  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Plan (P)</h2>
        <p className="text-gray-600">Create diagnostic and therapeutic plans for the patient</p>
      </div>
      
      {/* Diagnosis Context */}
      {patientData.doctorDiagnosis && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <Activity className="w-5 h-5 text-blue-600 mr-2" />
            <span className="font-medium text-blue-900">Working Diagnosis: </span>
            <span className="ml-2 text-blue-800">{patientData.doctorDiagnosis}</span>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'diagnostics'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <TestTube className="w-4 h-4 inline mr-2" />
              Diagnostic Tests
            </button>
            <button
              onClick={() => setActiveTab('therapeutics')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'therapeutics'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Heart className="w-4 h-4 inline mr-2" />
              Therapeutic Plan
            </button>
          </nav>
        </div>        
        <div className="p-6">
          {activeTab === 'diagnostics' ? (
            /* Diagnostic Tests Tab */
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recommended Diagnostic Tests</h3>
                <button
                  onClick={() => setShowCustomTestModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Custom Test
                </button>
              </div>
              
              {recommendedTests.length > 0 ? (
                <div className="space-y-3">
                  {recommendedTests.map((test) => (
                    <div
                      key={test.id}
                      className={`border rounded-lg p-4 transition-all cursor-pointer ${
                        selectedTests.some(t => t.id === test.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleTestToggle(test)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <div className={`w-5 h-5 rounded border-2 mr-3 flex items-center justify-center ${
                              selectedTests.some(t => t.id === test.id)
                                ? 'border-blue-500 bg-blue-500'
                                : 'border-gray-300'
                            }`}>
                              {selectedTests.some(t => t.id === test.id) && (
                                <Check className="w-3 h-3 text-white" />
                              )}
                            </div>
                            <h4 className="font-medium text-gray-900">{test.name}</h4>
                          </div>
                          <p className="text-sm text-gray-600 mt-1 ml-8">{test.purpose}</p>
                          <div className="flex items-center space-x-4 mt-2 ml-8 text-xs text-gray-500">
                            <span>Category: {test.category}</span>
                            <span>Turnaround: {test.turnaroundTime}</span>
                            <span>Cost: {test.cost}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TestTube className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No tests recommended based on current diagnosis</p>
                </div>
              )}
            </div>
          ) : (            /* Therapeutic Plan Tab */
            <div className="space-y-6">
              {/* Medications Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Medications</h3>
                  <button
                    onClick={handleAddMedication}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Medication
                  </button>
                </div>
                
                {therapeuticPlan.medications.length > 0 ? (
                  <div className="space-y-3">
                    {therapeuticPlan.medications.map((med) => (
                      <div key={med.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                          <input
                            type="text"
                            value={med.name}
                            onChange={(e) => updateMedication(med.id, 'name', e.target.value)}
                            placeholder="Medication name"
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            value={med.dosage}
                            onChange={(e) => updateMedication(med.id, 'dosage', e.target.value)}
                            placeholder="Dosage"
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            value={med.frequency}
                            onChange={(e) => updateMedication(med.id, 'frequency', e.target.value)}
                            placeholder="Frequency"
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                          <input
                            type="text"
                            value={med.duration}
                            onChange={(e) => updateMedication(med.id, 'duration', e.target.value)}
                            placeholder="Duration"
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          />
                          <button
                            onClick={() => removeMedication(med.id)}
                            className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Pill className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">No medications prescribed yet</p>
                  </div>
                )}
              </div>              
              {/* Follow-up Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Follow-up Plan</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Follow-up Timeline
                    </label>
                    <input
                      type="text"
                      value={therapeuticPlan.followUp}
                      onChange={(e) => setTherapeuticPlan({...therapeuticPlan, followUp: e.target.value})}
                      placeholder="e.g., 1 week, 2-3 days if symptoms worsen"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Patient Education & Instructions
                    </label>
                    <textarea
                      value={therapeuticPlan.patientEducation}
                      onChange={(e) => setTherapeuticPlan({...therapeuticPlan, patientEducation: e.target.value})}
                      rows={4}
                      placeholder="Instructions for home care, warning signs to watch for, lifestyle modifications..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Selected Summary */}
      {(selectedTests.length > 0 || therapeuticPlan.medications.length > 0) && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <h4 className="font-semibold text-green-900 mb-2">Plan Summary</h4>
          <div className="text-sm text-green-800 space-y-1">
            {selectedTests.length > 0 && (
              <p>• {selectedTests.length} diagnostic test(s) ordered</p>
            )}
            {therapeuticPlan.medications.length > 0 && (
              <p>• {therapeuticPlan.medications.length} medication(s) prescribed</p>
            )}
            {therapeuticPlan.followUp && (
              <p>• Follow-up: {therapeuticPlan.followUp}</p>
            )}
          </div>
        </div>
      )}
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center shadow-sm hover:shadow-md"
        >
          Continue to Results Review
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default RecommendedTests;