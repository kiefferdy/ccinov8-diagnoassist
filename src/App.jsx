import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { PatientDataProvider } from './context/PatientDataContext'
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
      <PatientDataProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/patient-info" replace />} />
            <Route path="/patient-info" element={<PatientInfo />} />
            <Route path="/physical-exam" element={<PhysicalExam />} />
            <Route path="/diagnostic-analysis" element={<DiagnosticAnalysis />} />
            <Route path="/recommended-tests" element={<RecommendedTests />} />
            <Route path="/test-results" element={<TestResults />} />
            <Route path="/final-diagnosis" element={<FinalDiagnosis />} />
          </Routes>
        </Layout>
      </PatientDataProvider>
    </Router>
  )
}

export default App
