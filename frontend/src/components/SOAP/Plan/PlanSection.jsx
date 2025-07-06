import React, { useState } from 'react';
import { ClipboardList, Pill, Calendar, UserPlus, BookOpen, Plus, X, Activity, AlertCircle } from 'lucide-react';
import { generateId } from '../../../utils/storage';

const PlanSection = ({ data, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('medications');
  const [showAddModal, setShowAddModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [newItem, setNewItem] = useState({});
  
  const tabs = [
    { id: 'medications', label: 'Medications', icon: Pill },
    { id: 'procedures', label: 'Procedures', icon: Activity },
    { id: 'referrals', label: 'Referrals', icon: UserPlus },
    { id: 'followup', label: 'Follow-up', icon: Calendar },
    { id: 'education', label: 'Patient Education', icon: BookOpen }
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
  
  const openAddModal = (type) => {
    setModalType(type);
    setNewItem({});
    setShowAddModal(true);
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex flex-wrap">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors
                    ${activeTab === tab.id
                      ? 'text-blue-600 border-blue-600'
                      : 'text-gray-500 border-transparent hover:text-gray-700'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
        <div className="p-6">
          {/* Medications Tab */}
          {activeTab === 'medications' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Medications</h4>
                <button
                  onClick={() => openAddModal('medication')}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Medication
                </button>
              </div>
              
              {data.medications?.length > 0 ? (
                <div className="space-y-3">
                  {data.medications.map((med) => (
                    <div key={med.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900">{med.name}</h5>
                          <div className="mt-1 space-y-1 text-sm text-gray-600">
                            {med.dosage && <p>Dosage: {med.dosage}</p>}
                            {med.frequency && <p>Frequency: {med.frequency}</p>}
                            {med.duration && <p>Duration: {med.duration}</p>}
                            {med.instructions && <p className="italic">Instructions: {med.instructions}</p>}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveItem('medication', med.id)}
                          className="text-gray-400 hover:text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Pill className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No medications prescribed</p>
                </div>
              )}
            </div>
          )}
          
          {/* Procedures Tab */}
          {activeTab === 'procedures' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Procedures</h4>
                <button
                  onClick={() => openAddModal('procedure')}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Procedure
                </button>
              </div>
              
              {data.procedures?.length > 0 ? (
                <div className="space-y-3">
                  {data.procedures.map((proc) => (
                    <div key={proc.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900">{proc.procedure}</h5>
                          <div className="mt-1 flex items-center gap-3 text-sm">
                            <span className={`
                              px-2 py-0.5 rounded-full text-xs font-medium
                              ${proc.urgency === 'urgent' ? 'bg-orange-100 text-orange-700' : 
                                proc.urgency === 'stat' ? 'bg-red-100 text-red-700' : 
                                'bg-gray-100 text-gray-700'}
                            `}>
                              {proc.urgency.toUpperCase()}
                            </span>
                            {proc.notes && <p className="text-gray-600">{proc.notes}</p>}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveItem('procedure', proc.id)}
                          className="text-gray-400 hover:text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No procedures scheduled</p>
                </div>
              )}
            </div>
          )}
          
          {/* Referrals Tab */}
          {activeTab === 'referrals' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Referrals</h4>
                <button
                  onClick={() => openAddModal('referral')}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Referral
                </button>
              </div>
              
              {data.referrals?.length > 0 ? (
                <div className="space-y-3">
                  {data.referrals.map((ref) => (
                    <div key={ref.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900">{ref.specialty}</h5>
                          <div className="mt-1 space-y-1 text-sm text-gray-600">
                            {ref.provider && <p>Provider: {ref.provider}</p>}
                            {ref.reason && <p>Reason: {ref.reason}</p>}
                            <span className={`
                              inline-block px-2 py-0.5 rounded-full text-xs font-medium
                              ${ref.urgency === 'urgent' ? 'bg-orange-100 text-orange-700' : 
                                'bg-gray-100 text-gray-700'}
                            `}>
                              {ref.urgency.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveItem('referral', ref.id)}
                          className="text-gray-400 hover:text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <UserPlus className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No referrals made</p>
                </div>
              )}
            </div>
          )}
          
          {/* Follow-up Tab */}
          {activeTab === 'followup' && (
            <div className="space-y-4">
              <h4 className="text-md font-medium text-gray-900 mb-4">Follow-up Plan</h4>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Follow-up Timeframe
                </label>
                <input
                  type="text"
                  value={data.followUp?.timeframe || ''}
                  onChange={(e) => handleFollowUpUpdate('timeframe', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1 week, 2-3 days, 1 month"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Follow-up
                </label>
                <textarea
                  value={data.followUp?.reason || ''}
                  onChange={(e) => handleFollowUpUpdate('reason', e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Re-evaluate symptoms, Review test results"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instructions for Patient
                </label>
                <textarea
                  value={data.followUp?.instructions || ''}
                  onChange={(e) => handleFollowUpUpdate('instructions', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Return sooner if symptoms worsen, Call if fever persists"
                />
              </div>
              
              {/* Activity and Diet Recommendations */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Activity Restrictions
                </label>
                <input
                  type="text"
                  value={data.activityRestrictions || ''}
                  onChange={(e) => onUpdate({ activityRestrictions: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Rest for 2 days, No heavy lifting"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diet Recommendations
                </label>
                <input
                  type="text"
                  value={data.dietRecommendations || ''}
                  onChange={(e) => onUpdate({ dietRecommendations: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Clear liquids, Low sodium diet"
                />
              </div>
            </div>
          )}
          
          {/* Patient Education Tab */}
          {activeTab === 'education' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">Patient Education</h4>
                <button
                  onClick={() => openAddModal('education')}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add Topic
                </button>
              </div>
              
              {data.patientEducation?.length > 0 ? (
                <div className="space-y-3">
                  {data.patientEducation.map((edu, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <h5 className="font-medium text-gray-900">{edu.topic}</h5>
                          {edu.materials && (
                            <p className="text-sm text-gray-600 mt-1">Materials: {edu.materials}</p>
                          )}
                          {edu.discussed && (
                            <span className="inline-flex items-center text-xs text-green-700 mt-2">
                              <AlertCircle className="w-3 h-3 mr-1" />
                              Discussed with patient
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemoveItem('education', index)}
                          className="text-gray-400 hover:text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BookOpen className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p>No education topics documented</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      {/* Add Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Add {modalType.charAt(0).toUpperCase() + modalType.slice(1)}
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Medication Fields */}
              {modalType === 'medication' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Medication Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.name || ''}
                      onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Amoxicillin"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Dosage</label>
                    <input
                      type="text"
                      value={newItem.dosage || ''}
                      onChange={(e) => setNewItem({ ...newItem, dosage: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., 500mg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                    <input
                      type="text"
                      value={newItem.frequency || ''}
                      onChange={(e) => setNewItem({ ...newItem, frequency: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Three times daily"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                    <input
                      type="text"
                      value={newItem.duration || ''}
                      onChange={(e) => setNewItem({ ...newItem, duration: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., 7 days"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
                    <textarea
                      value={newItem.instructions || ''}
                      onChange={(e) => setNewItem({ ...newItem, instructions: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Take with food"
                    />
                  </div>
                </>
              )}
              
              {/* Procedure Fields */}
              {modalType === 'procedure' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Procedure <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.procedure || ''}
                      onChange={(e) => setNewItem({ ...newItem, procedure: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., CT scan abdomen"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
                    <select
                      value={newItem.urgency || 'routine'}
                      onChange={(e) => setNewItem({ ...newItem, urgency: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="routine">Routine</option>
                      <option value="urgent">Urgent</option>
                      <option value="stat">STAT</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                    <textarea
                      value={newItem.notes || ''}
                      onChange={(e) => setNewItem({ ...newItem, notes: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Any special instructions..."
                    />
                  </div>
                </>
              )}
              
              {/* Referral Fields */}
              {modalType === 'referral' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Specialty <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.specialty || ''}
                      onChange={(e) => setNewItem({ ...newItem, specialty: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Cardiology"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                    <input
                      type="text"
                      value={newItem.provider || ''}
                      onChange={(e) => setNewItem({ ...newItem, provider: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Dr. Smith"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                    <textarea
                      value={newItem.reason || ''}
                      onChange={(e) => setNewItem({ ...newItem, reason: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Reason for referral..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
                    <select
                      value={newItem.urgency || 'routine'}
                      onChange={(e) => setNewItem({ ...newItem, urgency: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="routine">Routine</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                </>
              )}
              
              {/* Education Fields */}
              {modalType === 'education' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Topic <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={newItem.topic || ''}
                      onChange={(e) => setNewItem({ ...newItem, topic: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Diabetes management"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Materials Provided</label>
                    <input
                      type="text"
                      value={newItem.materials || ''}
                      onChange={(e) => setNewItem({ ...newItem, materials: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., Handout on diet, Website resources"
                    />
                  </div>
                </>
              )}
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  switch (modalType) {
                    case 'medication':
                      handleAddMedication();
                      break;
                    case 'procedure':
                      handleAddProcedure();
                      break;
                    case 'referral':
                      handleAddReferral();
                      break;
                    case 'education':
                      handleAddEducation();
                      break;
                  }
                }}
                disabled={
                  (modalType === 'medication' && !newItem.name?.trim()) ||
                  (modalType === 'procedure' && !newItem.procedure?.trim()) ||
                  (modalType === 'referral' && !newItem.specialty?.trim()) ||
                  (modalType === 'education' && !newItem.topic?.trim())
                }
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add {modalType.charAt(0).toUpperCase() + modalType.slice(1)}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanSection;