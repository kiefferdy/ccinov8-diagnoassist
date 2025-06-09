import { useState, useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { TestTube, Clock, DollarSign, AlertTriangle, CheckCircle, Filter, Search } from 'lucide-react'
import clsx from 'clsx'

const mockRecommendedTests = [
  {
    id: 'chest-xray',
    name: 'Chest X-Ray',
    category: 'Imaging',
    urgency: 'high',
    estimatedCost: 150,
    estimatedTime: '15 min',
    reasoning: 'Essential to evaluate for pneumonia, consolidation, and rule out other pulmonary pathology given respiratory symptoms and physical exam findings.',
    relatedDiagnoses: ['Community-Acquired Pneumonia', 'Acute Bronchitis'],
    contraindications: [],
    preparation: 'No special preparation required',
    expectedFindings: 'Look for consolidation, infiltrates, pleural effusion'
  },
  {
    id: 'cbc-diff',
    name: 'Complete Blood Count with Differential',
    category: 'Laboratory',
    urgency: 'high',
    estimatedCost: 45,
    estimatedTime: '30 min',
    reasoning: 'Evaluate for infection (elevated WBC with left shift) and assess overall hematologic status.',
    relatedDiagnoses: ['Community-Acquired Pneumonia', 'Acute Bronchitis'],
    contraindications: [],
    preparation: 'No fasting required',
    expectedFindings: 'Elevated WBC count, possible left shift indicating bacterial infection'
  },
  {
    id: 'basic-metabolic',
    name: 'Basic Metabolic Panel',
    category: 'Laboratory',
    urgency: 'medium',
    estimatedCost: 35,
    estimatedTime: '30 min',
    reasoning: 'Assess electrolyte balance and kidney function, especially important if patient is dehydrated from fever.',
    relatedDiagnoses: ['Community-Acquired Pneumonia'],
    contraindications: [],
    preparation: 'No fasting required',
    expectedFindings: 'May show dehydration, electrolyte imbalances'
  },
  {
    id: 'blood-cultures',
    name: 'Blood Cultures x2',
    category: 'Laboratory',
    urgency: 'high',
    estimatedCost: 120,
    estimatedTime: '24-48 hours',
    reasoning: 'Identify causative organism in suspected pneumonia, guide antibiotic selection.',
    relatedDiagnoses: ['Community-Acquired Pneumonia'],
    contraindications: [],
    preparation: 'Draw before antibiotic administration',
    expectedFindings: 'May isolate causative bacterial pathogen'
  },
  {
    id: 'arterial-blood-gas',
    name: 'Arterial Blood Gas',
    category: 'Laboratory',
    urgency: 'medium',
    estimatedCost: 85,
    estimatedTime: '15 min',
    reasoning: 'Assess oxygenation and acid-base status if respiratory compromise is suspected.',
    relatedDiagnoses: ['Community-Acquired Pneumonia', 'Pulmonary Embolism'],
    contraindications: ['Severe coagulopathy', 'No palpable pulse'],
    preparation: 'Patient should be on room air for 20 minutes if possible',
    expectedFindings: 'May show hypoxemia, respiratory alkalosis or acidosis'
  },
  {
    id: 'ct-chest',
    name: 'CT Chest with Contrast',
    category: 'Imaging',
    urgency: 'low',
    estimatedCost: 800,
    estimatedTime: '45 min',
    reasoning: 'Consider if chest X-ray is inconclusive or if PE is suspected. Can provide detailed lung parenchymal evaluation.',
    relatedDiagnoses: ['Pulmonary Embolism', 'Lung Cancer'],
    contraindications: ['Contrast allergy', 'Severe kidney disease'],
    preparation: 'NPO 4 hours, check creatinine',
    expectedFindings: 'Detailed evaluation of lung parenchyma, vessels'
  },
  {
    id: 'procalcitonin',
    name: 'Procalcitonin',
    category: 'Laboratory',
    urgency: 'medium',
    estimatedCost: 65,
    estimatedTime: '60 min',
    reasoning: 'Distinguish bacterial from viral infection, guide antibiotic therapy decisions.',
    relatedDiagnoses: ['Community-Acquired Pneumonia', 'Acute Bronchitis'],
    contraindications: [],
    preparation: 'No special preparation',
    expectedFindings: 'Elevated levels suggest bacterial infection'
  },
  {
    id: 'd-dimer',
    name: 'D-Dimer',
    category: 'Laboratory',
    urgency: 'medium',
    estimatedCost: 55,
    estimatedTime: '45 min',
    reasoning: 'Rule out pulmonary embolism if clinically suspected, though has low specificity.',
    relatedDiagnoses: ['Pulmonary Embolism'],
    contraindications: [],
    preparation: 'No special preparation',
    expectedFindings: 'Elevated levels may suggest thromboembolism but low specificity'
  }
]

export default function RecommendedTests() {
  const { 
    initialDiagnosis,
    recommendedTests, 
    selectedTests, 
    setRecommendedTests, 
    setSelectedTests 
  } = usePatientData()
  
  const [filteredTests, setFilteredTests] = useState([])
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterUrgency, setFilterUrgency] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showJustification, setShowJustification] = useState({})

  useEffect(() => {
    if (!recommendedTests.length) {
      setRecommendedTests(mockRecommendedTests)
    }
  }, [])

  useEffect(() => {
    let filtered = recommendedTests

    if (filterCategory !== 'all') {
      filtered = filtered.filter(test => test.category.toLowerCase() === filterCategory)
    }

    if (filterUrgency !== 'all') {
      filtered = filtered.filter(test => test.urgency === filterUrgency)
    }

    if (searchTerm) {
      filtered = filtered.filter(test => 
        test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        test.reasoning.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredTests(filtered)
  }, [recommendedTests, filterCategory, filterUrgency, searchTerm])

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high':
        return 'text-red-700 bg-red-100 border-red-200'
      case 'medium':
        return 'text-yellow-700 bg-yellow-100 border-yellow-200'
      case 'low':
        return 'text-green-700 bg-green-100 border-green-200'
      default:
        return 'text-gray-700 bg-gray-100 border-gray-200'
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Laboratory':
        return <TestTube className="w-4 h-4" />
      case 'Imaging':
        return <div className="w-4 h-4 bg-blue-500 rounded"></div>
      default:
        return <div className="w-4 h-4 bg-gray-500 rounded"></div>
    }
  }

  const toggleTestSelection = (testId) => {
    if (selectedTests.includes(testId)) {
      setSelectedTests(selectedTests.filter(id => id !== testId))
    } else {
      setSelectedTests([...selectedTests, testId])
    }
  }

  const toggleJustification = (testId) => {
    setShowJustification(prev => ({
      ...prev,
      [testId]: !prev[testId]
    }))
  }

  const getSelectedTestsInfo = () => {
    const selected = recommendedTests.filter(test => selectedTests.includes(test.id))
    const totalCost = selected.reduce((sum, test) => sum + test.estimatedCost, 0)
    return { count: selected.length, totalCost }
  }

  const selectedInfo = getSelectedTestsInfo()

  const categories = ['all', 'laboratory', 'imaging']
  const urgencies = ['all', 'high', 'medium', 'low']

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Recommended Diagnostic Tests</h2>
        <p className="mt-2 text-gray-600">
          AI-recommended tests to narrow down the differential diagnosis
        </p>
      </div>

      {/* Test Selection Summary */}
      {selectedInfo.count > 0 && (
        <div className="card bg-blue-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <CheckCircle className="w-6 h-6 text-blue-600" />
              <div>
                <h3 className="font-semibold text-blue-900">
                  {selectedInfo.count} test{selectedInfo.count !== 1 ? 's' : ''} selected
                </h3>
                <p className="text-blue-700 text-sm">
                  Total estimated cost: ${selectedInfo.totalCost}
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedTests([])}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Clear selection
            </button>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filter & Search Tests</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
              placeholder="Search tests..."
            />
          </div>
          
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="input-field"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
          
          <select
            value={filterUrgency}
            onChange={(e) => setFilterUrgency(e.target.value)}
            className="input-field"
          >
            {urgencies.map(urgency => (
              <option key={urgency} value={urgency}>
                {urgency === 'all' ? 'All Urgencies' : urgency.charAt(0).toUpperCase() + urgency.slice(1) + ' Priority'}
              </option>
            ))}
          </select>
          
          <div className="text-sm text-gray-600 flex items-center">
            <span>{filteredTests.length} tests shown</span>
          </div>
        </div>
      </div>

      {/* Test List */}
      <div className="space-y-4">
        {filteredTests.map((test) => {
          const isSelected = selectedTests.includes(test.id)
          const showDetails = showJustification[test.id]
          
          return (
            <div 
              key={test.id} 
              className={clsx(
                'card cursor-pointer transition-all duration-200 hover:shadow-md',
                isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : 'hover:bg-gray-50'
              )}
              onClick={() => toggleTestSelection(test.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="mt-1">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleTestSelection(test.id)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(test.category)}
                        <h4 className="text-lg font-semibold text-gray-900">{test.name}</h4>
                      </div>
                      
                      <span className={clsx(
                        'px-2 py-1 rounded-full text-xs font-medium border',
                        getUrgencyColor(test.urgency)
                      )}>
                        {test.urgency} priority
                      </span>
                      
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {test.category}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-3">{test.reasoning}</p>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{test.estimatedTime}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <DollarSign className="w-4 h-4" />
                        <span>${test.estimatedCost}</span>
                      </div>
                      {test.contraindications.length > 0 && (
                        <div className="flex items-center space-x-1 text-yellow-600">
                          <AlertTriangle className="w-4 h-4" />
                          <span>Contraindications</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleJustification(test.id)
                  }}
                  className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                >
                  {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
              </div>
              
              {showDetails && (
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Related Diagnoses</h5>
                      <div className="flex flex-wrap gap-1">
                        {test.relatedDiagnoses.map((diagnosis) => (
                          <span key={diagnosis} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            {diagnosis}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Expected Findings</h5>
                      <p className="text-sm text-gray-700">{test.expectedFindings}</p>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Preparation Required</h5>
                      <p className="text-sm text-gray-700">{test.preparation}</p>
                    </div>
                    
                    {test.contraindications.length > 0 && (
                      <div>
                        <h5 className="font-medium text-red-700 mb-2 flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          Contraindications
                        </h5>
                        <ul className="text-sm text-red-700 space-y-1">
                          {test.contraindications.map((contraindication, idx) => (
                            <li key={idx}>• {contraindication}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {filteredTests.length === 0 && (
        <div className="card text-center">
          <TestTube className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No tests found</h3>
          <p className="text-gray-600">Try adjusting your filters or search terms.</p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              const highPriorityTests = recommendedTests
                .filter(test => test.urgency === 'high')
                .map(test => test.id)
              setSelectedTests(highPriorityTests)
            }}
            className="btn-secondary text-sm"
          >
            Select All High Priority
          </button>
          <button
            onClick={() => {
              const labTests = recommendedTests
                .filter(test => test.category === 'Laboratory')
                .map(test => test.id)
              setSelectedTests(labTests)
            }}
            className="btn-secondary text-sm"
          >
            Select All Lab Tests
          </button>
          <button
            onClick={() => {
              const imagingTests = recommendedTests
                .filter(test => test.category === 'Imaging')
                .map(test => test.id)
              setSelectedTests(imagingTests)
            }}
            className="btn-secondary text-sm"
          >
            Select All Imaging
          </button>
        </div>
      </div>
    </div>
  )
}