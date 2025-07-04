// I'll create a new component for the editable sections

import React from 'react';
import { 
  Phone,
  Mail,
  MapPin,
  User,
  Calendar,
  Save,
  X,
  Users,
  UserCircle
} from 'lucide-react';

export const EditableContactSection = ({ 
  patient, 
  editData, 
  setEditData, 
  isEditing, 
  onSave, 
  onCancel 
}) => {
  if (!isEditing) {
    return (
      <div className="space-y-6">
        {/* Basic Information */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Basic Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start">
              <UserCircle className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Full Name</p>
                <p className="text-gray-900">{patient.name}</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <Calendar className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Date of Birth</p>
                <p className="text-gray-900">{new Date(patient.dateOfBirth).toLocaleDateString()}</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <Users className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Sex</p>
                <p className="text-gray-900">{patient.gender}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Contact Information */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Contact Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start">
              <Phone className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Phone</p>
                <p className="text-gray-900">{patient.phone || 'Not provided'}</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <Mail className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Email</p>
                <p className="text-gray-900">{patient.email || 'Not provided'}</p>
              </div>
            </div>
            
            <div className="flex items-start md:col-span-2">
              <MapPin className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Address</p>
                <p className="text-gray-900">{patient.address || 'Not provided'}</p>
              </div>
            </div>
            
            <div className="flex items-start md:col-span-2">
              <User className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Emergency Contact</p>
                <p className="text-gray-900">{patient.emergencyContact || 'Not provided'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Basic Information - Editable */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Basic Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <UserCircle className="w-4 h-4 inline mr-1" />
              Full Name
            </label>
            <input
              type="text"
              value={editData.name || ''}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter patient's full name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar className="w-4 h-4 inline mr-1" />
              Date of Birth
            </label>
            <input
              type="date"
              value={editData.dateOfBirth ? editData.dateOfBirth.split('T')[0] : ''}
              onChange={(e) => setEditData({ ...editData, dateOfBirth: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Users className="w-4 h-4 inline mr-1" />
              Sex
            </label>
            <select
              value={editData.gender || ''}
              onChange={(e) => setEditData({ ...editData, gender: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select sex</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Contact Information - Editable */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Contact Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Phone className="w-4 h-4 inline mr-1" />
              Phone
            </label>
            <input
              type="tel"
              value={editData.phone || ''}
              onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="(555) 123-4567"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Mail className="w-4 h-4 inline mr-1" />
              Email
            </label>
            <input
              type="email"
              value={editData.email || ''}
              onChange={(e) => setEditData({ ...editData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="patient@email.com"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <MapPin className="w-4 h-4 inline mr-1" />
              Address
            </label>
            <input
              type="text"
              value={editData.address || ''}
              onChange={(e) => setEditData({ ...editData, address: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="123 Main St, City, State ZIP"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <User className="w-4 h-4 inline mr-1" />
              Emergency Contact
            </label>
            <input
              type="text"
              value={editData.emergencyContact || ''}
              onChange={(e) => setEditData({ ...editData, emergencyContact: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Name - Phone Number"
            />
          </div>
        </div>
      </div>
      
      <div className="flex justify-end space-x-2 pt-4">
        <button
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </button>
        <button
          onClick={onSave}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </button>
      </div>
    </div>
  );
};