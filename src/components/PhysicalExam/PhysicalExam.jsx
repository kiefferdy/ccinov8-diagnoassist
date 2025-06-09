import { useEffect } from 'react'
import { usePatientData } from '../../context/PatientDataContext'
import { Activity, Heart, Thermometer, Scale, Ruler, Users } from 'lucide-react'

export default function PhysicalExam() {
  const { physicalExam, updatePhysicalExam, updateVitalSigns } = usePatientData()

  const calculateBMI = (height, weight) => {
    if (height && weight && height > 0 && weight > 0) {
      const heightInM = height / 100
      const bmi = weight / (heightInM * heightInM)
      return bmi.toFixed(1)
    }
    return ''
  }

  useEffect(() => {
    const { height, weight } = physicalExam.vitalSigns
    const bmi = calculateBMI(height, weight)
    if (bmi && bmi !== physicalExam.vitalSigns.bmi) {
      updateVitalSigns({ bmi })
    }
  }, [physicalExam.vitalSigns.height, physicalExam.vitalSigns.weight])

  const handleVitalSignChange = (field, value) => {
    updateVitalSigns({ [field]: value })
  }

  const handlePhysicalExamChange = (field, value) => {
    updatePhysicalExam({ [field]: value })
  }

  const getBMICategory = (bmi) => {
    const bmiNum = parseFloat(bmi)
    if (bmiNum < 18.5) return { category: 'Underweight', color: 'text-blue-600' }
    if (bmiNum < 25) return { category: 'Normal', color: 'text-green-600' }
    if (bmiNum < 30) return { category: 'Overweight', color: 'text-yellow-600' }
    return { category: 'Obese', color: 'text-red-600' }
  }

  const vitalSignsRanges = {
    heartRate: { normal: '60-100 bpm', label: 'Normal: 60-100 bpm' },
    bloodPressure: { normal: '<140/90 mmHg', label: 'Normal: <140/90 mmHg' },
    temperature: { normal: '36.1-37.2°C', label: 'Normal: 36.1-37.2°C (97-99°F)' },
    respiratoryRate: { normal: '12-20/min', label: 'Normal: 12-20 breaths/min' },
    oxygenSaturation: { normal: '>95%', label: 'Normal: >95%' },
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Physical Examination</h2>
        <p className="mt-2 text-gray-600">
          Record objective findings from the physical examination
        </p>
      </div>

      {/* Vital Signs */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Activity className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Vital Signs</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Blood Pressure (mmHg)
            </label>
            <input
              type="text"
              value={physicalExam.vitalSigns.bloodPressure}
              onChange={(e) => handleVitalSignChange('bloodPressure', e.target.value)}
              className="input-field"
              placeholder="120/80"
            />
            <p className="text-xs text-gray-500 mt-1">{vitalSignsRanges.bloodPressure.label}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Heart Rate (bpm)
            </label>
            <input
              type="number"
              value={physicalExam.vitalSigns.heartRate}
              onChange={(e) => handleVitalSignChange('heartRate', e.target.value)}
              className="input-field"
              placeholder="72"
              min="0"
              max="300"
            />
            <p className="text-xs text-gray-500 mt-1">{vitalSignsRanges.heartRate.label}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperature (°C)
            </label>
            <input
              type="number"
              step="0.1"
              value={physicalExam.vitalSigns.temperature}
              onChange={(e) => handleVitalSignChange('temperature', e.target.value)}
              className="input-field"
              placeholder="36.5"
              min="30"
              max="45"
            />
            <p className="text-xs text-gray-500 mt-1">{vitalSignsRanges.temperature.label}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Respiratory Rate (/min)
            </label>
            <input
              type="number"
              value={physicalExam.vitalSigns.respiratoryRate}
              onChange={(e) => handleVitalSignChange('respiratoryRate', e.target.value)}
              className="input-field"
              placeholder="16"
              min="0"
              max="100"
            />
            <p className="text-xs text-gray-500 mt-1">{vitalSignsRanges.respiratoryRate.label}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Oxygen Saturation (%)
            </label>
            <input
              type="number"
              value={physicalExam.vitalSigns.oxygenSaturation}
              onChange={(e) => handleVitalSignChange('oxygenSaturation', e.target.value)}
              className="input-field"
              placeholder="98"
              min="0"
              max="100"
            />
            <p className="text-xs text-gray-500 mt-1">{vitalSignsRanges.oxygenSaturation.label}</p>
          </div>
        </div>
      </div>

      {/* Anthropometric Measurements */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Scale className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Anthropometric Measurements</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Height (cm)
            </label>
            <input
              type="number"
              value={physicalExam.vitalSigns.height}
              onChange={(e) => handleVitalSignChange('height', e.target.value)}
              className="input-field"
              placeholder="170"
              min="0"
              max="300"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Weight (kg)
            </label>
            <input
              type="number"
              step="0.1"
              value={physicalExam.vitalSigns.weight}
              onChange={(e) => handleVitalSignChange('weight', e.target.value)}
              className="input-field"
              placeholder="70"
              min="0"
              max="500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              BMI (kg/m²)
            </label>
            <div className="relative">
              <input
                type="text"
                value={physicalExam.vitalSigns.bmi}
                className="input-field bg-gray-50"
                placeholder="Calculated automatically"
                readOnly
              />
              {physicalExam.vitalSigns.bmi && (
                <div className="mt-1">
                  <span className={`text-xs font-medium ${getBMICategory(physicalExam.vitalSigns.bmi).color}`}>
                    {getBMICategory(physicalExam.vitalSigns.bmi).category}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* General Appearance */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Users className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">General Appearance</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Overall appearance and general condition
          </label>
          <textarea
            value={physicalExam.generalAppearance}
            onChange={(e) => handlePhysicalExamChange('generalAppearance', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Patient appears well-developed, well-nourished, alert and oriented..."
          />
        </div>
      </div>

      {/* System-specific Examinations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cardiovascular */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Heart className="w-5 h-5 text-red-500" />
            <h4 className="text-md font-semibold text-gray-900">Cardiovascular</h4>
          </div>
          <textarea
            value={physicalExam.cardiovascular}
            onChange={(e) => handlePhysicalExamChange('cardiovascular', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Heart sounds, murmurs, peripheral pulses, edema..."
          />
        </div>

        {/* Respiratory */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-5 h-5 text-blue-500" />
            <h4 className="text-md font-semibold text-gray-900">Respiratory</h4>
          </div>
          <textarea
            value={physicalExam.respiratory}
            onChange={(e) => handlePhysicalExamChange('respiratory', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Breath sounds, chest expansion, percussion..."
          />
        </div>

        {/* Gastrointestinal */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-5 h-5 bg-yellow-500 rounded-full"></div>
            <h4 className="text-md font-semibold text-gray-900">Gastrointestinal</h4>
          </div>
          <textarea
            value={physicalExam.gastrointestinal}
            onChange={(e) => handlePhysicalExamChange('gastrointestinal', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Abdominal inspection, palpation, bowel sounds..."
          />
        </div>

        {/* Neurological */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-5 h-5 bg-purple-500 rounded-full"></div>
            <h4 className="text-md font-semibold text-gray-900">Neurological</h4>
          </div>
          <textarea
            value={physicalExam.neurological}
            onChange={(e) => handlePhysicalExamChange('neurological', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Mental status, cranial nerves, motor/sensory function..."
          />
        </div>

        {/* Musculoskeletal */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-5 h-5 bg-green-500 rounded-full"></div>
            <h4 className="text-md font-semibold text-gray-900">Musculoskeletal</h4>
          </div>
          <textarea
            value={physicalExam.musculoskeletal}
            onChange={(e) => handlePhysicalExamChange('musculoskeletal', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Joint range of motion, muscle strength, deformities..."
          />
        </div>

        {/* Skin */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-5 h-5 bg-orange-500 rounded-full"></div>
            <h4 className="text-md font-semibold text-gray-900">Skin</h4>
          </div>
          <textarea
            value={physicalExam.skin}
            onChange={(e) => handlePhysicalExamChange('skin', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Color, temperature, moisture, lesions, rashes..."
          />
        </div>
      </div>

      {/* Other Findings */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Activity className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Other Findings</h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional physical examination findings
          </label>
          <textarea
            value={physicalExam.other}
            onChange={(e) => handlePhysicalExamChange('other', e.target.value)}
            className="input-field"
            rows={3}
            placeholder="Any other relevant physical examination findings..."
          />
        </div>
      </div>
    </div>
  )
}