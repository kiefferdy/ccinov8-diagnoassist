import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { PatientProvider } from './contexts/PatientContext';
import { EpisodeProvider } from './contexts/EpisodeContext';
import { EncounterProvider } from './contexts/EncounterContext';
import { NavigationProvider } from './contexts/NavigationContext';

// Import components
import Home from './components/Home/Home';
import PatientList from './components/PatientManagement/PatientList';
import PatientDashboard from './components/Dashboard/PatientDashboard';
import EpisodeWorkspace from './components/Episode/EpisodeWorkspace';
import LandingPage from './components/LandingPage/LandingPage';

function AppProviders({ children }) {
  return (
    <NavigationProvider>
      <PatientProvider>
        <EpisodeProvider>
          <EncounterProvider>
            {children}
          </EncounterProvider>
        </EpisodeProvider>
      </PatientProvider>
    </NavigationProvider>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/" element={
          <AppProviders>
            <Home />
          </AppProviders>
        } />
        <Route path="/patients" element={
          <AppProviders>
            <PatientList />
          </AppProviders>
        } />
        <Route path="/patient/:patientId" element={
          <AppProviders>
            <PatientDashboard />
          </AppProviders>
        } />
        <Route path="/patient/:patientId/episode/:episodeId" element={
          <AppProviders>
            <EpisodeWorkspace />
          </AppProviders>
        } />
      </Routes>
    </Router>
  );
}

export default App;