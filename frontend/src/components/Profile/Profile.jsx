import React, { useState, useEffect } from 'react';
import { 
  User, Mail, Phone, Building, Calendar, 
  Award, Globe, Camera, Save, Edit2, X,
  Stethoscope, GraduationCap, MapPin, Clock,
  Languages, Heart, Shield, CheckCircle
} from 'lucide-react';
import DashboardLayout from '../Layout/DashboardLayout';
import './profile-animations.css';

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [profileData, setProfileData] = useState({
    name: 'Dr. Sarah Chen',
    email: 'sarah.chen@diagnoassist.com',
    phone: '+1 (555) 123-4567',
    specialty: 'Internal Medicine',
    licenseNumber: 'MD123456',
    hospital: 'City General Hospital',
    department: 'Internal Medicine Department',
    yearsOfExperience: 12,
    education: 'Harvard Medical School, MD',
    languages: ['English', 'Mandarin', 'Spanish'],
    address: '123 Medical Center Drive, Suite 400, New York, NY 10001',
    bio: 'Dedicated internal medicine physician with over 12 years of experience in patient care, specializing in preventive medicine and chronic disease management.',
    availability: {
      monday: '9:00 AM - 5:00 PM',
      tuesday: '9:00 AM - 5:00 PM',
      wednesday: '9:00 AM - 5:00 PM',
      thursday: '9:00 AM - 5:00 PM',
      friday: '9:00 AM - 3:00 PM',
      saturday: 'Off',
      sunday: 'Off'
    }
  });

  const [editData, setEditData] = useState(profileData);

  // Load profile from localStorage
  useEffect(() => {
    const storedProfile = localStorage.getItem('doctor_profile');
    if (storedProfile) {
      const parsed = JSON.parse(storedProfile);
      setProfileData(parsed);
      setEditData(parsed);
    }
  }, []);

  const handleSave = () => {
    setProfileData(editData);
    localStorage.setItem('doctor_profile', JSON.stringify(editData));
    setIsEditing(false);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleCancel = () => {
    setEditData(profileData);
    setIsEditing(false);
  };

  const handleLanguageAdd = (e) => {
    if (e.key === 'Enter' && e.target.value.trim()) {
      setEditData({
        ...editData,
        languages: [...editData.languages, e.target.value.trim()]
      });
      e.target.value = '';
    }
  };

  const handleLanguageRemove = (index) => {
    setEditData({
      ...editData,
      languages: editData.languages.filter((_, i) => i !== index)
    });
  };
  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 animate-fadeIn">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Success Message */}
          {showSuccess && (
            <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg flex items-center animate-slideDown">
              <CheckCircle className="w-5 h-5 mr-2" />
              Profile updated successfully!
            </div>
          )}

          {/* Header */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Profile
                </button>
              ) : (
                <div className="flex gap-3">
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                </div>
              )}
            </div>

            {/* Profile Picture and Basic Info */}
            <div className="flex flex-col md:flex-row gap-8">
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-4xl font-bold shadow-lg">
                    {profileData.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  {isEditing && (
                    <button className="absolute bottom-0 right-0 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors">
                      <Camera className="w-5 h-5 text-gray-600" />
                    </button>
                  )}
                </div>
              </div>

              <div className="flex-1 space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editData.name}
                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <p className="text-lg font-medium text-gray-900">{profileData.name}</p>
                  )}
                </div>

                {/* Email and Phone */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Mail className="w-4 h-4 inline mr-1" />
                      Email
                    </label>
                    {isEditing ? (
                      <input
                        type="email"
                        value={editData.email}
                        onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    ) : (
                      <p className="text-gray-900">{profileData.email}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Phone className="w-4 h-4 inline mr-1" />
                      Phone
                    </label>
                    {isEditing ? (
                      <input
                        type="tel"
                        value={editData.phone}
                        onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    ) : (
                      <p className="text-gray-900">{profileData.phone}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Professional Information */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Stethoscope className="w-6 h-6 text-blue-600" />
              Professional Information
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Specialty</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.specialty}
                    onChange={(e) => setEditData({ ...editData, specialty: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.specialty}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">License Number</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.licenseNumber}
                    onChange={(e) => setEditData({ ...editData, licenseNumber: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.licenseNumber}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Hospital/Clinic</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.hospital}
                    onChange={(e) => setEditData({ ...editData, hospital: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.hospital}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
                {isEditing ? (
                  <input
                    type="number"
                    value={editData.yearsOfExperience}
                    onChange={(e) => setEditData({ ...editData, yearsOfExperience: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.yearsOfExperience} years</p>
                )}
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">Education</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.education}
                  onChange={(e) => setEditData({ ...editData, education: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <p className="text-gray-900">{profileData.education}</p>
              )}
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">Professional Bio</label>
              {isEditing ? (
                <textarea
                  value={editData.bio}
                  onChange={(e) => setEditData({ ...editData, bio: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <p className="text-gray-900">{profileData.bio}</p>
              )}
            </div>
          </div>

          {/* Additional Information */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
              <Globe className="w-6 h-6 text-purple-600" />
              Additional Information
            </h2>

            {/* Languages */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Languages className="w-4 h-4 inline mr-1" />
                Languages Spoken
              </label>
              <div className="flex flex-wrap gap-2">
                {(isEditing ? editData : profileData).languages.map((lang, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium flex items-center gap-1"
                  >
                    {lang}
                    {isEditing && (
                      <button
                        onClick={() => handleLanguageRemove(index)}
                        className="ml-1 hover:text-purple-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    )}
                  </span>
                ))}
                {isEditing && (
                  <input
                    type="text"
                    placeholder="Add language (press Enter)"
                    onKeyDown={handleLanguageAdd}
                    className="px-3 py-1 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                )}
              </div>
            </div>

            {/* Address */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Clinic Address
              </label>
              {isEditing ? (
                <textarea
                  value={editData.address}
                  onChange={(e) => setEditData({ ...editData, address: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <p className="text-gray-900">{profileData.address}</p>
              )}
            </div>

            {/* Availability */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Clock className="w-4 h-4 inline mr-1" />
                Weekly Schedule
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(isEditing ? editData.availability : profileData.availability).map(([day, hours]) => (
                  <div key={day} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-700 capitalize">{day}</span>
                    {isEditing ? (
                      <input
                        type="text"
                        value={hours}
                        onChange={(e) => setEditData({
                          ...editData,
                          availability: {
                            ...editData.availability,
                            [day]: e.target.value
                          }
                        })}
                        className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    ) : (
                      <span className="text-sm text-gray-600">{hours}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Profile;