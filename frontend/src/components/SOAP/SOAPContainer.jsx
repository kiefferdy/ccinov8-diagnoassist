import React, { useState } from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { useEncounter } from '../../contexts/EncounterContext';
import SubjectiveSection from './Subjective/SubjectiveSection';
import ObjectiveSection from './Objective/ObjectiveSection';
import AssessmentSection from './Assessment/AssessmentSection';
import PlanSection from './Plan/PlanSection';
import SOAPProgress from './SOAPProgress';
import UnifiedVoiceInput from './UnifiedVoice/UnifiedVoiceInput';
import AutoSaveIndicator from '../common/AutoSaveIndicator';
import AIAssistant from '../common/AIAssistant';
import useKeyboardShortcuts from '../../hooks/useKeyboardShortcuts';
import './animations.css';
import { 
  ChevronLeft, ChevronRight, MessageSquare, Stethoscope, 
  Brain, FileText, Check, Clock, Sparkles,
  Save, CheckCircle, Keyboard, X
} from 'lucide-react';

const SOAPContainer = ({ encounter, episode, patient, onUpdate, onSave, onSign, saving, hasUnsavedChanges, lastSaved }) => {
  const { 
    currentSection, 
    navigateToSection, 
    getAdjacentSection,
    sectionProgress 
  } = useNavigation();
  
  const { getEpisodeEncounters } = useEncounter();
  const [showShortcuts, setShowShortcuts] = useState(false);
  
  // Define sections array first
  const sections = [
    { 
      id: 'subjective', 
      label: 'Subjective', 
      shortLabel: 'S',
      icon: MessageSquare,
      color: 'blue',
      bgGradient: 'from-blue-500 to-blue-600'
    },
    { 
      id: 'objective', 
      label: 'Objective', 
      shortLabel: 'O',
      icon: Stethoscope,
      color: 'green',
      bgGradient: 'from-green-500 to-green-600'
    },
    { 
      id: 'assessment', 
      label: 'Assessment', 
      shortLabel: 'A',
      icon: Brain,
      color: 'purple',
      bgGradient: 'from-purple-500 to-purple-600'
    },
    { 
      id: 'plan', 
      label: 'Plan', 
      shortLabel: 'P',
      icon: FileText,
      color: 'orange',
      bgGradient: 'from-orange-500 to-orange-600'
    }
  ];
  
  const currentSectionIndex = sections.findIndex(s => s.id === currentSection);
  
  // Define navigation functions before using them in keyboard shortcuts
  const navigateToNextSection = () => {
    const nextSection = getAdjacentSection('next');
    if (nextSection) {
      navigateToSection(nextSection);
    }
  };
  
  const navigateToPreviousSection = () => {
    const prevSection = getAdjacentSection('previous');
    if (prevSection) {
      navigateToSection(prevSection);
    }
  };
  
  // Setup keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 's',
      ctrl: true,
      callback: () => {
        if (onSave && hasUnsavedChanges) {
          onSave();
        }
      },
      enabled: true
    },
    {
      key: '1',
      alt: true,
      callback: () => navigateToSection('subjective'),
      enabled: true
    },
    {
      key: '2',
      alt: true,
      callback: () => navigateToSection('objective'),
      enabled: true
    },
    {
      key: '3',
      alt: true,
      callback: () => navigateToSection('assessment'),
      enabled: true
    },
    {
      key: '4',
      alt: true,
      callback: () => navigateToSection('plan'),
      enabled: true
    },
    {
      key: 'ArrowLeft',
      alt: true,
      callback: navigateToPreviousSection,
      enabled: currentSectionIndex > 0
    },
    {
      key: 'ArrowRight',
      alt: true,
      callback: navigateToNextSection,
      enabled: currentSectionIndex < sections.length - 1
    },
    {
      key: '?',
      shift: true,
      callback: () => setShowShortcuts(!showShortcuts),
      enabled: true
    }
  ]);
  const CurrentComponent = sections[currentSectionIndex]?.component || 
    (currentSection === 'subjective' ? SubjectiveSection :
     currentSection === 'objective' ? ObjectiveSection :
     currentSection === 'assessment' ? AssessmentSection :
     PlanSection);  
  
  const handleSectionUpdate = (sectionData) => {
    onUpdate({
      soap: {
        ...encounter.soap,
        [currentSection]: {
          ...encounter.soap[currentSection],
          ...sectionData,
          lastUpdated: new Date().toISOString()
        }
      }
    });
  };
  
  const handleUnifiedVoiceUpdate = (processedData) => {
    // Update all sections at once with the processed voice data
    const updates = {
      soap: {
        ...encounter.soap,
        subjective: {
          ...encounter.soap.subjective,
          ...processedData.subjective,
          lastUpdated: new Date().toISOString()
        },
        objective: {
          ...encounter.soap.objective,
          ...processedData.objective,
          lastUpdated: new Date().toISOString()
        },
        assessment: {
          ...encounter.soap.assessment,
          ...processedData.assessment,
          lastUpdated: new Date().toISOString()
        },
        plan: {
          ...encounter.soap.plan,
          ...processedData.plan,
          lastUpdated: new Date().toISOString()
        }
      }
    };
    
    onUpdate(updates);
  };
  
  const getCompletionIcon = (status) => {
    if (status === 'complete') {
      return <Check className="w-3 h-3" />;
    } else if (status === 'partial') {
      return <Clock className="w-3 h-3" />;
    }
    return null;
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Modern Header with Voice Input */}
      <div className="bg-white shadow-lg border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <Sparkles className="w-6 h-6 mr-2 text-blue-600" />
                Encounter Documentation
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(encounter.date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
              {encounter.status === 'signed' && (
                <div className="mt-2 flex items-center text-sm text-green-700 bg-green-50 px-3 py-1 rounded-full w-fit">
                  <CheckCircle className="w-4 h-4 mr-1.5" />
                  Signed by {encounter.signedBy} on {new Date(encounter.signedAt).toLocaleString()}
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
              <AutoSaveIndicator 
                hasUnsavedChanges={hasUnsavedChanges}
                lastSaved={lastSaved}
              />
              
              <button
                onClick={onSave}
                disabled={!hasUnsavedChanges || saving}
                className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Save className="w-4 h-4 mr-1.5" />
                {saving ? 'Saving...' : 'Save'}
              </button>
              
              {encounter.status !== 'signed' && (
                <button
                  onClick={onSign}
                  className="inline-flex items-center px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <CheckCircle className="w-4 h-4 mr-1.5" />
                  Sign Encounter
                </button>
              )}
            </div>
          </div>
          
          {/* Integrated Voice Input */}
          <UnifiedVoiceInput 
            encounter={encounter}
            onUpdateSections={handleUnifiedVoiceUpdate}
          />
        </div>        
        {/* Modern SOAP Navigation Tabs */}
        <div className="px-6 pb-0">
          <nav className="flex space-x-4 relative">
            {sections.map((section, idx) => {
              const Icon = section.icon;
              const isActive = currentSection === section.id;
              const status = sectionProgress[section.id];
              
              return (
                <button
                  key={section.id}
                  onClick={() => navigateToSection(section.id)}
                  className={`
                    relative group flex items-center px-4 py-3 rounded-t-xl transition-all duration-300
                    ${isActive
                      ? 'bg-gradient-to-r ' + section.bgGradient + ' text-white shadow-lg transform -translate-y-1'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-800'
                    }
                  `}
                >
                  <div className="flex items-center space-x-2">
                    <Icon className={`w-5 h-5 ${isActive ? 'animate-pulse' : ''}`} />
                    <span className="font-medium hidden sm:inline">{section.label}</span>
                    <span className="font-medium sm:hidden">{section.shortLabel}</span>
                    
                    {status && (
                      <div className={`
                        ml-2 w-5 h-5 rounded-full flex items-center justify-center text-white text-xs
                        ${status === 'complete' ? 'bg-green-500' : 'bg-yellow-500'}
                        ${isActive ? 'animate-bounce' : ''}
                      `}>
                        {getCompletionIcon(status)}
                      </div>
                    )}
                  </div>
                  
                  {/* Progress Indicator */}
                  {idx < sections.length - 1 && (
                    <div className="absolute -right-4 top-1/2 -translate-y-1/2 z-10">
                      <ChevronRight className={`
                        w-5 h-5 
                        ${status === 'complete' ? 'text-green-500' : 'text-gray-400'}
                        ${isActive ? 'animate-pulse' : ''}
                      `} />
                    </div>
                  )}
                  
                  {/* Hover Effect */}
                  <div className={`
                    absolute inset-0 rounded-t-xl bg-white opacity-0 group-hover:opacity-10 
                    transition-opacity duration-300
                  `} />
                </button>
              );
            })}
          </nav>
        </div>
      </div>
      
      {/* Enhanced Progress Bar */}
      <div className="bg-white shadow-sm">
        <SOAPProgress />
      </div>      
      {/* Section Content with Animation */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-6">
          <div className="animate-fadeIn">
            {CurrentComponent && (
              <CurrentComponent
                data={encounter.soap[currentSection]}
                patient={patient}
                episode={episode}
                encounter={encounter}
                onUpdate={handleSectionUpdate}
              />
            )}
          </div>
        </div>
      </div>
      
      {/* Modern Navigation Footer */}
      <div className="bg-gradient-to-b from-white to-gray-50 border-t border-gray-200 shadow-lg">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <button
              onClick={navigateToPreviousSection}
              disabled={currentSectionIndex === 0}
              className={`
                inline-flex items-center px-6 py-3 text-sm font-medium rounded-xl
                transition-all duration-300 transform hover:scale-105
                ${currentSectionIndex === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-gray-200 to-gray-300 text-gray-700 hover:from-gray-300 hover:to-gray-400 hover:shadow-md'
                }
              `}
            >
              <ChevronLeft className="w-5 h-5 mr-2" />
              Previous
            </button>
            
            <div className="flex items-center space-x-2">
              {sections.map((section, idx) => (
                <div
                  key={section.id}
                  className={`
                    rounded-full transition-all duration-300 shadow-sm
                    ${idx === currentSectionIndex
                      ? 'w-8 h-2 bg-gradient-to-r ' + section.bgGradient
                      : sectionProgress[section.id] === 'complete'
                      ? 'w-2 h-2 bg-green-500'
                      : sectionProgress[section.id] === 'partial'
                      ? 'w-2 h-2 bg-yellow-500'
                      : 'w-2 h-2 bg-gray-300'
                    }
                  `}
                />
              ))}
            </div>
            
            <button
              onClick={navigateToNextSection}
              disabled={currentSectionIndex === sections.length - 1}
              className={`
                inline-flex items-center px-6 py-3 text-sm font-medium rounded-xl
                transition-all duration-300 transform hover:scale-105
                ${currentSectionIndex === sections.length - 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-md hover:shadow-xl'
                }
              `}
            >
              Next
              <ChevronRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>
      </div>
      
      {/* AI Assistant - Persistent across sections */}
      <AIAssistant
        patient={patient}
        episode={episode}
        encounter={encounter}
        encounterId={encounter?.id}
        currentSection={currentSection}
        onInsightApply={(insight) => {
          // Handle insights based on current section
          if (insight.section && insight.section === currentSection) {
            handleSectionUpdate({ [insight.field || 'content']: insight.content });
          }
        }}
      />
      
      {/* Keyboard Shortcuts Help */}
      <button
        onClick={() => setShowShortcuts(!showShortcuts)}
        className="fixed bottom-6 left-6 p-3 bg-gray-800 text-white rounded-full shadow-lg hover:bg-gray-700 transition-all z-40"
        title="Keyboard Shortcuts (Shift+?)"
      >
        <Keyboard className="w-5 h-5" />
      </button>
      
      {showShortcuts && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">Keyboard Shortcuts</h3>
              <button
                onClick={() => setShowShortcuts(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Save Encounter</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Ctrl+S</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Go to Subjective</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+1</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Go to Objective</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+2</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Go to Assessment</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+3</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Go to Plan</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+4</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Previous Section</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+←</kbd>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Next Section</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Alt+→</kbd>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-700">Show/Hide Shortcuts</span>
                <kbd className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-mono">Shift+?</kbd>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SOAPContainer;