import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { PatientProvider } from './contexts/PatientContext';
import { EpisodeProvider } from './contexts/EpisodeContext';
import { EncounterProvider } from './contexts/EncounterContext';
import { NavigationProvider } from './contexts/NavigationContext';
import { NotificationProvider } from './components/common/Notification';

// Import components
import DoctorDashboard from './components/Dashboard/DoctorDashboard';
import PatientList from './components/PatientManagement/PatientList';
import PatientDashboard from './components/Dashboard/PatientDashboard';
import EpisodeWorkspace from './components/Episode/EpisodeWorkspace';
import LandingPage from './components/LandingPage/LandingPage';
import Schedule from './components/Schedule/Schedule';
import Reports from './components/Reports/Reports';
import Profile from './components/Profile/Profile';
import NotificationsPage from './components/Notifications/NotificationsPage';

function AppProviders({ children }) {
  return (
    <NotificationProvider>
      <NavigationProvider>
        <PatientProvider>
          <EpisodeProvider>
            <EncounterProvider>
              {children}
            </EncounterProvider>
          </EpisodeProvider>
        </PatientProvider>
      </NavigationProvider>
    </NotificationProvider>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={
          <AppProviders>
            <DoctorDashboard />
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
        <Route path="/schedule" element={
          <AppProviders>
            <Schedule />
          </AppProviders>
        } />
        <Route path="/reports" element={
          <AppProviders>
            <Reports />
          </AppProviders>
        } />
        <Route path="/profile" element={
          <AppProviders>
            <Profile />
          </AppProviders>
        } />
        <Route path="/notifications" element={
          <AppProviders>
            <NotificationsPage />
          </AppProviders>
        } />
      </Routes>
    </Router>
  );
}

export default App;