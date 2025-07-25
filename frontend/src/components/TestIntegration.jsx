import React, { useState, useEffect } from 'react';
import { usePatient } from '../contexts/PatientContext';
import { useEpisode } from '../contexts/EpisodeContext';

const TestIntegration = () => {
  const { patients, loading: patientsLoading, error: patientsError, createPatient } = usePatient();
  const { episodes, loading: episodesLoading, error: episodesError, createEpisode, deleteEpisode } = useEpisode();
  const [testResult, setTestResult] = useState('');

  const handleTestCreatePatient = async () => {
    try {
      setTestResult('Creating test patient...');
      const testPatientData = {
        name: 'Frontend Test Patient',
        dateOfBirth: '1990-05-15',
        gender: 'Female',
        email: 'frontend.test@example.com',
        phone: '555-0199',
        address: '456 Frontend Ave'
      };
      
      const newPatient = await createPatient(testPatientData);
      setTestResult(`✅ Successfully created patient: ${newPatient.demographics.name} (ID: ${newPatient.id})`);
    } catch (error) {
      setTestResult(`❌ Failed to create patient: ${error.message}`);
    }
  };

  const handleTestCreateEpisode = async () => {
    if (patients.length === 0) {
      setTestResult('❌ No patients available to create episode for');
      return;
    }

    try {
      setTestResult('Creating test episode...');
      const firstPatient = patients[0];
      const testEpisodeData = {
        chiefComplaint: 'Frontend integration test episode',
        category: 'acute',
        tags: ['test', 'integration']
      };
      
      const newEpisode = await createEpisode(firstPatient.id, testEpisodeData);
      setTestResult(`✅ Successfully created episode: ${newEpisode.chiefComplaint} (ID: ${newEpisode.id})`);
    } catch (error) {
      setTestResult(`❌ Failed to create episode: ${error.message}`);
    }
  };

  const handleTestDeleteEpisode = async () => {
    if (episodes.length === 0) {
      setTestResult('❌ No episodes available to delete');
      return;
    }

    try {
      setTestResult('Testing episode deletion...');
      const episodeToDelete = episodes[0]; // Delete the first episode
      console.log('Attempting to delete episode:', episodeToDelete.id);
      
      await deleteEpisode(episodeToDelete.id);
      setTestResult(`✅ Successfully deleted episode: ${episodeToDelete.chiefComplaint} (ID: ${episodeToDelete.id})`);
    } catch (error) {
      console.error('Delete test failed:', error);
      setTestResult(`❌ Failed to delete episode: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Frontend-Backend Integration Test</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Patients Data</h3>
        <p>Loading: {patientsLoading ? 'Yes' : 'No'}</p>
        <p>Error: {patientsError || 'None'}</p>
        <p>Count: {patients.length}</p>
        {patients.length > 0 && (
          <div>
            <p>Sample Patient:</p>
            <pre style={{ background: '#f5f5f5', padding: '10px', fontSize: '12px' }}>
              {JSON.stringify(patients[0], null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Episodes Data</h3>
        <p>Loading: {episodesLoading ? 'Yes' : 'No'}</p>
        <p>Error: {episodesError || 'None'}</p>
        <p>Count: {episodes.length}</p>
        {episodes.length > 0 && (
          <div>
            <p>Sample Episode:</p>
            <pre style={{ background: '#f5f5f5', padding: '10px', fontSize: '12px' }}>
              {JSON.stringify(episodes[0], null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Test Operations</h3>
        <button onClick={handleTestCreatePatient} style={{ margin: '5px', padding: '10px' }}>
          Test Create Patient
        </button>
        <button onClick={handleTestCreateEpisode} style={{ margin: '5px', padding: '10px' }}>
          Test Create Episode
        </button>
        <button onClick={handleTestDeleteEpisode} style={{ margin: '5px', padding: '10px' }}>
          Test Delete Episode
        </button>
        <div style={{ marginTop: '10px', padding: '10px', background: '#f0f0f0' }}>
          <strong>Result:</strong> {testResult}
        </div>
      </div>
    </div>
  );
};

export default TestIntegration;