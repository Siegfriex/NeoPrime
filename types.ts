export interface AcademicScore {
  subjectName?: string; // e.g., "Social Culture", "Ethics"
  standardScore?: number;
  rawScore?: number;
  percentile?: number;
  grade?: number;
}

export interface AdmissionResult {
  university: string;
  major: string;
  result: 'Accepted' | 'Rejected' | 'Pending' | 'Waitlisted' | 'Canceled';
  type: 'Su-si (Early)' | 'Jeong-si (Regular)' | 'Mock';
  year: number;
}

export interface SimilarCase {
  id: string;
  anonymizedName: string; // e.g., "Student K."
  year: number;
  matchRate: number; // 0-100%
  university: string;
  major: string;
  result: 'Accepted' | 'Rejected' | 'Waitlisted';
  comparison: {
    academic: 'Higher' | 'Lower' | 'Similar';
    practical: 'Higher' | 'Lower' | 'Similar';
    note: string; // e.g., "Practical score was +2 higher"
  };
}

export interface Student {
  id: string;
  name: string;
  grade: '1학년' | '2학년' | '3학년' | '재수';
  school: string;
  targetUniversity: string;
  major: string;
  currentLevel: 'A+' | 'A' | 'B+' | 'B' | 'C';
  instructorId: string;
  avatarUrl: string;
  
  // New fields for Dashboard
  artworks: string[];
  academicScores: {
    korean: AcademicScore;
    english: AcademicScore;
    math: AcademicScore;
    social1: AcademicScore;
    social2: AcademicScore;
  };
  targetUnivAvgScores: {
    korean: AcademicScore;
    english: AcademicScore;
    math: AcademicScore;
    social1: AcademicScore;
    social2: AcademicScore;
  };
  admissionHistory: AdmissionResult[];
  similarCases: SimilarCase[];
}

export interface EvaluationScore {
  composition: number; // 0-10
  tone: number; // 0-10
  idea: number; // 0-10
  completeness: number; // 0-10
}

export interface Evaluation {
  id: string;
  studentId: string;
  date: string;
  scores: EvaluationScore;
  totalScore: number;
  notes: string;
  aiFeedback?: {
    strengths: string;
    weaknesses: string;
    actionPlan: string;
  };
  instructorId: string;
}

export interface AdmissionStats {
  university: string;
  probability: number; // 0-100
  line: 'TOP' | 'HIGH' | 'MID' | 'LOW';
}