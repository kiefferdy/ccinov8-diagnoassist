import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { usePatientData } from '../../context/PatientDataContext'
import { showInfo } from './NotificationSystem'

const KeyboardShortcuts = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { nextStep, prevStep } = usePatientData()

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Only handle shortcuts when not typing in an input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
        return
      }

      // Ctrl/Cmd + key combinations
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault()
            showInfo('Auto-save is always enabled', 'Save')
            break
          case 'ArrowRight':
            e.preventDefault()
            handleNextStep()
            break
          case 'ArrowLeft':
            e.preventDefault()
            handlePrevStep()
            break
          case '1':
            e.preventDefault()
            navigate('/patient-info')
            break
          case '2':
            e.preventDefault()
            navigate('/physical-exam')
            break
          case '3':
            e.preventDefault()
            navigate('/diagnostic-analysis')
            break
          case '4':
            e.preventDefault()
            navigate('/recommended-tests')
            break
          case '5':
            e.preventDefault()
            navigate('/test-results')
            break
          case '6':
            e.preventDefault()
            navigate('/final-diagnosis')
            break
          case '/':
            e.preventDefault()
            showShortcutsHelp()
            break
        }
      }

      // Arrow keys for navigation (without Ctrl/Cmd)
      if (!e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey) {
        switch (e.key) {
          case 'ArrowRight':
            if (!isFormElement(e.target)) {
              e.preventDefault()
              handleNextStep()
            }
            break
          case 'ArrowLeft':
            if (!isFormElement(e.target)) {
              e.preventDefault()
              handlePrevStep()
            }
            break
          case 'Escape':
            // Clear focus from any active element
            document.activeElement?.blur()
            break
        }
      }
    }

    const isFormElement = (element) => {
      return ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(element.tagName)
    }

    const handleNextStep = () => {
      const paths = ['/patient-info', '/physical-exam', '/diagnostic-analysis', '/recommended-tests', '/test-results', '/final-diagnosis']
      const currentIndex = paths.indexOf(location.pathname)
      if (currentIndex >= 0 && currentIndex < paths.length - 1) {
        navigate(paths[currentIndex + 1])
        nextStep()
      }
    }

    const handlePrevStep = () => {
      const paths = ['/patient-info', '/physical-exam', '/diagnostic-analysis', '/recommended-tests', '/test-results', '/final-diagnosis']
      const currentIndex = paths.indexOf(location.pathname)
      if (currentIndex > 0) {
        navigate(paths[currentIndex - 1])
        prevStep()
      }
    }

    const showShortcutsHelp = () => {
      const shortcuts = [
        'Ctrl/Cmd + S: Save (auto-save enabled)',
        'Ctrl/Cmd + → / ←: Next/Previous step',
        'Ctrl/Cmd + 1-6: Go to specific step',
        'Ctrl/Cmd + /: Show this help',
        '← / →: Navigate steps (when not in form)',
        'Esc: Clear focus'
      ]
      
      showInfo(shortcuts.join('\n'), 'Keyboard Shortcuts')
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [location.pathname, navigate, nextStep, prevStep])

  return null // This component doesn't render anything
}

export default KeyboardShortcuts