import { useState } from 'react';
import StepNavigation from './components/StepNavigation';
import type { PatientInfo, MedicalHistory, PhysicalExam, Differential, TestItem } from './types';
import './App.css';

const steps = [
  'Patient Info',
  'History',
  'Exam',
  'Analysis',
  'Tests',
  'Diagnosis'
];

export default function App() {
  const [current, setCurrent] = useState(0);

  const [patientInfo, setPatientInfo] = useState<PatientInfo>({ chiefComplaint: '', details: '' });
  const [history, setHistory] = useState<MedicalHistory>({ history: '', observations: '' });
  const [exam, setExam] = useState<PhysicalExam>({ bloodPressure: '', heartRate: '', height: '', weight: '', other: '' });
  const [differentials] = useState<Differential[]>([
    { condition: 'Pneumonia', explanation: 'Inflammation of lung tissue due to infection.' },
    { condition: 'Tuberculosis', explanation: 'Chronic infection by Mycobacterium tuberculosis.' },
    { condition: 'COPD', explanation: 'Chronic obstructive pulmonary disease causing airflow limitation.' }
  ]);
  const [feedback, setFeedback] = useState('');
  const [tests, setTests] = useState<TestItem[]>([
    { name: 'Complete Blood Count', selected: false, result: '' },
    { name: 'Chest X-ray', selected: false, result: '' },
    { name: 'Sputum Culture', selected: false, result: '' }
  ]);
  const [finalDx, setFinalDx] = useState('');

  const next = () => setCurrent((c) => Math.min(c + 1, steps.length - 1));
  const prev = () => setCurrent((c) => Math.max(c - 1, 0));

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold mb-6 text-center text-blue-700">DiagnoAssist</h1>
        <StepNavigation steps={steps} current={current} />
      {current === 0 && (
        <div className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Chief Complaint</label>
            <input
              className="border rounded w-full p-2"
              placeholder="Describe the issue"
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={patientInfo.chiefComplaint}
              onChange={(e) =>
                setPatientInfo({ ...patientInfo, chiefComplaint: e.target.value })
              }
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Details</label>
            <textarea
              className="border rounded w-full p-2"
              rows={4}
              placeholder="Additional details"
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={patientInfo.details}
              onChange={(e) =>
                setPatientInfo({ ...patientInfo, details: e.target.value })
              }
            />
          </div>
        </div>
      )}

      {current === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Medical History</label>
            <textarea
              className="border rounded w-full p-2"
              rows={4}
              placeholder="Past illnesses, surgeries, etc."
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={history.history}
              onChange={(e) =>
                setHistory({ ...history, history: e.target.value })
              }
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Doctor Observations</label>
            <textarea
              className="border rounded w-full p-2"
              rows={3}
              placeholder="Your notes"
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={history.observations}
              onChange={(e) =>
                setHistory({ ...history, observations: e.target.value })
              }
            />
          </div>
        </div>
      )}

      {current === 2 && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block mb-1 font-medium">Blood Pressure</label>
              <input
                className="border rounded w-full p-2"
                placeholder="120/80"
                autoCorrect="on"
                autoCapitalize="off"
                spellCheck
                value={exam.bloodPressure}
                onChange={(e) =>
                  setExam({ ...exam, bloodPressure: e.target.value })
                }
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Heart Rate</label>
              <input
                className="border rounded w-full p-2"
                placeholder="beats/min"
                autoCorrect="on"
                autoCapitalize="off"
                spellCheck
                value={exam.heartRate}
                onChange={(e) =>
                  setExam({ ...exam, heartRate: e.target.value })
                }
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Height</label>
              <input
                className="border rounded w-full p-2"
                placeholder="cm"
                autoCorrect="on"
                autoCapitalize="off"
                spellCheck
                value={exam.height}
                onChange={(e) => setExam({ ...exam, height: e.target.value })}
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Weight</label>
              <input
                className="border rounded w-full p-2"
                placeholder="kg"
                autoCorrect="on"
                autoCapitalize="off"
                spellCheck
                value={exam.weight}
                onChange={(e) => setExam({ ...exam, weight: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="block mb-1 font-medium">Other Findings</label>
            <textarea
              className="border rounded w-full p-2"
              rows={3}
              placeholder="Any other findings"
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={exam.other}
              onChange={(e) => setExam({ ...exam, other: e.target.value })}
            />
          </div>
        </div>
      )}

      {current === 3 && (
        <div className="space-y-4">
          <h2 className="font-medium">Differential Diagnosis Suggestions</h2>
          <ul className="space-y-2 list-disc list-inside">
            {differentials.map((d) => (
              <li key={d.condition}>
                <span className="font-semibold">{d.condition}:</span> {d.explanation}
              </li>
            ))}
          </ul>
          <div>
            <label className="block mb-1 font-medium">Doctor Feedback</label>
            <textarea
              className="border rounded w-full p-2"
              rows={3}
              placeholder="Let us know if anything looks off"
              autoCorrect="on"
              autoCapitalize="sentences"
              spellCheck
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </div>
        </div>
      )}

      {current === 4 && (
        <div className="space-y-4">
          <h2 className="font-medium">Recommended Tests</h2>
          {tests.map((t, idx) => (
            <div key={t.name} className="mb-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={t.selected}
                  onChange={(e) => {
                    const newTests = [...tests];
                    newTests[idx].selected = e.target.checked;
                    setTests(newTests);
                  }}
                />
                <span>{t.name}</span>
              </label>
              {t.selected && (
                <input
                  className="border rounded w-full p-2 mt-1"
                  placeholder="Result"
                  autoCorrect="on"
                  autoCapitalize="off"
                  spellCheck
                  value={t.result}
                  onChange={(e) => {
                    const newTests = [...tests];
                    newTests[idx].result = e.target.value;
                    setTests(newTests);
                  }}
                />
              )}
            </div>
          ))}
        </div>
      )}

      {current === 5 && (
        <div className="space-y-4">
          <h2 className="font-medium">Finalize Diagnosis</h2>
          <textarea
            className="border rounded w-full p-2"
            rows={4}
            placeholder="Enter your working diagnosis"
            autoCorrect="on"
            autoCapitalize="sentences"
            spellCheck
            value={finalDx}
            onChange={(e) => setFinalDx(e.target.value)}
          />
          <div className="border rounded p-2 bg-gray-50">
            <h3 className="font-semibold mb-1">Summary</h3>
            <p><strong>Chief Complaint:</strong> {patientInfo.chiefComplaint}</p>
            <p><strong>History:</strong> {history.history}</p>
            <p><strong>Observations:</strong> {history.observations}</p>
            <p><strong>Exam BP:</strong> {exam.bloodPressure}, <strong>HR:</strong> {exam.heartRate}</p>
          </div>
        </div>
      )}

      <div className="flex justify-between mt-6">
        <button
          className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          onClick={prev}
          disabled={current === 0}
        >
          Back
        </button>
        {current < steps.length - 1 ? (
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded"
            onClick={next}
          >
            Next
          </button>
        ) : (
          <button
            className="px-4 py-2 bg-green-600 text-white rounded"
            onClick={() => alert('Diagnosis submitted!')}
          >
            Confirm
          </button>
        )}
      </div>
    </div>
    </div>
  );
}
