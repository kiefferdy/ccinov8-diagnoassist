import React, { useState } from 'react';
import { 
  X, Calendar, Clock, User, FileText, 
  Activity, Building, Edit2, Trash2, CheckCircle, XCircle 
} from 'lucide-react';

const AppointmentDetailsModal = ({ appointment, patient, episode, onUpdate, onDelete, onClose }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    status: appointment.status,
    room: appointment.room || '',
    notes: appointment.notes || ''
  });

  const handleUpdate = () => {
    onUpdate(editData);
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this appointment?')) {
      onDelete();
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'scheduled':
        return <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">Scheduled</span>;
      case 'confirmed':
        return <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Confirmed</span>;
      case 'completed':
        return <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">Completed</span>;
      case 'cancelled':
        return <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">Cancelled</span>;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900">Appointment Details</h2>
            {getStatusBadge(appointment.status)}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Patient Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <User className="w-5 h-5 text-gray-600" />
              Patient Information
            </h3>
            <div className="space-y-2">
              <p className="text-gray-700">
                <span className="font-medium">Name:</span> {appointment.patientName}
              </p>
              {patient && (
                <>
                  <p className="text-gray-700">
                    <span className="font-medium">Date of Birth:</span> {patient.demographics.dateOfBirth}
                  </p>
                  <p className="text-gray-700">
                    <span className="font-medium">Gender:</span> {patient.demographics.gender}
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Appointment Info */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Appointment Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-700">
                  <span className="font-medium">Date:</span> {new Date(appointment.date).toLocaleDateString()}
                </p>
                <p className="text-gray-700 mt-2">
                  <span className="font-medium">Time:</span> {appointment.time}
                </p>
                <p className="text-gray-700 mt-2">
                  <span className="font-medium">Duration:</span> {appointment.duration} minutes
                </p>
              </div>
              <div>
                <p className="text-gray-700">
                  <span className="font-medium">Type:</span> {appointment.type}
                </p>
                <p className="text-gray-700 mt-2">
                  <span className="font-medium">Reason:</span> {appointment.reason}
                </p>
                {isEditing ? (
                  <div className="mt-2">
                    <span className="font-medium text-gray-700">Room:</span>
                    <input
                      type="text"
                      value={editData.room}
                      onChange={(e) => setEditData({ ...editData, room: e.target.value })}
                      className="ml-2 px-2 py-1 border border-gray-300 rounded text-sm"
                      placeholder="Room number"
                    />
                  </div>
                ) : (
                  <p className="text-gray-700 mt-2">
                    <span className="font-medium">Room:</span> {appointment.room || 'TBA'}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Episode Info */}
          {episode && (
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Related Episode
              </h3>
              <p className="text-gray-700">
                <span className="font-medium">Chief Complaint:</span> {episode.chiefComplaint}
              </p>
              <p className="text-gray-700 mt-2">
                <span className="font-medium">Started:</span> {new Date(episode.startDate).toLocaleDateString()}
              </p>
            </div>
          )}

          {/* Notes */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-600" />
              Notes
            </h3>
            {isEditing ? (
              <textarea
                value={editData.notes}
                onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add notes..."
              />
            ) : (
              <p className="text-gray-700">{appointment.notes || 'No notes added'}</p>
            )}
          </div>

          {/* Status Update */}
          {isEditing && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Update Status</h3>
              <div className="flex gap-3">
                <button
                  onClick={() => setEditData({ ...editData, status: 'scheduled' })}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    editData.status === 'scheduled' 
                      ? 'border-blue-500 bg-blue-50 text-blue-700' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  Scheduled
                </button>
                <button
                  onClick={() => setEditData({ ...editData, status: 'confirmed' })}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    editData.status === 'confirmed' 
                      ? 'border-green-500 bg-green-50 text-green-700' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  Confirmed
                </button>
                <button
                  onClick={() => setEditData({ ...editData, status: 'completed' })}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    editData.status === 'completed' 
                      ? 'border-gray-500 bg-gray-50 text-gray-700' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  Completed
                </button>
                <button
                  onClick={() => setEditData({ ...editData, status: 'cancelled' })}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    editData.status === 'cancelled' 
                      ? 'border-red-500 bg-red-50 text-red-700' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  Cancelled
                </button>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between pt-4 border-t border-gray-200">
            <button
              onClick={handleDelete}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
            
            <div className="flex gap-3">
              {isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpdate}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Save Changes
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentDetailsModal;