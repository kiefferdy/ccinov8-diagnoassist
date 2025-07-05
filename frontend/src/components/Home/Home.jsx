import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Users, Clock, ChartBar, ArrowRight, Plus } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  
  const handleNewPatient = () => {
    navigate('/patients');
  };
  
  const handlePatientList = () => {
    navigate('/patients');
  };
  
  const stats = [
    { icon: Users, label: 'Active Patients', value: '24' },
    { icon: Clock, label: 'Avg. Documentation Time', value: '6 min' },
    { icon: ChartBar, label: 'Episodes This Month', value: '142' }
  ];
  
  const quickActions = [
    {
      title: 'Start New Episode',
      description: 'Begin documenting a new patient visit',
      icon: Plus,
      action: handleNewPatient,
      color: 'blue'
    },
    {
      title: 'Patient List',
      description: 'View and manage all patients',
      icon: Users,
      action: handlePatientList,
      color: 'green'
    }
  ];
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Activity className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            DiagnoAssist
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Episode-based clinical documentation with integrated SOAP workflow
          </p>
        </div>
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-gray-600" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className={`bg-white rounded-xl shadow-sm p-8 border border-gray-200 hover:shadow-md transition-all group text-left`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-14 h-14 bg-${action.color}-100 rounded-xl flex items-center justify-center group-hover:bg-${action.color}-200 transition-colors`}>
                    <action.icon className={`w-7 h-7 text-${action.color}-600`} />
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h3>
                <p className="text-gray-600">{action.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Episode-Based Documentation</h3>
              <p className="text-gray-600">Track patient health issues over time with linked episodes and encounters</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Flexible SOAP Workflow</h3>
              <p className="text-gray-600">Navigate freely between sections with auto-save and progress tracking</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Integrated Clinical Tools</h3>
              <p className="text-gray-600">Order tests, view results, and manage diagnoses all within the SOAP framework</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Assistance</h3>
              <p className="text-gray-600">Get intelligent suggestions and clinical insights when you need them</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;