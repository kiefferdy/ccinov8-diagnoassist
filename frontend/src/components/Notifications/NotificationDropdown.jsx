import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, X, Calendar, AlertCircle, CheckCircle, 
  FileText, Users, Activity, Clock
} from 'lucide-react';
import { StorageManager } from '../../utils/storage';

const NotificationDropdown = () => {
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const dropdownRef = useRef(null);

  // Load notifications
  useEffect(() => {
    const loadNotifications = () => {
      const stored = StorageManager.getNotifications();
      if (stored.length === 0) {
        // Initialize with sample notifications
        const sampleNotifications = generateSampleNotifications();
        StorageManager.saveNotifications(sampleNotifications);
        setNotifications(sampleNotifications);
      } else {
        setNotifications(stored);
      }
    };
    loadNotifications();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Generate sample notifications
  const generateSampleNotifications = () => {
    const types = [
      {
        type: 'appointment',
        iconType: 'calendar',
        color: 'blue',
        messages: [
          'New appointment scheduled with John Doe',
          'Appointment reminder: Sarah Johnson at 2:00 PM',
          'Appointment cancelled by patient Michael Brown'
        ]
      },
      {
        type: 'episode',
        iconType: 'activity',
        color: 'blue',
        messages: [
          'New episode created for patient James Wilson',
          'Episode #EP-2024-003 requires review',
          'Follow-up needed for episode: Acute Bronchitis'
        ]
      },
      {
        type: 'test-result',
        iconType: 'file-text',
        color: 'green',
        messages: [
          'Lab results available for Emily Davis',
          'X-ray report ready for review',
          'Blood test results require immediate attention'
        ]
      },
      {
        type: 'alert',
        iconType: 'alert-circle',
        color: 'red',
        messages: [
          'Critical lab value for patient Robert Wilson',
          'Medication interaction alert',
          'Patient no-show for scheduled procedure'
        ]
      },
      {
        type: 'update',
        iconType: 'check-circle',
        color: 'purple',
        messages: [
          'Treatment plan updated for Jennifer Martinez',
          'New diagnosis added to patient record',
          'Episode marked as resolved'
        ]
      }
    ];

    const notifications = [];
    const now = new Date();

    // Generate 8-10 random notifications
    for (let i = 0; i < Math.floor(Math.random() * 3) + 8; i++) {
      const typeInfo = types[Math.floor(Math.random() * types.length)];
      const timestamp = new Date(now.getTime() - Math.random() * 72 * 60 * 60 * 1000); // Random time within last 72 hours
      
      notifications.push({
        id: `NOTIF-${Date.now()}-${i}`,
        type: typeInfo.type,
        message: typeInfo.messages[Math.floor(Math.random() * typeInfo.messages.length)],
        timestamp: timestamp.toISOString(),
        read: Math.random() > 0.6,
        iconType: typeInfo.iconType,
        color: typeInfo.color
      });
    }

    return notifications.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  };

  // Mark notification as read
  const markAsRead = (notificationId) => {
    const updated = StorageManager.markNotificationAsRead(notificationId);
    setNotifications(updated);
  };

  // Mark all as read
  const markAllAsRead = () => {
    const updated = notifications.map(notif => ({ ...notif, read: true }));
    StorageManager.saveNotifications(updated);
    setNotifications(updated);
  };

  // Delete notification
  const deleteNotification = (notificationId) => {
    const updated = notifications.filter(notif => notif.id !== notificationId);
    StorageManager.saveNotifications(updated);
    setNotifications(updated);
  };

  // Clear all notifications
  const clearAll = () => {
    StorageManager.saveNotifications([]);
    setNotifications([]);
    setShowDropdown(false);
  };

  // Get time ago string
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

  const unreadCount = notifications.filter(n => !n.read).length;

  // Get icon component from iconType
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

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border border-gray-200 z-50">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Mark all read
                  </button>
                )}
                {notifications.length > 0 && (
                  <button
                    onClick={clearAll}
                    className="text-sm text-gray-600 hover:text-gray-700"
                  >
                    Clear all
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No notifications</p>
              </div>
            ) : (
              notifications.map(notification => {
                const Icon = getIconComponent(notification.iconType);
                return (
                  <div
                    key={notification.id}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                    className={`p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${
                      !notification.read ? 'bg-blue-50/30' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${
                        notification.color === 'blue' ? 'bg-blue-100' :
                        notification.color === 'green' ? 'bg-green-100' :
                        notification.color === 'red' ? 'bg-red-100' :
                        notification.color === 'purple' ? 'bg-purple-100' : 'bg-gray-100'
                      }`}>
                        <Icon className={`w-5 h-5 ${
                          notification.color === 'blue' ? 'text-blue-600' :
                          notification.color === 'green' ? 'text-green-600' :
                          notification.color === 'red' ? 'text-red-600' :
                          notification.color === 'purple' ? 'text-purple-600' : 'text-gray-600'
                        }`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${!notification.read ? 'font-medium' : ''} text-gray-900`}>
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {getTimeAgo(notification.timestamp)}
                        </p>
                      </div>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        className="p-1 hover:bg-gray-200 rounded transition-colors"
                      >
                        <X className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-gray-200 text-center">
              <button 
                onClick={() => {
                  setShowDropdown(false);
                  navigate('/notifications');
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;