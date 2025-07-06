import React, { createContext, useContext, useState, useCallback } from 'react';

const NavigationContext = createContext(null);

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};

export const NavigationProvider = ({ children }) => {
  // Current view state
  const [currentView, setCurrentView] = useState('home'); // home, patient-list, patient-dashboard, episode-workspace
  const [currentSection, setCurrentSection] = useState('subjective'); // subjective, objective, assessment, plan
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);
  
  // Navigation history for breadcrumbs
  const [navigationHistory, setNavigationHistory] = useState([]);
  
  // SOAP section progress tracking
  const [sectionProgress, setSectionProgress] = useState({
    subjective: 'empty',
    objective: 'empty',
    assessment: 'empty',
    plan: 'empty'
  });

  // Navigate to a view
  const navigateTo = useCallback((view) => {
    setNavigationHistory(prev => [...prev, { view: currentView, timestamp: new Date().toISOString() }]);
    setCurrentView(view);
    
    // Reset section to subjective when entering episode workspace
    if (view === 'episode-workspace') {
      setCurrentSection('subjective');
    }
  }, [currentView]);
  // Navigate back
  const navigateBack = useCallback(() => {
    if (navigationHistory.length > 0) {
      const previous = navigationHistory[navigationHistory.length - 1];
      setNavigationHistory(prev => prev.slice(0, -1));
      setCurrentView(previous.view);
    } else {
      setCurrentView('home');
    }
  }, [navigationHistory]);

  // Update section progress
  const updateSectionProgress = useCallback((section, status) => {
    setSectionProgress(prev => ({
      ...prev,
      [section]: status // 'empty', 'partial', 'complete'
    }));
  }, []);

  // Calculate overall progress
  const getOverallProgress = useCallback(() => {
    const sections = Object.values(sectionProgress);
    const complete = sections.filter(s => s === 'complete').length;
    const partial = sections.filter(s => s === 'partial').length;
    const total = sections.length;
    
    return {
      percentage: Math.round(((complete * 100) + (partial * 50)) / total),
      complete,
      partial,
      empty: sections.filter(s => s === 'empty').length
    };
  }, [sectionProgress]);

  // Navigate between SOAP sections
  const navigateToSection = useCallback((section) => {
    setCurrentSection(section);
  }, []);

  // Get next/previous section
  const getAdjacentSection = useCallback((direction) => {
    const sections = ['subjective', 'objective', 'assessment', 'plan'];
    const currentIndex = sections.indexOf(currentSection);
    
    if (direction === 'next' && currentIndex < sections.length - 1) {
      return sections[currentIndex + 1];
    } else if (direction === 'previous' && currentIndex > 0) {
      return sections[currentIndex - 1];
    }
    
    return null;
  }, [currentSection]);

  // Check if can navigate to section
  const canNavigateToSection = useCallback(() => {
    // In flexible navigation, always allow navigation
    return true;
  }, []);

  // Toggle sidebar
  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed(prev => !prev);
  }, []);

  // Toggle right panel
  const toggleRightPanel = useCallback(() => {
    setRightPanelOpen(prev => !prev);
  }, []);

  // Get breadcrumb trail
  const getBreadcrumbs = useCallback(() => {
    const breadcrumbs = [];
    
    // Always start with home
    breadcrumbs.push({ label: 'Home', view: 'home' });
    
    switch (currentView) {
      case 'patient-list':
        breadcrumbs.push({ label: 'Patients', view: 'patient-list' });
        break;
      case 'patient-dashboard':
        breadcrumbs.push({ label: 'Patients', view: 'patient-list' });
        breadcrumbs.push({ label: 'Patient Dashboard', view: 'patient-dashboard' });
        break;
      case 'episode-workspace':
        breadcrumbs.push({ label: 'Patients', view: 'patient-list' });
        breadcrumbs.push({ label: 'Patient Dashboard', view: 'patient-dashboard' });
        breadcrumbs.push({ label: 'Episode', view: 'episode-workspace' });
        break;
    }
    
    return breadcrumbs;
  }, [currentView]);

  const value = {
    currentView,
    currentSection,
    sidebarCollapsed,
    rightPanelOpen,
    navigationHistory,
    sectionProgress,
    navigateTo,
    navigateBack,
    updateSectionProgress,
    getOverallProgress,
    navigateToSection,
    getAdjacentSection,
    canNavigateToSection,
    toggleSidebar,
    toggleRightPanel,
    getBreadcrumbs
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
};