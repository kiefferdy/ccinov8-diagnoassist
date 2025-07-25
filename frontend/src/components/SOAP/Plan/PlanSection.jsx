import React, { useState } from 'react';
import { 
  ClipboardList, Pill, Calendar, UserPlus, BookOpen, Plus, X, 
  Activity, AlertCircle, Clock, Send, FileText, Heart,
  Shield, Info, CheckCircle, Download, Printer, ChevronRight,
  Sparkles, Search, Star, Zap, Package, AlertTriangle,
  Phone, MapPin, Globe, MessageSquare, Video, User, Stethoscope
} from 'lucide-react';
import { generateId } from '../../../utils/storage';

const PlanSection = ({ data, patient, episode, encounter, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('medications');
  const [showAddModal, setShowAddModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [newItem, setNewItem] = useState({});
  const [prescriptionView, setPrescriptionView] = useState(false);
  
  const tabs = [
    { id: 'medications', label: 'Medications', icon: Pill, color: 'blue' },
    { id: 'procedures', label: 'Procedures', icon: Activity, color: 'purple' },
    { id: 'referrals', label: 'Referrals', icon: UserPlus, color: 'green' },
    { id: 'followup', label: 'Follow-up', icon: Calendar, color: 'orange' },
    { id: 'education', label: 'Education', icon: BookOpen, color: 'pink' },
    { id: 'restrictions', label: 'Activity & Diet', icon: Shield, color: 'red' }
  ];
  
  // Common medications database
  const commonMedications = {
    'Pain': [
      { name: 'Ibuprofen', dosage: '400-800mg', frequency: 'q6-8h PRN', duration: '5-7 days' },
      { name: 'Acetaminophen', dosage: '500-1000mg', frequency: 'q6h PRN', duration: 'As needed' },
      { name: 'Naproxen', dosage: '250-500mg', frequency: 'BID', duration: '7-10 days' }
    ],
    'Antibiotics': [
      { name: 'Amoxicillin', dosage: '500mg', frequency: 'TID', duration: '7-10 days' },
      { name: 'Azithromycin', dosage: '250mg', frequency: 'QD', duration: '5 days' },
      { name: 'Cephalexin', dosage: '500mg', frequency: 'QID', duration: '7 days' }
    ],
    'Cardiovascular': [
      { name: 'Aspirin', dosage: '81mg', frequency: 'QD', duration: 'Ongoing' },
      { name: 'Lisinopril', dosage: '10mg', frequency: 'QD', duration: 'Ongoing' },
      { name: 'Metoprolol', dosage: '25mg', frequency: 'BID', duration: 'Ongoing' }
    ],
    'GI': [
      { name: 'Omeprazole', dosage: '20mg', frequency: 'QD', duration: '4-8 weeks' },
      { name: 'Ondansetron', dosage: '4mg', frequency: 'q8h PRN', duration: 'As needed' },
      { name: 'Docusate', dosage: '100mg', frequency: 'BID', duration: 'As needed' }
    ]
  };
  
  // Common referral specialties
  const referralSpecialties = [
    { specialty: 'Cardiology', common: ['chest pain', 'hypertension', 'arrhythmia'] },
    { specialty: 'Gastroenterology', common: ['GERD', 'IBD', 'liver disease'] },
    { specialty: 'Orthopedics', common: ['fracture', 'joint pain', 'sports injury'] },
    { specialty: 'Neurology', common: ['headache', 'seizure', 'neuropathy'] },
    { specialty: 'Endocrinology', common: ['diabetes', 'thyroid', 'hormone'] },
    { specialty: 'Pulmonology', common: ['asthma', 'COPD', 'sleep apnea'] },
    { specialty: 'Psychiatry', common: ['depression', 'anxiety', 'bipolar'] },
    { specialty: 'Physical Therapy', common: ['rehab', 'pain', 'mobility'] }
  ];
  
  const handleAddMedication = () => {
    if (!newItem.name?.trim()) return;
    
    const medication = {
      id: generateId('MED'),
      name: newItem.name,
      dosage: newItem.dosage || '',
      frequency: newItem.frequency || '',
      duration: newItem.duration || '',
      instructions: newItem.instructions || '',
      prescribed: true
    };
    
    onUpdate({
      medications: [...(data.medications || []), medication]
    });
    
    setNewItem({});
    setShowAddModal(false);
  };
  
  const handleAddProcedure = () => {
    if (!newItem.procedure?.trim()) return;
    
    const procedure = {
      id: generateId('PROC'),
      procedure: newItem.procedure,
      urgency: newItem.urgency || 'routine',
      notes: newItem.notes || '',
      scheduled: false
    };
    
    onUpdate({
      procedures: [...(data.procedures || []), procedure]
    });
    
    setNewItem({});
    setShowAddModal(false);
  };
  
  const handleAddReferral = () => {
    if (!newItem.specialty?.trim()) return;
    
    const referral = {
      id: generateId('REF'),
      specialty: newItem.specialty,
      provider: newItem.provider || '',
      reason: newItem.reason || '',
      urgency: newItem.urgency || 'routine',
      sent: false
    };
    
    onUpdate({
      referrals: [...(data.referrals || []), referral]
    });
    
    setNewItem({});
    setShowAddModal(false);
  };
  
  const handleAddEducation = () => {
    if (!newItem.topic?.trim()) return;
    
    const education = {
      topic: newItem.topic,
      materials: newItem.materials || '',
      discussed: true
    };
    
    onUpdate({
      patientEducation: [...(data.patientEducation || []), education]
    });
    
    setNewItem({});
    setShowAddModal(false);
  };
  
  const handleRemoveItem = (type, id) => {
    const updates = {};
    
    switch (type) {
      case 'medication':
        updates.medications = data.medications.filter(m => m.id !== id);
        break;
      case 'procedure':
        updates.procedures = data.procedures.filter(p => p.id !== id);
        break;
      case 'referral':
        updates.referrals = data.referrals.filter(r => r.id !== id);
        break;
      case 'education':
        updates.patientEducation = data.patientEducation.filter((e, idx) => idx !== id);
        break;
    }
    
    onUpdate(updates);
  };
  
  const handleFollowUpUpdate = (field, value) => {
    onUpdate({
      followUp: {
        ...data.followUp,
        [field]: value
      }
    });
  };
  
  const handleActivityUpdate = (value) => {
    onUpdate({ activityRestrictions: value });
  };
  
  const handleDietUpdate = (value) => {
    onUpdate({ dietRecommendations: value });
  };
  
  const openAddModal = (type) => {
    setModalType(type);
    setNewItem({});
    setShowAddModal(true);
  };
  
  const handleAIInsight = (insight) => {
    if (insight.type === 'template' && insight.section === 'plan') {
      // Apply treatment template
      // Implementation depends on the specific format
    }
  };
  
  // Calculate completion for tabs
  const calculateTabCompletion = (tabId) => {
    switch (tabId) {
      case 'medications':
        return (data.medications?.length || 0) > 0 ? 'partial' : 'empty';
      case 'procedures':
        return (data.procedures?.length || 0) > 0 ? 'partial' : 'empty';
      case 'referrals':
        return (data.referrals?.length || 0) > 0 ? 'partial' : 'empty';
      case 'followup':
        return data.followUp?.timeframe ? 'complete' : 'empty';
      case 'education':
        return (data.patientEducation?.length || 0) > 0 ? 'partial' : 'empty';
      case 'restrictions':
        return data.activityRestrictions || data.dietRecommendations ? 'partial' : 'empty';
      default:
        return 'empty';
    }
  };
  
  const getCompletionIcon = (status) => {
    switch (status) {
      case 'complete':
        return <div className="w-2 h-2 bg-green-500 rounded-full" />;
      case 'partial':
        return <div className="w-2 h-2 bg-yellow-500 rounded-full" />;
      default:
        return <div className="w-2 h-2 bg-gray-300 rounded-full" />;
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Plan Overview */}
      <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-2xl shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2 flex items-center">
              <ClipboardList className="w-6 h-6 mr-2" />
              Treatment Plan
            </h3>
            <p className="text-green-100">
              Comprehensive care plan and patient instructions
            </p>
          </div>
          <div className="flex gap-3">
            <button className="p-3 bg-white/20 rounded-lg backdrop-blur-sm hover:bg-white/30 transition-colors">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-3 bg-white/20 rounded-lg backdrop-blur-sm hover:bg-white/30 transition-colors">
              <Printer className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Quick Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Pill className="w-5 h-5 mb-1" />
            <div className="text-2xl font-bold">{data.medications?.length || 0}</div>
            <div className="text-sm text-green-200">Medications</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Activity className="w-5 h-5 mb-1" />
            <div className="text-2xl font-bold">{data.procedures?.length || 0}</div>
            <div className="text-sm text-green-200">Procedures</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <UserPlus className="w-5 h-5 mb-1" />
            <div className="text-2xl font-bold">{data.referrals?.length || 0}</div>
            <div className="text-sm text-green-200">Referrals</div>
          </div>
          <div className="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
            <Calendar className="w-5 h-5 mb-1" />
            <div className="text-2xl font-bold">{data.followUp?.timeframe || 'TBD'}</div>
            <div className="text-sm text-green-200">Follow-up</div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="border-b border-gray-200 bg-gray-50">
          <nav className="flex flex-wrap">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const completion = calculateTabCompletion(tab.id);
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center px-4 lg:px-6 py-4 text-sm font-medium 
                    border-b-3 transition-all duration-200 relative group
                    ${activeTab === tab.id
                      ? `text-${tab.color}-600 border-${tab.color}-600 bg-white`
                      : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">{tab.label}</span>
                  <div className="ml-2">
                    {getCompletionIcon(completion)}
                  </div>
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-green-500 to-teal-500" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-6">
          {/* Medications Tab */}
          {activeTab === 'medications' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Pill className="w-5 h-5 mr-2 text-blue-600" />
                    Medications
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Prescribe medications and provide instructions</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPrescriptionView(!prescriptionView)}
                    className="inline-flex items-center px-3 py-1.5 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    {prescriptionView ? 'List View' : 'Prescription View'}
                  </button>
                  <button
                    onClick={() => openAddModal('medication')}
                    className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Medication
                  </button>
                </div>
              </div>
              
              {data.medications?.length > 0 ? (
                prescriptionView ? (
                  <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                    <div className="text-center mb-6">
                      <h5 className="text-xl font-bold text-gray-900">Prescription</h5>
                      <p className="text-gray-600">{new Date().toLocaleDateString()}</p>
                    </div>
                    <div className="space-y-4">
                      {data.medications.map((med, idx) => (
                        <div key={med.id} className="border-b border-gray-300 pb-4 last:border-0">
                          <p className="font-semibold text-gray-900">
                            {idx + 1}. {med.name} {med.dosage}
                          </p>
                          <p className="text-gray-700 mt-1">
                            Sig: Take {med.frequency} {med.duration && `for ${med.duration}`}
                          </p>
                          {med.instructions && (
                            <p className="text-gray-600 text-sm mt-1 italic">{med.instructions}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.medications.map((med) => (
                      <div key={med.id} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-200 hover:border-blue-300 transition-all hover:shadow-md">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h5 className="font-semibold text-gray-900 text-lg flex items-center">
                              <Package className="w-4 h-4 mr-2 text-blue-600" />
                              {med.name}
                            </h5>
                            <div className="mt-3 space-y-2">
                              {med.dosage && (
                                <div className="flex items-center text-sm">
                                  <span className="text-gray-600 w-20">Dosage:</span>
                                  <span className="font-medium text-gray-800">{med.dosage}</span>
                                </div>
                              )}
                              {med.frequency && (
                                <div className="flex items-center text-sm">
                                  <span className="text-gray-600 w-20">Frequency:</span>
                                  <span className="font-medium text-gray-800">{med.frequency}</span>
                                </div>
                              )}
                              {med.duration && (
                                <div className="flex items-center text-sm">
                                  <span className="text-gray-600 w-20">Duration:</span>
                                  <span className="font-medium text-gray-800">{med.duration}</span>
                                </div>
                              )}
                            </div>
                            {med.instructions && (
                              <div className="mt-3 p-3 bg-white rounded-lg border border-blue-100">
                                <p className="text-sm text-gray-700">
                                  <span className="font-medium text-blue-700">Instructions:</span> {med.instructions}
                                </p>
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => handleRemoveItem('medication', med.id)}
                            className="ml-3 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-dashed border-blue-300">
                  <Pill className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                  <p className="text-gray-600 font-medium mb-4">No medications prescribed</p>
                  <button
                    onClick={() => openAddModal('medication')}
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Prescribe Medication
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Procedures Tab */}
          {activeTab === 'procedures' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-purple-600" />
                    Procedures & Orders
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Schedule procedures and medical orders</p>
                </div>
                <button
                  onClick={() => openAddModal('procedure')}
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-md hover:shadow-lg"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Procedure
                </button>
              </div>
              
              {data.procedures?.length > 0 ? (
                <div className="space-y-4">
                  {data.procedures.map((proc) => (
                    <div key={proc.id} className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-200 hover:border-purple-300 transition-all hover:shadow-md">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-900 text-lg">{proc.procedure}</h5>
                          <div className="mt-2 flex items-center gap-3">
                            <span className={`
                              inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border
                              ${proc.urgency === 'urgent' ? 'bg-orange-100 text-orange-700 border-orange-200' : 
                                proc.urgency === 'stat' ? 'bg-red-100 text-red-700 border-red-200' : 
                                'bg-gray-100 text-gray-700 border-gray-200'}
                            `}>
                              <Zap className="w-3 h-3 mr-1" />
                              {proc.urgency.toUpperCase()}
                            </span>
                            {proc.scheduled && (
                              <span className="inline-flex items-center text-green-700 text-sm">
                                <CheckCircle className="w-4 h-4 mr-1" />
                                Scheduled
                              </span>
                            )}
                          </div>
                          {proc.notes && (
                            <div className="mt-3 p-3 bg-white rounded-lg border border-purple-100">
                              <p className="text-sm text-gray-700">{proc.notes}</p>
                            </div>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemoveItem('procedure', proc.id)}
                          className="ml-3 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border-2 border-dashed border-purple-300">
                  <Activity className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                  <p className="text-gray-600 font-medium mb-4">No procedures scheduled</p>
                  <button
                    onClick={() => openAddModal('procedure')}
                    className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Procedure
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Referrals Tab */}
          {activeTab === 'referrals' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <UserPlus className="w-5 h-5 mr-2 text-green-600" />
                    Specialist Referrals
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Refer to specialists and coordinate care</p>
                </div>
                <button
                  onClick={() => openAddModal('referral')}
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition-all shadow-md hover:shadow-lg"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Referral
                </button>
              </div>
              
              {data.referrals?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.referrals.map((ref) => (
                    <div key={ref.id} className="bg-gradient-to-br from-green-50 to-teal-50 rounded-xl p-5 border border-green-200 hover:border-green-300 transition-all hover:shadow-md">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-900 text-lg flex items-center">
                            <Stethoscope className="w-4 h-4 mr-2 text-green-600" />
                            {ref.specialty}
                          </h5>
                          <div className="mt-3 space-y-2">
                            {ref.provider && (
                              <div className="flex items-center text-sm">
                                <User className="w-4 h-4 mr-2 text-gray-500" />
                                <span className="text-gray-700">{ref.provider}</span>
                              </div>
                            )}
                            {ref.reason && (
                              <div className="text-sm">
                                <span className="font-medium text-gray-700">Reason:</span>
                                <p className="text-gray-600 mt-1">{ref.reason}</p>
                              </div>
                            )}
                          </div>
                          <div className="mt-3 flex items-center gap-3">
                            <span className={`
                              inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border
                              ${ref.urgency === 'urgent' ? 'bg-orange-100 text-orange-700 border-orange-200' : 
                                'bg-gray-100 text-gray-700 border-gray-200'}
                            `}>
                              {ref.urgency.toUpperCase()}
                            </span>
                            {ref.sent ? (
                              <span className="inline-flex items-center text-green-700 text-sm">
                                <Send className="w-4 h-4 mr-1" />
                                Sent
                              </span>
                            ) : (
                              <button className="inline-flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium">
                                <Send className="w-4 h-4 mr-1" />
                                Send Referral
                              </button>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveItem('referral', ref.id)}
                          className="ml-3 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-green-50 to-teal-50 rounded-xl border-2 border-dashed border-green-300">
                  <UserPlus className="w-16 h-16 mx-auto mb-4 text-green-400" />
                  <p className="text-gray-600 font-medium mb-4">No referrals made</p>
                  <button
                    onClick={() => openAddModal('referral')}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Referral
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Follow-up Tab */}
          {activeTab === 'followup' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 flex items-center mb-4">
                  <Calendar className="w-5 h-5 mr-2 text-orange-600" />
                  Follow-up Planning
                </h4>
                
                <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-6 border border-orange-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Follow-up Timeframe
                      </label>
                      <select
                        value={data.followUp?.timeframe || ''}
                        onChange={(e) => handleFollowUpUpdate('timeframe', e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      >
                        <option value="">Select timeframe...</option>
                        <option value="24-48 hours">24-48 hours</option>
                        <option value="3-5 days">3-5 days</option>
                        <option value="1 week">1 week</option>
                        <option value="2 weeks">2 weeks</option>
                        <option value="1 month">1 month</option>
                        <option value="3 months">3 months</option>
                        <option value="6 months">6 months</option>
                        <option value="As needed">As needed</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Follow-up Type
                      </label>
                      <div className="grid grid-cols-2 gap-2">
                        {[
                          { type: 'In-person', icon: User },
                          { type: 'Telemedicine', icon: Video },
                          { type: 'Phone', icon: Phone },
                          { type: 'Message', icon: MessageSquare }
                        ].map((item) => (
                          <button
                            key={item.type}
                            onClick={() => handleFollowUpUpdate('type', item.type)}
                            className={`p-3 rounded-lg border-2 text-sm font-medium transition-all flex items-center justify-center ${
                              data.followUp?.type === item.type
                                ? 'bg-orange-100 border-orange-500 text-orange-700'
                                : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                            }`}
                          >
                            <item.icon className="w-4 h-4 mr-1" />
                            {item.type}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Follow-up Reason
                    </label>
                    <textarea
                      value={data.followUp?.reason || ''}
                      onChange={(e) => handleFollowUpUpdate('reason', e.target.value)}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                      placeholder="Reason for follow-up and what to monitor..."
                    />
                  </div>
                  
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Instructions for Follow-up
                    </label>
                    <textarea
                      value={data.followUp?.instructions || ''}
                      onChange={(e) => handleFollowUpUpdate('instructions', e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                      placeholder="What should the patient do before the follow-up visit..."
                    />
                  </div>
                  
                  {/* Red Flag Instructions */}
                  <div className="mt-6 p-4 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-sm font-medium text-red-800 mb-2 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-1" />
                      Return Immediately If:
                    </p>
                    <textarea
                      value={data.followUp?.redFlags || ''}
                      onChange={(e) => handleFollowUpUpdate('redFlags', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-red-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                      placeholder="List warning signs that require immediate medical attention..."
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Patient Education Tab */}
          {activeTab === 'education' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                    <BookOpen className="w-5 h-5 mr-2 text-pink-600" />
                    Patient Education
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">Educational materials and discussions</p>
                </div>
                <button
                  onClick={() => openAddModal('education')}
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-pink-600 to-purple-600 text-white rounded-lg hover:from-pink-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Education
                </button>
              </div>
              
              {data.patientEducation?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.patientEducation.map((edu, idx) => (
                    <div key={idx} className="bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl p-5 border border-pink-200 hover:border-pink-300 transition-all hover:shadow-md">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-900 flex items-center">
                            <Info className="w-4 h-4 mr-2 text-pink-600" />
                            {edu.topic}
                          </h5>
                          {edu.materials && (
                            <p className="text-sm text-gray-600 mt-2">{edu.materials}</p>
                          )}
                          <div className="mt-3">
                            {edu.discussed ? (
                              <span className="inline-flex items-center text-green-700 text-sm">
                                <CheckCircle className="w-4 h-4 mr-1" />
                                Discussed with patient
                              </span>
                            ) : (
                              <span className="text-gray-500 text-sm">Pending discussion</span>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveItem('education', idx)}
                          className="ml-3 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gradient-to-br from-pink-50 to-purple-50 rounded-xl border-2 border-dashed border-pink-300">
                  <BookOpen className="w-16 h-16 mx-auto mb-4 text-pink-400" />
                  <p className="text-gray-600 font-medium mb-4">No patient education documented</p>
                  <button
                    onClick={() => openAddModal('education')}
                    className="inline-flex items-center px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Education Topic
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Activity & Diet Tab */}
          {activeTab === 'restrictions' && (
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-red-600" />
                Activity & Dietary Recommendations
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
                  <h5 className="font-medium text-gray-900 mb-4 flex items-center">
                    <Activity className="w-4 h-4 mr-2 text-red-600" />
                    Activity Restrictions
                  </h5>
                  <textarea
                    value={data.activityRestrictions || ''}
                    onChange={(e) => handleActivityUpdate(e.target.value)}
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                    placeholder="Describe any activity restrictions or recommendations..."
                  />
                  <div className="mt-3 flex flex-wrap gap-2">
                    {['No restrictions', 'Light activity only', 'Bed rest', 'No lifting > 10 lbs', 'No driving'].map(template => (
                      <button
                        key={template}
                        onClick={() => handleActivityUpdate(template)}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                  <h5 className="font-medium text-gray-900 mb-4 flex items-center">
                    <Heart className="w-4 h-4 mr-2 text-green-600" />
                    Dietary Recommendations
                  </h5>
                  <textarea
                    value={data.dietRecommendations || ''}
                    onChange={(e) => handleDietUpdate(e.target.value)}
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                    placeholder="Describe any dietary modifications or recommendations..."
                  />
                  <div className="mt-3 flex flex-wrap gap-2">
                    {['Regular diet', 'Low sodium', 'Diabetic diet', 'Clear liquids', 'BRAT diet'].map(template => (
                      <button
                        key={template}
                        onClick={() => handleDietUpdate(template)}
                        className="px-3 py-1 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Add Item Modals */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className={`bg-gradient-to-r ${
              modalType === 'medication' ? 'from-blue-600 to-indigo-600' :
              modalType === 'procedure' ? 'from-purple-600 to-pink-600' :
              modalType === 'referral' ? 'from-green-600 to-teal-600' :
              'from-pink-600 to-purple-600'
            } text-white p-6`}>
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold">
                  Add {modalType.charAt(0).toUpperCase() + modalType.slice(1)}
                </h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
              {modalType === 'medication' && (
                <div className="space-y-6">
                  {/* Common Medications */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Common Medications
                    </label>
                    <div className="space-y-3">
                      {Object.entries(commonMedications).map(([category, meds]) => (
                        <div key={category} className="bg-gray-50 rounded-xl p-4">
                          <p className="text-sm font-medium text-gray-900 mb-2">{category}</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {meds.map((med, idx) => (
                              <button
                                key={idx}
                                onClick={() => setNewItem(med)}
                                className="text-left px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                              >
                                <p className="font-medium text-gray-900 text-sm">{med.name}</p>
                                <p className="text-xs text-gray-600">{med.dosage} - {med.frequency}</p>
                              </button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Medication Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.name || ''}
                      onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Amoxicillin"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dosage</label>
                      <input
                        type="text"
                        value={newItem.dosage || ''}
                        onChange={(e) => setNewItem({ ...newItem, dosage: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., 500mg"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                      <input
                        type="text"
                        value={newItem.frequency || ''}
                        onChange={(e) => setNewItem({ ...newItem, frequency: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., TID"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                      <input
                        type="text"
                        value={newItem.duration || ''}
                        onChange={(e) => setNewItem({ ...newItem, duration: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., 7 days"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Special Instructions
                    </label>
                    <textarea
                      value={newItem.instructions || ''}
                      onChange={(e) => setNewItem({ ...newItem, instructions: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="e.g., Take with food, avoid alcohol..."
                    />
                  </div>
                </div>
              )}
              
              {modalType === 'procedure' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Procedure Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.procedure || ''}
                      onChange={(e) => setNewItem({ ...newItem, procedure: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="e.g., MRI Brain, Blood work, X-ray..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Urgency</label>
                    <div className="grid grid-cols-3 gap-3">
                      {['routine', 'urgent', 'stat'].map(urgency => (
                        <button
                          key={urgency}
                          onClick={() => setNewItem({ ...newItem, urgency })}
                          className={`p-3 rounded-lg border-2 font-medium transition-all ${
                            newItem.urgency === urgency
                              ? urgency === 'stat' ? 'bg-red-100 border-red-500 text-red-700' :
                                urgency === 'urgent' ? 'bg-orange-100 border-orange-500 text-orange-700' :
                                'bg-gray-100 border-gray-500 text-gray-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {urgency.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                    <textarea
                      value={newItem.notes || ''}
                      onChange={(e) => setNewItem({ ...newItem, notes: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                      placeholder="Any special instructions or clinical context..."
                    />
                  </div>
                </div>
              )}
              
              {modalType === 'referral' && (
                <div className="space-y-6">
                  {/* Quick Specialty Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Common Specialties
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {referralSpecialties.map(({ specialty }) => (
                        <button
                          key={specialty}
                          onClick={() => setNewItem({ ...newItem, specialty })}
                          className={`px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all ${
                            newItem.specialty === specialty
                              ? 'bg-green-100 border-green-500 text-green-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {specialty}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Specialty <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.specialty || ''}
                      onChange={(e) => setNewItem({ ...newItem, specialty: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., Cardiology, Orthopedics..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Provider Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={newItem.provider || ''}
                      onChange={(e) => setNewItem({ ...newItem, provider: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Specific provider if known..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reason for Referral
                    </label>
                    <textarea
                      value={newItem.reason || ''}
                      onChange={(e) => setNewItem({ ...newItem, reason: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                      placeholder="Clinical reason for referral..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Urgency</label>
                    <div className="grid grid-cols-2 gap-3">
                      {['routine', 'urgent'].map(urgency => (
                        <button
                          key={urgency}
                          onClick={() => setNewItem({ ...newItem, urgency })}
                          className={`p-3 rounded-lg border-2 font-medium transition-all ${
                            newItem.urgency === urgency
                              ? urgency === 'urgent' ? 'bg-orange-100 border-orange-500 text-orange-700' :
                                'bg-gray-100 border-gray-500 text-gray-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {urgency.charAt(0).toUpperCase() + urgency.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              {modalType === 'education' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Education Topic <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.topic || ''}
                      onChange={(e) => setNewItem({ ...newItem, topic: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                      placeholder="e.g., Disease management, Medication use..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Materials Provided
                    </label>
                    <textarea
                      value={newItem.materials || ''}
                      onChange={(e) => setNewItem({ ...newItem, materials: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
                      placeholder="Handouts, websites, or other resources provided..."
                    />
                  </div>
                </div>
              )}
            </div>
            
            <div className="border-t border-gray-200 p-6 bg-gray-50">
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (modalType === 'medication') handleAddMedication();
                    else if (modalType === 'procedure') handleAddProcedure();
                    else if (modalType === 'referral') handleAddReferral();
                    else if (modalType === 'education') handleAddEducation();
                  }}
                  disabled={
                    (modalType === 'medication' && !newItem.name) ||
                    (modalType === 'procedure' && !newItem.procedure) ||
                    (modalType === 'referral' && !newItem.specialty) ||
                    (modalType === 'education' && !newItem.topic)
                  }
                  className="px-6 py-2.5 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  Add {modalType.charAt(0).toUpperCase() + modalType.slice(1)}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanSection;