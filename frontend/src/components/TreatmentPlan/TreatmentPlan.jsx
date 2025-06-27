import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  ChevronLeft,
  ChevronRight,
  Pill,
  FileText,
  Calendar,
  User,
  AlertCircle,
  Save,
  RefreshCw,
  Sparkles,
  Plus,
  Trash2,
  Edit3,
  CheckCircle,
  Clock,
  Info,
  Heart,
  Brain,
  Stethoscope,
  X,
  Check
} from 'lucide-react';
import TreatmentPlanEditor from '../Treatment/components/TreatmentPlanEditor';

const TreatmentPlan = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [treatmentPlan, setTreatmentPlan] = useState('');
  const [prescriptions, setPrescriptions] = useState([]);
  const [editingPrescriptionId, setEditingPrescriptionId] = useState(null);
  const [tempPrescription, setTempPrescription] = useState(null);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [followUpRecommendations, setFollowUpRecommendations] = useState('');
  const [patientEducation, setPatientEducation] = useState('');
  const [selectedTab, setSelectedTab] = useState('treatment'); // 'treatment', 'prescriptions', 'followup', 'education'
  
  useEffect(() => {
    // Load existing data if available
    if (patientData.treatmentPlan) {
      setTreatmentPlan(patientData.treatmentPlan);
    }
    if (patientData.prescriptions && patientData.prescriptions.length > 0) {
      setPrescriptions(patientData.prescriptions);
    }
    if (patientData.followUpRecommendations) {
      setFollowUpRecommendations(patientData.followUpRecommendations);
    }
    if (patientData.patientEducation) {
      setPatientEducation(patientData.patientEducation);
    }
    
    // Generate treatment plan if not already present
    if (!patientData.treatmentPlan && patientData.selectedDiagnosis) {
      generateTreatmentPlan();
    }
  }, []);
  
  const generateTreatmentPlan = async () => {
    setIsGeneratingPlan(true);
    const diagnosis = patientData.selectedDiagnosis;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Enhanced treatment plan generation
    let plan = '';
    let mockPrescriptions = [];
    let followUp = '';
    let education = '';
    
    if (diagnosis.name.includes('Pneumonia')) {
      plan = `TREATMENT PLAN - ${diagnosis.name}

1. ANTIBIOTIC THERAPY
   Primary Treatment:
   • Amoxicillin-clavulanate 875mg PO BID x 7-10 days
   • Alternative: Azithromycin 500mg x 1 day, then 250mg daily x 4 days
   • Consider macrolide addition if atypical pneumonia suspected
   
   Duration & Monitoring:
   • 7-10 days based on clinical response
   • Reassess in 48-72 hours for treatment response
   • Switch to IV antibiotics if no improvement or deterioration

2. SUPPORTIVE CARE
   Symptom Management:
   • Rest and adequate hydration (2-3L daily unless contraindicated)
   • Antipyretics: Acetaminophen 500-1000mg q6h PRN for fever
   • Cough suppressants: Dextromethorphan 15-30mg q4h PRN
   • Supplemental oxygen if O2 saturation < 92%
   
   Respiratory Support:
   • Chest physiotherapy if productive cough
   • Incentive spirometry 10 breaths q1h while awake
   • Elevate head of bed 30-45 degrees

3. MONITORING PARAMETERS
   Clinical Assessment:
   • Daily temperature monitoring
   • Respiratory status (rate, effort, O2 saturation)
   • Watch for signs of clinical deterioration
   • Monitor for medication side effects
   
   Red Flags Requiring Immediate Attention:
   • Worsening dyspnea or tachypnea
   • Persistent fever >72 hours on antibiotics
   • Confusion or altered mental status
   • Hypotension or signs of sepsis

4. ACTIVITY & LIFESTYLE
   • Gradual return to normal activities as tolerated
   • Avoid strenuous activities until fully recovered
   • Smoking cessation counseling if applicable
   • Adequate nutrition to support recovery`;
   
      mockPrescriptions = [
        {
          id: 1,
          medication: 'Amoxicillin-Clavulanate',
          dosage: '875mg',
          frequency: 'Twice daily',
          duration: '7 days',
          route: 'Oral',
          instructions: 'Take with food to minimize GI upset',
          quantity: '14 tablets',
          refills: 0
        },
        {
          id: 2,
          medication: 'Acetaminophen',
          dosage: '500mg',
          frequency: 'Every 6 hours as needed',
          duration: 'As needed for fever',
          route: 'Oral',
          instructions: 'Maximum 4g daily. Do not exceed recommended dose.',
          quantity: '30 tablets',
          refills: 1
        },
        {
          id: 3,
          medication: 'Guaifenesin',
          dosage: '400mg',
          frequency: 'Every 4 hours as needed',
          duration: 'As needed for cough',
          route: 'Oral',
          instructions: 'Take with full glass of water',
          quantity: '30 tablets',
          refills: 1
        }
      ];
      
      followUp = `FOLLOW-UP RECOMMENDATIONS

1. SCHEDULED FOLLOW-UP
   • Phone check-in: 48-72 hours to assess treatment response
   • Office visit: 1 week if not improving or sooner if worsening
   • Chest X-ray: 4-6 weeks to ensure radiographic resolution
   
2. LABORATORY MONITORING
   • No routine labs needed for uncomplicated cases
   • Consider repeat CBC if no clinical improvement
   • Blood cultures if signs of sepsis develop
   
3. PREVENTIVE CARE
   • Pneumococcal vaccine when recovered (if not previously vaccinated)
   • Annual influenza vaccination
   • COVID-19 vaccination status review
   
4. RETURN PRECAUTIONS
   Patient should return immediately if experiencing:
   • Worsening shortness of breath
   • Chest pain
   • Persistent high fever (>103°F)
   • Coughing up blood
   • Confusion or lethargy`;
      
      education = `PATIENT EDUCATION

UNDERSTANDING YOUR DIAGNOSIS
${diagnosis.name} is an infection of the lungs that causes inflammation in the air sacs (alveoli). This can make breathing difficult and cause the symptoms you're experiencing.

MEDICATION INSTRUCTIONS
• Take antibiotics exactly as prescribed, even if feeling better
• Complete the entire course to prevent resistance
• Take with food if stomach upset occurs
• Avoid alcohol while on antibiotics

SELF-CARE AT HOME
• Rest is crucial for recovery - aim for 8+ hours of sleep
• Stay hydrated - drink 8-10 glasses of water daily
• Use a humidifier to ease breathing
• Practice deep breathing exercises hourly while awake

ACTIVITY GUIDELINES
• Avoid strenuous activities until fever resolves
• Gradually increase activity as energy improves
• Return to work/school when fever-free for 24 hours

PREVENTING SPREAD
• Cover coughs and sneezes
• Wash hands frequently
• Avoid close contact with others until no longer contagious
• Dispose of tissues properly

WHEN TO SEEK IMMEDIATE CARE
Go to the emergency room if you experience:
• Severe difficulty breathing
• Chest pain that worsens with breathing
• Coughing up large amounts of blood
• Blue lips or fingernails
• Confusion or difficulty staying awake`;
    } else {
      // Generic treatment plan for other diagnoses
      plan = `TREATMENT PLAN - ${diagnosis.name}

1. PRIMARY TREATMENT
   • Specific interventions based on diagnosis
   • Medication regimen as indicated
   • Supportive care measures

2. SYMPTOM MANAGEMENT
   • Address specific symptoms
   • Pain management if needed
   • Comfort measures

3. MONITORING
   • Track symptom progression
   • Monitor treatment response
   • Watch for complications

4. LIFESTYLE MODIFICATIONS
   • Activity recommendations
   • Dietary considerations
   • Risk factor modification`;
      
      followUp = `FOLLOW-UP RECOMMENDATIONS

1. SCHEDULED FOLLOW-UP
   • As clinically indicated
   • Based on symptom progression

2. MONITORING PARAMETERS
   • Relevant to specific condition
   • Treatment response indicators

3. PREVENTIVE MEASURES
   • Condition-specific prevention
   • General health maintenance`;
      
      education = `PATIENT EDUCATION

UNDERSTANDING YOUR CONDITION
Information about ${diagnosis.name} and its implications for your health.

TREATMENT EXPECTATIONS
What to expect during treatment and recovery.

SELF-CARE RECOMMENDATIONS
How to manage your condition at home.

WARNING SIGNS
When to seek additional medical care.`;
    }
    
    setTreatmentPlan(plan);
    setPrescriptions(mockPrescriptions);
    setFollowUpRecommendations(followUp);
    setPatientEducation(education);
    
    updatePatientData('treatmentPlan', plan);
    updatePatientData('prescriptions', mockPrescriptions);
    updatePatientData('followUpRecommendations', followUp);
    updatePatientData('patientEducation', education);
    
    setIsGeneratingPlan(false);
  };
  
  const handleContinue = () => {
    // Save all treatment data
    updatePatientData('treatmentPlan', treatmentPlan);
    updatePatientData('prescriptions', prescriptions);
    updatePatientData('followUpRecommendations', followUpRecommendations);
    updatePatientData('patientEducation', patientEducation);
    
    // Navigate to clinical summary
    setCurrentStep('clinical-summary');
  };
  
  const handleBack = () => {
    setCurrentStep('final-diagnosis');
  };
  
  const addPrescription = () => {
    const newPrescription = {
      id: Date.now(),
      medication: '',
      dosage: '',
      frequency: '',
      duration: '',
      route: 'Oral',
      instructions: '',
      quantity: '',
      refills: 0
    };
    setPrescriptions([...prescriptions, newPrescription]);
    setEditingPrescriptionId(newPrescription.id);
  };
  
  const startEditPrescription = (prescription) => {
    setEditingPrescriptionId(prescription.id);
    setTempPrescription({ ...prescription });
  };
  
  const savePrescription = () => {
    if (tempPrescription) {
      setPrescriptions(prescriptions.map(p => 
        p.id === tempPrescription.id ? tempPrescription : p
      ));
      updatePatientData('prescriptions', prescriptions.map(p => 
        p.id === tempPrescription.id ? tempPrescription : p
      ));
    }
    setEditingPrescriptionId(null);
    setTempPrescription(null);
  };
  
  const cancelEdit = () => {
    // If it's a new prescription with no data, remove it
    if (editingPrescriptionId && prescriptions.find(p => p.id === editingPrescriptionId && !p.medication)) {
      setPrescriptions(prescriptions.filter(p => p.id !== editingPrescriptionId));
    }
    setEditingPrescriptionId(null);
    setTempPrescription(null);
  };
  
  const updateTempPrescription = (field, value) => {
    setTempPrescription(prev => ({ ...prev, [field]: value }));
  };
  
  const removePrescription = (id) => {
    setPrescriptions(prescriptions.filter(p => p.id !== id));
    updatePatientData('prescriptions', prescriptions.filter(p => p.id !== id));
  };
  
  const renderPrescriptionPreview = (prescription, index) => (
    <div key={prescription.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-blue-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-white p-2 rounded-lg shadow-sm">
              <Pill className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">{prescription.medication || 'Unnamed Medication'}</h4>
              <p className="text-sm text-gray-600">Prescription #{index + 1}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => startEditPrescription(prescription)}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-white rounded-lg transition-all"
              title="Edit prescription"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => removePrescription(prescription.id)}
              className="p-2 text-gray-600 hover:text-red-600 hover:bg-white rounded-lg transition-all"
              title="Delete prescription"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Dosage</p>
            <p className="text-sm font-medium text-gray-900">{prescription.dosage || '-'}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Frequency</p>
            <p className="text-sm font-medium text-gray-900">{prescription.frequency || '-'}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Duration</p>
            <p className="text-sm font-medium text-gray-900">{prescription.duration || '-'}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Route</p>
            <p className="text-sm font-medium text-gray-900">{prescription.route}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Quantity</p>
            <p className="text-sm font-medium text-gray-900">{prescription.quantity || '-'}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Refills</p>
            <p className="text-sm font-medium text-gray-900">{prescription.refills || 0}</p>
          </div>
        </div>
        
        {prescription.instructions && (
          <div className="pt-4 border-t border-gray-100">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Special Instructions</p>
            <p className="text-sm text-gray-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              <AlertCircle className="inline w-4 h-4 text-amber-600 mr-2" />
              {prescription.instructions}
            </p>
          </div>
        )}
      </div>
    </div>
  );
  
  const renderPrescriptionEdit = (prescription, index) => {
    const currentPrescription = tempPrescription || prescription;
    
    return (
      <div key={prescription.id} className="bg-white rounded-xl shadow-sm border-2 border-blue-300 p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-medium text-gray-900">
            {prescription.medication ? `Editing: ${prescription.medication}` : 'New Prescription'}
          </h4>
          <div className="flex items-center space-x-2">
            <button
              onClick={savePrescription}
              className="flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Check className="w-4 h-4 mr-1" />
              Save
            </button>
            <button
              onClick={cancelEdit}
              className="flex items-center px-3 py-1.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <X className="w-4 h-4 mr-1" />
              Cancel
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medication Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={currentPrescription.medication}
              onChange={(e) => updateTempPrescription('medication', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Amoxicillin"
              autoFocus
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dosage <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={currentPrescription.dosage}
              onChange={(e) => updateTempPrescription('dosage', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 500mg"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Frequency <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={currentPrescription.frequency}
              onChange={(e) => updateTempPrescription('frequency', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Twice daily"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration
            </label>
            <input
              type="text"
              value={currentPrescription.duration}
              onChange={(e) => updateTempPrescription('duration', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 7 days"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Route
            </label>
            <select
              value={currentPrescription.route}
              onChange={(e) => updateTempPrescription('route', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="Oral">Oral</option>
              <option value="IV">Intravenous</option>
              <option value="IM">Intramuscular</option>
              <option value="Topical">Topical</option>
              <option value="Inhaled">Inhaled</option>
              <option value="Subcutaneous">Subcutaneous</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              type="text"
              value={currentPrescription.quantity}
              onChange={(e) => updateTempPrescription('quantity', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., 30 tablets"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Refills
            </label>
            <input
              type="number"
              value={currentPrescription.refills}
              onChange={(e) => updateTempPrescription('refills', parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min="0"
              max="12"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Special Instructions
            </label>
            <textarea
              value={currentPrescription.instructions}
              onChange={(e) => updateTempPrescription('instructions', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Take with food to minimize stomach upset"
              rows={2}
            />
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold text-gray-900">Treatment Plan</h2>
          <div className="flex items-center space-x-2">
            <Heart className="w-6 h-6 text-red-500" />
            <span className="text-sm text-gray-600">Personalized Care Planning</span>
          </div>
        </div>
        <p className="text-gray-600">
          Develop a comprehensive treatment strategy based on the diagnosis
        </p>
      </div>
      
      {/* Patient & Diagnosis Summary */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-1">
              <User className="w-4 h-4 text-green-600 mr-2" />
              <span className="font-medium text-green-900">{patientData.name}</span>
              <span className="text-green-700 ml-2">{patientData.age} years • {patientData.gender}</span>
            </div>
            <div className="flex items-center">
              <Stethoscope className="w-4 h-4 text-green-600 mr-2" />
              <p className="text-green-800">
                Diagnosis: <span className="font-medium">{patientData.selectedDiagnosis?.name || patientData.finalDiagnosis}</span>
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center text-sm text-green-700">
              <Calendar className="w-4 h-4 mr-1" />
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Generation Status */}
      {isGeneratingPlan && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
          <div className="flex items-center">
            <div className="relative mr-4">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
              <Sparkles className="absolute inset-0 m-auto w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-blue-900 font-medium">Generating personalized treatment plan...</p>
              <p className="text-blue-700 text-sm">Creating evidence-based recommendations</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedTab('treatment')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedTab === 'treatment'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText className="w-4 h-4 mr-2" />
          Treatment Plan
        </button>
        <button
          onClick={() => setSelectedTab('prescriptions')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedTab === 'prescriptions'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Pill className="w-4 h-4 mr-2" />
          Prescriptions
          {prescriptions.length > 0 && (
            <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-0.5 rounded-full">
              {prescriptions.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setSelectedTab('followup')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedTab === 'followup'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Calendar className="w-4 h-4 mr-2" />
          Follow-up
        </button>
        <button
          onClick={() => setSelectedTab('education')}
          className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg font-medium transition-all ${
            selectedTab === 'education'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Brain className="w-4 h-4 mr-2" />
          Patient Education
        </button>
      </div>
      
      {/* Main Content */}
      <div className="mb-6">
        {selectedTab === 'treatment' ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Treatment Recommendations</h3>
              <button
                onClick={generateTreatmentPlan}
                className="flex items-center space-x-1 px-3 py-1.5 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Regenerate</span>
              </button>
            </div>
            <textarea
              value={treatmentPlan}
              onChange={(e) => {
                setTreatmentPlan(e.target.value);
                updatePatientData('treatmentPlan', e.target.value);
              }}
              rows={20}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Treatment plan will be generated based on the diagnosis..."
            />
          </div>
        ) : selectedTab === 'prescriptions' ? (
          <div className="space-y-4">
            {prescriptions.map((prescription, index) => 
              editingPrescriptionId === prescription.id
                ? renderPrescriptionEdit(prescription, index)
                : renderPrescriptionPreview(prescription, index)
            )}
            
            <button
              onClick={addPrescription}
              className="w-full p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all flex items-center justify-center text-gray-600 hover:text-gray-800 group"
            >
              <Plus className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
              <span className="font-medium">Add Prescription</span>
            </button>
          </div>
        ) : selectedTab === 'followup' ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Follow-up Recommendations</h3>
            <textarea
              value={followUpRecommendations}
              onChange={(e) => {
                setFollowUpRecommendations(e.target.value);
                updatePatientData('followUpRecommendations', e.target.value);
              }}
              rows={15}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Enter follow-up recommendations..."
            />
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Patient Education Materials</h3>
            <textarea
              value={patientEducation}
              onChange={(e) => {
                setPatientEducation(e.target.value);
                updatePatientData('patientEducation', e.target.value);
              }}
              rows={15}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              placeholder="Enter patient education information..."
            />
          </div>
        )}
      </div>
      
      {/* Information Note */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
        <div className="flex items-start">
          <Info className="w-5 h-5 text-amber-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-900 mb-1">Important Reminder</p>
            <p className="text-sm text-amber-800">
              Ensure all treatment recommendations are evidence-based and appropriate for the patient's 
              specific condition, comorbidities, and medication history. Always verify drug interactions 
              and contraindications before finalizing prescriptions.
            </p>
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">
              {prescriptions.length} prescription{prescriptions.length !== 1 ? 's' : ''} added
            </span>
          </div>
          
          <button
            onClick={handleContinue}
            className="flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors group"
          >
            Continue to Clinical Summary
            <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back to Final Diagnosis
        </button>
      </div>
    </div>
  );
};

export default TreatmentPlan;