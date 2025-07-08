import React, { useState } from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { useEncounter } from '../../contexts/EncounterContext';
import SubjectiveSection from './Subjective/SubjectiveSection';
import ObjectiveSection from './Objective/ObjectiveSection';
import AssessmentSection from './Assessment/AssessmentSection';
import PlanSection from './Plan/PlanSection';
import SOAPProgress from './SOAPProgress';
import CopyForward from '../common/CopyForward';
import QuickTemplate from '../common/QuickTemplate';
import UnifiedVoiceInput from './UnifiedVoice/UnifiedVoiceInput';
import './animations.css';
import { 
  ChevronLeft, ChevronRight, MessageSquare, Stethoscope, 
  Brain, FileText, Check, Clock, Sparkles, MoreVertical,
  Copy, Layout, Zap
} from 'lucide-react';

const SOAPContainer = ({ encounter, episode, patient, onUpdate }) => {
  const { 
    currentSection, 
    navigateToSection, 
    getAdjacentSection,
    sectionProgress 
  } = useNavigation();
  
  const { getEpisodeEncounters, copyForwardFromEncounter } = useEncounter();
  const [showMoreOptions, setShowMoreOptions] = useState(false);
  
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
  const CurrentComponent = sections[currentSectionIndex]?.component || 
    (currentSection === 'subjective' ? SubjectiveSection :
     currentSection === 'objective' ? ObjectiveSection :
     currentSection === 'assessment' ? AssessmentSection :
     PlanSection);  
  // Get previous encounters for copy forward
  const previousEncounters = getEpisodeEncounters(episode.id)
    .filter(e => e.id !== encounter.id && e.status === 'signed');
  
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
  const handleCopyForward = (sourceEncounterId, sections) => {
    copyForwardFromEncounter(sourceEncounterId, sections);
  };
  
  const handleApplyTemplate = (template) => {
    // Apply template data to current encounter
    const updates = {};
    
    if (template.hpi) {
      updates.subjective = { ...encounter.soap.subjective, hpi: template.hpi };
    }
    if (template.ros) {
      updates.subjective = { ...updates.subjective || encounter.soap.subjective, ros: template.ros };
    }
    if (template.physicalExam) {
      updates.objective = { 
        ...encounter.soap.objective,
        physicalExam: { 
          ...encounter.soap.objective.physicalExam,
          ...template.physicalExam 
        }
      };
    }
    if (template.assessment) {
      updates.assessment = { 
        ...encounter.soap.assessment, 
        clinicalImpression: template.assessment 
      };
    }
    if (template.plan) {
      updates.plan = { ...encounter.soap.plan, ...template.plan };
    }
    
    // Apply all updates at once
    Object.keys(updates).forEach(section => {
      onUpdate({
        soap: {
          ...encounter.soap,
          [section]: updates[section]
        }
      });
    });
  };
  
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
            </div>
            
            <div className="flex items-center space-x-3">
              {previousEncounters.length > 0 && encounter.status !== 'signed' && (
                <CopyForward 
                  previousEncounters={previousEncounters}
                  onCopyForward={handleCopyForward}
                />
              )}
              
              {encounter.status !== 'signed' && (
                <QuickTemplate 
                  onApplyTemplate={handleApplyTemplate}
                  currentChiefComplaint={episode.chiefComplaint}
                />
              )}
              
              <div className="relative">
                <button
                  onClick={() => setShowMoreOptions(!showMoreOptions)}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
                
                {showMoreOptions && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-10">
                    <button className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                      <Copy className="w-4 h-4" />
                      <span>Copy to clipboard</span>
                    </button>
                    <button className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                      <Layout className="w-4 h-4" />
                      <span>Change layout</span>
                    </button>
                  </div>
                )}
              </div>
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
          <nav className="flex space-x-2">
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
                    <ChevronRight className={`
                      absolute -right-3 w-6 h-6 
                      ${status === 'complete' ? 'text-green-500' : 'text-gray-300'}
                      ${isActive ? 'animate-pulse' : ''}
                    `} />
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
      <div className="bg-white border-t border-gray-200 shadow-lg">
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
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 hover:shadow-md'
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
                    w-2 h-2 rounded-full transition-all duration-300
                    ${idx === currentSectionIndex
                      ? 'w-8 bg-gradient-to-r ' + section.bgGradient
                      : sectionProgress[section.id] === 'complete'
                      ? 'bg-green-500'
                      : sectionProgress[section.id] === 'partial'
                      ? 'bg-yellow-500'
                      : 'bg-gray-300'
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
      
      {/* Click outside to close more options */}
      {showMoreOptions && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setShowMoreOptions(false)}
        />
      )}
    </div>
  );
};

export default SOAPContainer;