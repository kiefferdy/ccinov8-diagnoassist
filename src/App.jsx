import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { PatientDataProvider } from './context/PatientDataContext'
import LandingPage from './components/Landing/LandingPage'
import Layout from './components/Layout/Layout'
import PatientInfo from './components/PatientInfo/PatientInfo'
import PhysicalExam from './components/PhysicalExam/PhysicalExam'
import DiagnosticAnalysis from './components/DiagnosticAnalysis/DiagnosticAnalysis'
import RecommendedTests from './components/RecommendedTests/RecommendedTests'
import TestResults from './components/TestResults/TestResults'
import FinalDiagnosis from './components/FinalDiagnosis/FinalDiagnosis'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app/*" element={
          <PatientDataProvider>
            <Layout>
              <Routes>
                <Route path="patient-info" element={<PatientInfo />} />
                <Route path="physical-exam" element={<PhysicalExam />} />
                <Route path="diagnostic-analysis" element={<DiagnosticAnalysis />} />
                <Route path="recommended-tests" element={<RecommendedTests />} />
                <Route path="test-results" element={<TestResults />} />
                <Route path="final-diagnosis" element={<FinalDiagnosis />} />
              </Routes>
            </Layout>
          </PatientDataProvider>
        } />
      </Routes>
    </Router>
  )
}

export default App
