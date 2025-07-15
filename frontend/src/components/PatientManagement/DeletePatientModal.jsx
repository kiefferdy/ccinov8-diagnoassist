import React, { useState } from 'react';
import { X, AlertTriangle, Trash2 } from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useEpisode } from '../../contexts/EpisodeContext';
import { useEncounter } from '../../contexts/EncounterContext';

const DeletePatientModal = ({ patient, onClose, onDeleted }) => {
  const { deletePatient } = usePatient();
  const { deletePatientEpisodes } = useEpisode();
  const { deletePatientEncounters } = useEncounter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  
  const patientName = patient.demographics.name;
  const expectedConfirmText = `DELETE ${patientName}`;
  
  const handleDelete = async () => {
    if (confirmText !== expectedConfirmText) {
      if (window.showNotification) {
        window.showNotification('Please type the confirmation text exactly', 'error');
      }
      return;
    }
    
    setIsDeleting(true);
    
    try {
      // Delete all patient encounters
      deletePatientEncounters(patient.id);
      
      // Delete all patient episodes
      deletePatientEpisodes(patient.id);
      
      // Delete the patient
      deletePatient(patient.id);
      
      if (window.showNotification) {
        window.showNotification('Patient deleted successfully', 'success');
      }
      
      // Call the onDeleted callback to navigate away
      onDeleted();
      
    } catch (error) {
      console.error('Error deleting patient:', error);
      if (window.showNotification) {
        window.showNotification('Failed to delete patient', 'error');
      }
    } finally {
      setIsDeleting(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="bg-red-600 text-white px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <div className="flex items-center">
            <AlertTriangle className="w-6 h-6 mr-3" />
            <h2 className="text-xl font-bold">Delete Patient</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            disabled={isDeleting}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6">
          <div className="mb-6">
            <p className="text-gray-800 mb-4">
              Are you sure you want to delete <strong>{patientName}</strong>?
            </p>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800">
                <strong>Warning:</strong> This action cannot be undone. All patient data including:
              </p>
              <ul className="list-disc list-inside text-sm text-red-700 mt-2">
                <li>Patient demographics and medical history</li>
                <li>All episodes and clinical documentation</li>
                <li>All encounters and SOAP notes</li>
                <li>All attachments and files</li>
              </ul>
              <p className="text-sm text-red-800 mt-2">
                will be permanently deleted.
              </p>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To confirm deletion, type: <span className="font-mono bg-gray-100 px-2 py-1 rounded">{expectedConfirmText}</span>
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Type confirmation text"
              disabled={isDeleting}
            />
          </div>
          
          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={isDeleting}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting || confirmText !== expectedConfirmText}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isDeleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Patient
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeletePatientModal;