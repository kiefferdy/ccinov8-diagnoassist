import React, { useState } from 'react';
import { 
  X, Calendar, Clock, User, FileText, 
  Activity, Building, AlertCircle 
} from 'lucide-react';

const NewAppointmentModal = ({ patients, episodes, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    patientId: '',
    date: new Date().toISOString().split('T')[0],
    time: '09:00',
    duration: 30,
    type: 'consultation',
    reason: '',
    episodeId: '',
    room: '',
    notes: '',
    status: 'scheduled'
  });

  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.patientId) newErrors.patientId = 'Please select a patient';
    if (!formData.date) newErrors.date = 'Please select a date';
    if (!formData.time) newErrors.time = 'Please select a time';
    if (!formData.reason) newErrors.reason = 'Please enter a reason for visit';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      const appointmentData = {
        ...formData,
        date: new Date(`${formData.date}T${formData.time}`).toISOString(),
        patientName: patients.find(p => p.id === formData.patientId)?.demographics.name || ''
      };
      onSave(appointmentData);
    }
  };

  const selectedPatient = patients.find(p => p.id === formData.patientId);
  const patientEpisodes = selectedPatient ? 
    episodes.filter(e => e.patientId === selectedPatient.id && e.status === 'open') : [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Schedule New Appointment</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Patient Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.patientId}
              onChange={(e) => setFormData({ ...formData, patientId: e.target.value, episodeId: '' })}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.patientId ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select a patient</option>
              {patients.map(patient => (
                <option key={patient.id} value={patient.id}>
                  {patient.demographics.name} - {patient.demographics.dateOfBirth}
                </option>
              ))}
            </select>
            {errors.patientId && (
              <p className="text-red-500 text-sm mt-1">{errors.patientId}</p>
            )}
          </div>

          {/* Episode Selection (if applicable) */}
          {patientEpisodes.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Related Episode (Optional)
              </label>
              <select
                value={formData.episodeId}
                onChange={(e) => setFormData({ ...formData, episodeId: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No related episode</option>
                {patientEpisodes.map(episode => (
                  <option key={episode.id} value={episode.id}>
                    {episode.chiefComplaint} - Started {new Date(episode.startDate).toLocaleDateString()}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.date && (
                <p className="text-red-500 text-sm mt-1">{errors.date}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time <span className="text-red-500">*</span>
              </label>
              <input
                type="time"
                value={formData.time}
                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.time ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.time && (
                <p className="text-red-500 text-sm mt-1">{errors.time}</p>
              )}
            </div>
          </div>

          {/* Duration and Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration
              </label>
              <select
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={45}>45 minutes</option>
                <option value={60}>1 hour</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Appointment Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="consultation">Consultation</option>
                <option value="follow-up">Follow-up</option>
                <option value="procedure">Procedure</option>
                <option value="check-up">Check-up</option>
              </select>
            </div>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Visit <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              placeholder="e.g., Annual physical examination"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.reason ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.reason && (
              <p className="text-red-500 text-sm mt-1">{errors.reason}</p>
            )}
          </div>

          {/* Room */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Room Assignment
            </label>
            <input
              type="text"
              value={formData.room}
              onChange={(e) => setFormData({ ...formData, room: e.target.value })}
              placeholder="e.g., Room 101"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              placeholder="Any special instructions or notes..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
            >
              Schedule Appointment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAppointmentModal;