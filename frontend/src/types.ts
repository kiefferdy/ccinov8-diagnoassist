export interface PatientInfo {
  chiefComplaint: string;
  details: string;
}

export interface MedicalHistory {
  history: string;
  observations: string;
}

export interface PhysicalExam {
  bloodPressure: string;
  heartRate: string;
  height: string;
  weight: string;
  other: string;
}

export interface Differential {
  condition: string;
  explanation: string;
}

export interface TestItem {
  name: string;
  selected: boolean;
  result: string;
}
