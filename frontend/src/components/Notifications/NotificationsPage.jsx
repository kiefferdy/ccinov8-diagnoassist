import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, X, Calendar, AlertCircle, CheckCircle, 
  FileText, Users, Activity, Clock, ArrowLeft,
  Trash2, CheckCheck, Filter, Search
} from 'lucide-react';
import { StorageManager } from '../../utils/storage';
import DashboardLayout from '../Layout/DashboardLayout';

const NotificationsPage = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [filteredNotifications, setFilteredNotifications] = useState([]);
  const [selectedType, setSelectedType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState([]);

  useEffect(() => {
    const stored = StorageManager.getNotifications();
    setNotifications(stored);
    setFilteredNotifications(stored);
  }, []);

  useEffect(() => {
    let filtered = notifications;
    
    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(n => n.type === selectedType);
    }
    
    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(n => 
        n.message.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredNotifications(filtered);
  }, [notifications, selectedType, searchTerm]);
  const markAsRead = (notificationId) => {
    const updated = StorageManager.markNotificationAsRead(notificationId);
    setNotifications(updated);
  };

  const markAllAsRead = () => {
    const updated = notifications.map(n => ({ ...n, read: true }));
    StorageManager.saveNotifications(updated);
    setNotifications(updated);
  };

  const deleteNotification = (notificationId) => {
    const updated = notifications.filter(n => n.id !== notificationId);
    StorageManager.saveNotifications(updated);
    setNotifications(updated);
    setSelectedNotifications(selectedNotifications.filter(id => id !== notificationId));
  };

  const deleteSelected = () => {
    const updated = notifications.filter(n => !selectedNotifications.includes(n.id));
    StorageManager.saveNotifications(updated);
    setNotifications(updated);
    setSelectedNotifications([]);
  };

  const toggleSelectNotification = (notificationId) => {
    setSelectedNotifications(prev => 
      prev.includes(notificationId)
        ? prev.filter(id => id !== notificationId)
        : [...prev, notificationId]
    );
  };

  const selectAll = () => {
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(filteredNotifications.map(n => n.id));
    }
  };
  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const getIconComponent = (iconType) => {
    switch (iconType) {
      case 'calendar': return Calendar;
      case 'file-text': return FileText;
      case 'alert-circle': return AlertCircle;
      case 'check-circle': return CheckCircle;
      case 'activity': return Activity;
      default: return Bell;
    }
  };

  const notificationTypes = [
    { value: 'all', label: 'All Notifications' },
    { value: 'appointment', label: 'Appointments' },
    { value: 'episode', label: 'Episodes' },
    { value: 'test-result', label: 'Test Results' },
    { value: 'alert', label: 'Alerts' },
    { value: 'update', label: 'Updates' }
  ];

  const unreadCount = notifications.filter(n => !n.read).length;
  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => navigate(-1)}
                  className="p-2 hover:bg-white rounded-xl transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                    <Bell className="w-8 h-8 text-blue-600" />
                    Notifications
                  </h1>
                  <p className="text-gray-600 mt-1">
                    {notifications.length} total • {unreadCount} unread
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {selectedNotifications.length > 0 && (
                  <button
                    onClick={deleteSelected}
                    className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-xl hover:bg-red-200 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Selected ({selectedNotifications.length})
                  </button>
                )}
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-xl hover:bg-blue-200 transition-colors"
                  >
                    <CheckCheck className="w-4 h-4" />
                    Mark All Read
                  </button>
                )}
              </div>
            </div>
          </div>
          {/* Filters */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search notifications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                {notificationTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Notifications List */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            {filteredNotifications.length > 0 && (
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedNotifications.length === filteredNotifications.length}
                    onChange={selectAll}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Select All ({filteredNotifications.length})
                  </span>
                </label>
              </div>
            )}
            {filteredNotifications.length === 0 ? (
              <div className="p-16 text-center">
                <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No notifications found</h3>
                <p className="text-gray-600">
                  {searchTerm || selectedType !== 'all' 
                    ? 'Try adjusting your filters' 
                    : 'You\'re all caught up!'}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {filteredNotifications.map(notification => {
                  const Icon = getIconComponent(notification.iconType);
                  return (
                    <div
                      key={notification.id}
                      className={`p-6 hover:bg-gray-50 transition-colors ${
                        !notification.read ? 'bg-blue-50/30' : ''
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedNotifications.includes(notification.id)}
                            onChange={() => toggleSelectNotification(notification.id)}
                            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                          />
                        </label>
                        
                        <div className={`p-3 rounded-xl ${
                          notification.color === 'blue' ? 'bg-blue-100' :
                          notification.color === 'green' ? 'bg-green-100' :
                          notification.color === 'red' ? 'bg-red-100' :
                          notification.color === 'purple' ? 'bg-purple-100' : 'bg-gray-100'
                        }`}>
                          <Icon className={`w-6 h-6 ${
                            notification.color === 'blue' ? 'text-blue-600' :
                            notification.color === 'green' ? 'text-green-600' :
                            notification.color === 'red' ? 'text-red-600' :
                            notification.color === 'purple' ? 'text-purple-600' : 'text-gray-600'
                          }`} />
                        </div>
                        
                        <div className="flex-1">
                          <p className={`text-base ${!notification.read ? 'font-semibold' : ''} text-gray-900`}>
                            {notification.message}
                          </p>
                          <p className="text-sm text-gray-500 mt-1">
                            {getTimeAgo(notification.timestamp)}
                          </p>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {!notification.read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                              title="Mark as read"
                            >
                              <CheckCircle className="w-5 h-5 text-gray-400" />
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotification(notification.id)}
                            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <X className="w-5 h-5 text-gray-400" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default NotificationsPage;