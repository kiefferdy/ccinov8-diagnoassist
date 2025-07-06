import React from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { useEncounter } from '../../contexts/EncounterContext';
import SubjectiveSection from './Subjective/SubjectiveSection';
import ObjectiveSection from './Objective/ObjectiveSection';
import AssessmentSection from './Assessment/AssessmentSection';
import PlanSection from './Plan/PlanSection';
import SOAPProgress from './SOAPProgress';
import CopyForward from '../common/CopyForward';
import QuickTemplate from '../common/QuickTemplate';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const SOAPContainer = ({ encounter, episode, patient, onUpdate }) => {
  const { 
    currentSection, 
    navigateToSection, 
    getAdjacentSection,
    sectionProgress 
  } = useNavigation();
  
  const { getEpisodeEncounters, copyForwardFromEncounter } = useEncounter();
  
  const sections = [
    { id: 'subjective', label: 'Subjective (S)', component: SubjectiveSection },
    { id: 'objective', label: 'Objective (O)', component: ObjectiveSection },
    { id: 'assessment', label: 'Assessment (A)', component: AssessmentSection },
    { id: 'plan', label: 'Plan (P)', component: PlanSection }
  ];
  
  const currentSectionIndex = sections.findIndex(s => s.id === currentSection);
  const CurrentComponent = sections[currentSectionIndex]?.component;
  
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
  
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* SOAP Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-0">
          <nav className="flex space-x-8">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => navigateToSection(section.id)}
                className={`
                  relative py-4 px-1 text-sm font-medium transition-colors
                  ${currentSection === section.id
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                  }
                `}
              >
                <span className="flex items-center">
                  {section.label}
                  {sectionProgress[section.id] === 'complete' && (
                    <span className="ml-2 w-2 h-2 bg-green-500 rounded-full" />
                  )}
                  {sectionProgress[section.id] === 'partial' && (
                    <span className="ml-2 w-2 h-2 bg-yellow-500 rounded-full" />
                  )}
                </span>
              </button>
            ))}
          </nav>
        </div>
        
        {/* Progress Bar */}
        <SOAPProgress />
      </div>
      
      {/* Section Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-6">
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
      
      {/* Navigation Footer */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={navigateToPreviousSection}
              disabled={currentSectionIndex === 0}
              className="inline-flex items-center px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </button>
            
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
          </div>
          
          <button
            onClick={navigateToNextSection}
            disabled={currentSectionIndex === sections.length - 1}
            className="inline-flex items-center px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default SOAPContainer;