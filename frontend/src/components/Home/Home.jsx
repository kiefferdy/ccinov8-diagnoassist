import React from 'react';
import { usePatient } from '../../contexts/PatientContext';
import { Activity, Users, Clock, ChartBar, ArrowRight, FolderOpen } from 'lucide-react';

const Home = () => {
  const { setCurrentStep } = usePatient();
  
  const handleNewPatient = () => {
    setCurrentStep('patient-selection');
  };
  
  const handlePatientList = () => {
    setCurrentStep('patient-list');
  };
  
  const stats = [
    { icon: Users, label: 'Patients Today', value: '12' },
    { icon: Clock, label: 'Avg. Diagnosis Time', value: '8 min' },
    { icon: ChartBar, label: 'Accuracy Rate', value: '94%' }
  ];
  
  const features = [
    {
      title: 'Dynamic Clinical Assessment',
      description: 'AI-powered questions that adapt based on patient responses for comprehensive data gathering'
    },
    {
      title: 'Intelligent Diagnosis',
      description: 'Advanced algorithms analyze symptoms, exam findings, and test results for accurate differential diagnoses'
    },
    {
      title: 'Evidence-Based Treatment',
      description: 'Get personalized treatment recommendations based on the latest medical guidelines and research'
    },
    {
      title: 'Seamless Workflow',
      description: 'Follows the natural clinical flow doctors use, enhancing rather than replacing medical expertise'
    }
  ];
  
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center">
            <Activity className="w-12 h-12 text-white" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to DiagnoAssist
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Your AI-powered diagnostic assistant that enhances clinical decision-making and improves patient care
        </p>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <Icon className="w-8 h-8 text-blue-600" />
                <span className="text-3xl font-bold text-gray-900">{stat.value}</span>
              </div>
              <p className="text-gray-600">{stat.label}</p>
            </div>
          );
        })}
      </div>
      
      {/* CTA Button */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={handleNewPatient}
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
          >
            Start New Patient Assessment
            <ArrowRight className="ml-3 w-6 h-6" />
          </button>
          <button
            onClick={handlePatientList}
            className="inline-flex items-center px-8 py-4 bg-gray-600 text-white text-lg font-medium rounded-xl hover:bg-gray-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
          >
            <FolderOpen className="mr-3 w-6 h-6" />
            View All Patients
          </button>
        </div>
      </div>
      
      {/* Features Grid */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          Designed for Modern Medical Practice
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <div key={index} className="bg-gradient-to-br from-blue-50 to-white rounded-xl p-6 border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Recent Patients (Mock) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Patients</h3>
        <div className="space-y-3">
          {[
            { name: 'John Smith', age: 45, diagnosis: 'Hypertension', time: '2 hours ago' },
            { name: 'Mary Johnson', age: 32, diagnosis: 'Acute Bronchitis', time: '3 hours ago' },
            { name: 'Robert Davis', age: 58, diagnosis: 'Type 2 Diabetes', time: '5 hours ago' }
          ].map((patient, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center mr-3">
                  <span className="text-sm font-medium text-gray-600">
                    {patient.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{patient.name}</p>
                  <p className="text-sm text-gray-600">{patient.age} years • {patient.diagnosis}</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">{patient.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
