// Helper functions for DiagnoAssist

export const formatDate = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const formatTime = (dateString) => {
  if (!dateString) return 'Not set'
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const calculateAge = (birthDate) => {
  const today = new Date()
  const birth = new Date(birthDate)
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  
  return age
}

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export const validatePhone = (phone) => {
  const re = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/
  return re.test(phone)
}

export const getBMICategory = (bmi) => {
  const bmiNum = parseFloat(bmi)
  if (isNaN(bmiNum)) return { category: 'Unknown', color: 'text-gray-600' }
  
  if (bmiNum < 18.5) return { category: 'Underweight', color: 'text-blue-600' }
  if (bmiNum < 25) return { category: 'Normal', color: 'text-green-600' }
  if (bmiNum < 30) return { category: 'Overweight', color: 'text-yellow-600' }
  return { category: 'Obese', color: 'text-red-600' }
}

export const getVitalSignStatus = (type, value) => {
  const val = parseFloat(value)
  if (isNaN(val)) return { status: 'unknown', color: 'text-gray-600' }
  
  switch (type) {
    case 'heartRate':
      if (val >= 60 && val <= 100) return { status: 'normal', color: 'text-green-600' }
      if (val < 60) return { status: 'low', color: 'text-blue-600' }
      return { status: 'high', color: 'text-red-600' }
      
    case 'temperature':
      if (val >= 36.1 && val <= 37.2) return { status: 'normal', color: 'text-green-600' }
      if (val < 36.1) return { status: 'low', color: 'text-blue-600' }
      return { status: 'high', color: 'text-red-600' }
      
    case 'respiratoryRate':
      if (val >= 12 && val <= 20) return { status: 'normal', color: 'text-green-600' }
      if (val < 12) return { status: 'low', color: 'text-blue-600' }
      return { status: 'high', color: 'text-red-600' }
      
    case 'oxygenSaturation':
      if (val >= 95) return { status: 'normal', color: 'text-green-600' }
      if (val >= 90) return { status: 'low', color: 'text-yellow-600' }
      return { status: 'critical', color: 'text-red-600' }
      
    default:
      return { status: 'unknown', color: 'text-gray-600' }
  }
}

export const generatePatientSummary = (patient, chiefComplaint, physicalExam) => {
  const age = patient.age ? `${patient.age}-year-old` : ''
  const gender = patient.gender ? patient.gender.toLowerCase() : ''
  const name = patient.name || 'Patient'
  
  return `${name} is a ${age} ${gender} presenting with ${chiefComplaint || 'chief complaint to be determined'}.`
}

export const exportToCSV = (data, filename) => {
  const csvContent = "data:text/csv;charset=utf-8," 
    + data.map(row => row.join(",")).join("\n")
  
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substr(0, maxLength) + '...'
}

export const capitalizeFirst = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}