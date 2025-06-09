import { useState, useEffect } from 'react'
import { CheckCircle, AlertTriangle, XCircle, X, Info } from 'lucide-react'
import clsx from 'clsx'

let notificationId = 0

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState([])

  const addNotification = (notification) => {
    const id = ++notificationId
    const newNotification = { id, ...notification }
    setNotifications(prev => [...prev, newNotification])

    // Auto remove after 5 seconds unless it's an error
    if (notification.type !== 'error') {
      setTimeout(() => {
        removeNotification(id)
      }, 5000)
    }
  }

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }

  // Global function to add notifications
  window.showNotification = addNotification

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />
      case 'error':
        return <XCircle className="w-5 h-5" />
      case 'info':
      default:
        return <Info className="w-5 h-5" />
    }
  }

  const getStyles = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={clsx(
            'max-w-sm p-4 rounded-lg border shadow-lg animate-in slide-in-from-top duration-300',
            getStyles(notification.type)
          )}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {getIcon(notification.type)}
            </div>
            <div className="flex-1">
              {notification.title && (
                <h4 className="font-medium mb-1">{notification.title}</h4>
              )}
              <p className="text-sm">{notification.message}</p>
            </div>
            <button
              onClick={() => removeNotification(notification.id)}
              className="flex-shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default NotificationSystem

// Helper functions
export const showSuccess = (message, title) => {
  if (window.showNotification) {
    window.showNotification({ type: 'success', message, title })
  }
}

export const showError = (message, title) => {
  if (window.showNotification) {
    window.showNotification({ type: 'error', message, title })
  }
}

export const showWarning = (message, title) => {
  if (window.showNotification) {
    window.showNotification({ type: 'warning', message, title })
  }
}

export const showInfo = (message, title) => {
  if (window.showNotification) {
    window.showNotification({ type: 'info', message, title })
  }
}