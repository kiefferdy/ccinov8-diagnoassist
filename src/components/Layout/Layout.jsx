import { useLocation, useNavigate } from 'react-router-dom'
import { usePatientData } from '../../context/PatientDataContext'
import NotificationSystem from './NotificationSystem'
import KeyboardShortcuts from './KeyboardShortcuts'
import { 
  User, 
  Activity, 
  Brain, 
  TestTube, 
  ClipboardList, 
  FileText,
  Stethoscope,
  ArrowLeft,
  ArrowRight
} from 'lucide-react'
import clsx from 'clsx'

const steps = [
  { id: 1, name: 'Patient Info', path: '/app/patient-info', icon: User },
  { id: 2, name: 'Physical Exam', path: '/app/physical-exam', icon: Activity },
  { id: 3, name: 'AI Analysis', path: '/app/diagnostic-analysis', icon: Brain },
  { id: 4, name: 'Recommended Tests', path: '/app/recommended-tests', icon: TestTube },
  { id: 5, name: 'Test Results', path: '/app/test-results', icon: ClipboardList },
  { id: 6, name: 'Final Diagnosis', path: '/app/final-diagnosis', icon: FileText },
]

export default function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { currentStep, patient, nextStep, prevStep } = usePatientData()

  const getCurrentStepFromPath = () => {
    const step = steps.find(s => s.path === location.pathname)
    return step ? step.id : 1
  }

  const currentStepNumber = getCurrentStepFromPath()
  const canGoNext = currentStepNumber < steps.length
  const canGoPrev = currentStepNumber > 1

  const handleNext = () => {
    if (canGoNext) {
      const nextStepPath = steps[currentStepNumber].path
      navigate(nextStepPath)
      nextStep()
    }
  }

  const handlePrev = () => {
    if (canGoPrev) {
      const prevStepPath = steps[currentStepNumber - 2].path
      navigate(prevStepPath)
      prevStep()
    }
  }

  const handleStepClick = (step) => {
    navigate(step.path)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NotificationSystem />
      <KeyboardShortcuts />
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <Stethoscope className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">DiagnoAssist</h1>
                <p className="text-sm text-gray-600">AI-Powered Diagnostic Assistant</p>
              </div>
            </div>
            
            {patient.name && (
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{patient.name}</p>
                <p className="text-xs text-gray-600">
                  {patient.age && `Age: ${patient.age}`}
                  {patient.age && patient.gender && ' • '}
                  {patient.gender}
                </p>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Progress Stepper */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-between">
              {steps.map((step, stepIdx) => {
                const isCompleted = step.id < currentStepNumber
                const isCurrent = step.id === currentStepNumber
                const Icon = step.icon

                return (
                  <li key={step.name} className="relative flex-1">
                    {stepIdx !== steps.length - 1 && (
                      <div
                        className={clsx(
                          'absolute top-4 left-4 w-full h-0.5 -ml-px',
                          isCompleted ? 'bg-primary-600' : 'bg-gray-200'
                        )}
                        style={{ width: 'calc(100% - 2rem)' }}
                      />
                    )}
                    
                    <button
                      onClick={() => handleStepClick(step)}
                      className={clsx(
                        'relative flex flex-col items-center group focus:outline-none',
                        'hover:opacity-80 transition-opacity duration-200'
                      )}
                    >
                      <span
                        className={clsx(
                          'step-indicator relative z-10',
                          isCurrent && 'step-active',
                          isCompleted && 'step-completed',
                          !isCurrent && !isCompleted && 'step-pending'
                        )}
                      >
                        <Icon className="w-4 h-4" />
                      </span>
                      <span
                        className={clsx(
                          'mt-2 text-xs font-medium text-center max-w-20',
                          isCurrent ? 'text-primary-600' : 'text-gray-500'
                        )}
                      >
                        {step.name}
                      </span>
                    </button>
                  </li>
                )
              })}
            </ol>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          {children}
        </div>
      </main>

      {/* Navigation Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <button
              onClick={handlePrev}
              disabled={!canGoPrev}
              className={clsx(
                'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200',
                canGoPrev
                  ? 'text-gray-700 hover:bg-gray-100 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2'
                  : 'text-gray-400 cursor-not-allowed'
              )}
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                Step {currentStepNumber} of {steps.length}
              </span>
            </div>

            <button
              onClick={handleNext}
              disabled={!canGoNext}
              className={clsx(
                'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200',
                canGoNext
                  ? 'btn-primary'
                  : 'text-gray-400 cursor-not-allowed bg-gray-100'
              )}
            >
              <span>Next</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </footer>
    </div>
  )
}