import React, { useState, useEffect } from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { 
  TestTube, 
  ChevronRight, 
  ChevronLeft,
  Plus,
  Check,
  X,
  Info,
  Filter,
  ArrowUpDown,
  AlertCircle,
  Edit3,
  FileText,
  Brain,
  Search
} from 'lucide-react';

const RecommendedTests = () => {
  const { patientData, updatePatientData, setCurrentStep } = usePatient();
  const [recommendedTests, setRecommendedTests] = useState([]);
  const [selectedTests, setSelectedTests] = useState([]);
  const [showCustomTestModal, setShowCustomTestModal] = useState(false);
  const [customTest, setCustomTest] = useState({
    name: '',
    category: 'Other',
    priority: 'medium',
    purpose: '',
    expectedFindings: '',
    turnaroundTime: '',
    specialInstructions: ''
  });
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [sortBy, setSortBy] = useState('priority');
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    // Extract unique tests from all diagnoses
    const allTests = new Set();
    const testsMap = new Map();
    
    patientData.differentialDiagnoses.forEach(diagnosis => {
      diagnosis.recommendedTests?.forEach(test => {
        if (!testsMap.has(test)) {
          testsMap.set(test, {
            name: test,
            diagnoses: [diagnosis.name],
            diagnosisProbabilities: [diagnosis.probability]
          });
        } else {
          const existing = testsMap.get(test);
          existing.diagnoses.push(diagnosis.name);
          existing.diagnosisProbabilities.push(diagnosis.probability);
        }
      });
    });
    
    const testsArray = Array.from(testsMap.entries()).map(([testName, testInfo], index) => ({
      id: index + 1,
      name: testName,
      category: categorizeTest(testName),
      priority: calculatePriority(testInfo),
      status: 'pending',
      relevantDiagnoses: testInfo.diagnoses,
      maxProbability: Math.max(...testInfo.diagnosisProbabilities),
      purpose: generateTestPurpose(testName, testInfo.diagnoses),
      expectedFindings: generateExpectedFindings(testName),
      turnaroundTime: estimateTurnaroundTime(testName)
    }));
    
    setRecommendedTests(testsArray);
    updatePatientData('recommendedTests', testsArray);
  }, []);
  
  const categorizeTest = (testName) => {
    const categories = {
      'Blood': ['CBC', 'Blood Culture', 'Complete Blood Count', 'Blood Gas', 'Electrolytes', 'Hemoglobin', 'Platelet'],
      'Imaging': ['X-ray', 'CT', 'MRI', 'Ultrasound', 'Chest X-ray', 'Echocardiogram', 'Angiography'],
      'Microbiology': ['Culture', 'Sputum', 'Urine Culture', 'Gram Stain'],
      'Chemistry': ['Glucose', 'Creatinine', 'Liver Function', 'Lipid Panel', 'BUN', 'ALT', 'AST'],
      'Cardiac': ['ECG', 'EKG', 'Troponin', 'BNP', 'Stress Test'],
      'Endocrine': ['TSH', 'T3', 'T4', 'Cortisol', 'HbA1c'],
      'Other': []
    };
    
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => testName.toLowerCase().includes(keyword.toLowerCase()))) {
        return category;
      }
    }
    return 'Other';
  };
  
  const calculatePriority = (testInfo) => {
    const maxProb = Math.max(...testInfo.diagnosisProbabilities);
    if (maxProb >= 0.7) return 'high';
    if (maxProb >= 0.4) return 'medium';
    return 'low';
  };
  
  const generateTestPurpose = (testName, diagnoses) => {
    const purposes = {
      'CBC': 'Evaluate blood cell counts to assess for infection, anemia, or other blood disorders',
      'Chest X-ray': 'Visualize lung fields and heart size to identify abnormalities',
      'ECG': 'Assess heart rhythm and electrical activity',
      'Blood Culture': 'Identify bacterial infections in the bloodstream'
    };
    
    return purposes[testName] || `Help differentiate between ${diagnoses.slice(0, 2).join(' and ')}`;
  };
  
  const generateExpectedFindings = (testName) => {
    const findings = {
      'CBC': 'May show elevated WBC (infection), low hemoglobin (anemia), or abnormal platelet count',
      'Chest X-ray': 'Could reveal infiltrates, consolidation, or cardiomegaly',
      'ECG': 'May demonstrate arrhythmias, ischemic changes, or conduction abnormalities',
      'Blood Culture': 'Positive growth would indicate bacteremia'
    };
    
    return findings[testName] || 'Results will help narrow differential diagnosis';
  };
  
  const estimateTurnaroundTime = (testName) => {
    const times = {
      'CBC': '1-2 hours',
      'Basic Metabolic Panel': '2-4 hours',
      'Blood Culture': '24-72 hours',
      'Chest X-ray': '30 minutes',
      'CT': '1-2 hours',
      'MRI': '2-4 hours'
    };
    
    for (const [test, time] of Object.entries(times)) {
      if (testName.includes(test)) return time;
    }
    return '2-6 hours';
  };
  
  const handleSelectTest = (test) => {
    if (!selectedTests.find(t => t.id === test.id)) {
      const updatedTest = { ...test, selectedAt: new Date().toISOString() };
      setSelectedTests([...selectedTests, updatedTest]);
      updatePatientData('selectedTests', [...selectedTests, updatedTest]);
    }
  };
  
  const handleDeselectTest = (testId) => {
    const filtered = selectedTests.filter(t => t.id !== testId);
    setSelectedTests(filtered);
    updatePatientData('selectedTests', filtered);
  };
  
  const handleAddCustomTest = () => {
    if (customTest.name.trim()) {
      const newTest = {
        id: recommendedTests.length + 1000, // Ensure unique ID
        ...customTest,
        status: 'pending',
        isCustom: true,
        relevantDiagnoses: ['Custom Test'],
        maxProbability: 0.5
      };
      
      setRecommendedTests([...recommendedTests, newTest]);
      setCustomTest({
        name: '',
        category: 'Other',
        priority: 'medium',
        purpose: '',
        expectedFindings: '',
        turnaroundTime: '',
        specialInstructions: ''
      });
      setShowCustomTestModal(false);
    }
  };
  
  const filteredAndSortedTests = () => {
    let tests = [...recommendedTests];
    
    // Filter by search term
    if (searchTerm) {
      tests = tests.filter(test => 
        test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        test.purpose.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filter by category
    if (filterCategory !== 'all') {
      tests = tests.filter(test => test.category === filterCategory);
    }
    
    // Filter by priority
    if (filterPriority !== 'all') {
      tests = tests.filter(test => test.priority === filterPriority);
    }
    
    // Sort
    tests.sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        case 'name':
          return a.name.localeCompare(b.name);
        case 'probability':
          return b.maxProbability - a.maxProbability;
        default:
          return 0;
      }
    });
    
    return tests;
  };
  
  const handleContinue = () => {
    if (selectedTests.length > 0) {
      setCurrentStep('test-results');
    }
  };
  
  const handleBack = () => {
    setCurrentStep('diagnostic-analysis');
  };
  
  const isTestSelected = (testId) => {
    return selectedTests.some(t => t.id === testId);
  };
  
  const categories = ['all', 'Blood', 'Imaging', 'Microbiology', 'Chemistry', 'Cardiac', 'Endocrine', 'Other'];
  const priorities = ['all', 'high', 'medium', 'low'];
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Recommended Laboratory Tests</h2>
        <p className="text-gray-600">Select the tests that would be most helpful for diagnosis</p>
      </div>
      
      {/* Selected Tests Summary */}
      {selectedTests.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <p className="text-sm font-medium text-blue-900">
            Selected Tests: {selectedTests.length}
          </p>
          <div className="flex flex-wrap gap-2 mt-2">
            {selectedTests.map(test => (
              <span key={test.id} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                {test.name}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Filters and Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="Search tests..."
              />
            </div>
          </div>
          
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Filter className="inline w-4 h-4 mr-1" />
              Category
            </label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat}
                </option>
              ))}
            </select>
          </div>
          
          {/* Priority Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <AlertCircle className="inline w-4 h-4 mr-1" />
              Priority
            </label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {priorities.map(priority => (
                <option key={priority} value={priority}>
                  {priority === 'all' ? 'All Priorities' : priority.charAt(0).toUpperCase() + priority.slice(1)}
                </option>
              ))}
            </select>
          </div>
          
          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <ArrowUpDown className="inline w-4 h-4 mr-1" />
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              <option value="priority">Priority</option>
              <option value="name">Name</option>
              <option value="probability">Relevance</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setShowCustomTestModal(true)}
            className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors flex items-center"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Custom Test
          </button>
        </div>
      </div>
      
      {/* Test Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {filteredAndSortedTests().map(test => {
          const isSelected = isTestSelected(test.id);
          
          return (
            <div
              key={test.id}
              className={`bg-white rounded-xl shadow-sm border-2 p-5 transition-all ${
                isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <TestTube className="w-5 h-5 text-blue-600 mr-2" />
                    <h4 className="font-semibold text-gray-900">{test.name}</h4>
                    {test.isCustom && (
                      <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Custom</span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      test.category === 'Blood' ? 'bg-red-100 text-red-700' :
                      test.category === 'Imaging' ? 'bg-blue-100 text-blue-700' :
                      test.category === 'Microbiology' ? 'bg-green-100 text-green-700' :
                      test.category === 'Chemistry' ? 'bg-yellow-100 text-yellow-700' :
                      test.category === 'Cardiac' ? 'bg-pink-100 text-pink-700' :
                      test.category === 'Endocrine' ? 'bg-purple-100 text-purple-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {test.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      test.priority === 'high' ? 'bg-red-100 text-red-700' :
                      test.priority === 'medium' ? 'bg-orange-100 text-orange-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {test.priority} priority
                    </span>
                    <span className="text-xs text-gray-500">
                      ~{test.turnaroundTime}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Purpose:</span>
                      <p className="text-gray-600">{test.purpose}</p>
                    </div>
                    
                    <div>
                      <span className="font-medium text-gray-700">Expected Findings:</span>
                      <p className="text-gray-600">{test.expectedFindings}</p>
                    </div>
                    
                    {!test.isCustom && test.relevantDiagnoses && (
                      <div>
                        <span className="font-medium text-gray-700">Relevant for:</span>
                        <p className="text-gray-600">{test.relevantDiagnoses.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => isSelected ? handleDeselectTest(test.id) : handleSelectTest(test)}
                  className={`ml-3 p-2 rounded-lg transition-colors ${
                    isSelected 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {isSelected ? <Check className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                </button>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Custom Test Modal */}
      {showCustomTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Custom Test</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Test Name *
                </label>
                <input
                  type="text"
                  value={customTest.name}
                  onChange={(e) => setCustomTest({ ...customTest, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Specialized Antibody Panel"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={customTest.category}
                  onChange={(e) => setCustomTest({ ...customTest, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.filter(cat => cat !== 'all').map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  value={customTest.priority}
                  onChange={(e) => setCustomTest({ ...customTest, priority: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Purpose / Justification
                </label>
                <textarea
                  value={customTest.purpose}
                  onChange={(e) => setCustomTest({ ...customTest, purpose: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Why is this test needed?"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Findings
                </label>
                <textarea
                  value={customTest.expectedFindings}
                  onChange={(e) => setCustomTest({ ...customTest, expectedFindings: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="What results might we see?"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Turnaround Time
                </label>
                <input
                  type="text"
                  value={customTest.turnaroundTime}
                  onChange={(e) => setCustomTest({ ...customTest, turnaroundTime: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 2-3 days"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Special Instructions
                </label>
                <textarea
                  value={customTest.specialInstructions}
                  onChange={(e) => setCustomTest({ ...customTest, specialInstructions: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Any special preparation or handling requirements?"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowCustomTestModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddCustomTest}
                disabled={!customTest.name.trim()}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300"
              >
                Add Test
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Info Message */}
      {selectedTests.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-yellow-800 font-medium">Please select at least one test to proceed</p>
              <p className="text-yellow-700 text-sm mt-1">
                The selected tests will help confirm or rule out the differential diagnoses. Choose tests based on their clinical relevance and the patient's condition.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <ChevronLeft className="mr-2 w-5 h-5" />
          Back
        </button>
        
        <button
          onClick={handleContinue}
          disabled={selectedTests.length === 0}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-all flex items-center disabled:bg-gray-300 shadow-sm hover:shadow-md"
        >
          Continue to Test Results
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default RecommendedTests;