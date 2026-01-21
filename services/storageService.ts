import { Student, Evaluation } from '../types';
import { STUDENTS, EVALUATIONS } from './mockData';

const STORAGE_KEYS = {
  STUDENTS: 'neoprime_students',
  EVALUATIONS: 'neoprime_evaluations',
};

// Initialize Data if empty
const initData = () => {
  if (!localStorage.getItem(STORAGE_KEYS.STUDENTS)) {
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(STUDENTS));
  }
  if (!localStorage.getItem(STORAGE_KEYS.EVALUATIONS)) {
    localStorage.setItem(STORAGE_KEYS.EVALUATIONS, JSON.stringify(EVALUATIONS));
  }
};

// --- Students CRUD ---
export const getStudents = (): Student[] => {
  initData();
  const data = localStorage.getItem(STORAGE_KEYS.STUDENTS);
  return data ? JSON.parse(data) : [];
};

export const getStudentById = (id: string): Student | undefined => {
  const students = getStudents();
  return students.find(s => s.id === id);
};

export const addStudent = (student: Student): void => {
  const students = getStudents();
  const newStudent = { ...student, id: `s${Date.now()}` }; // Simple ID generation
  students.push(newStudent);
  localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(students));
};

export const updateStudent = (updatedStudent: Student): void => {
  const students = getStudents();
  const index = students.findIndex(s => s.id === updatedStudent.id);
  if (index !== -1) {
    students[index] = updatedStudent;
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(students));
  }
};

// --- Evaluations CRUD ---
export const getEvaluations = (): Evaluation[] => {
  initData();
  const data = localStorage.getItem(STORAGE_KEYS.EVALUATIONS);
  const evals = data ? JSON.parse(data) : [];
  // Sort by date descending
  return evals.sort((a: Evaluation, b: Evaluation) => new Date(b.date).getTime() - new Date(a.date).getTime());
};

export const getEvaluationsByStudentId = (studentId: string): Evaluation[] => {
  const evals = getEvaluations();
  return evals.filter(e => e.studentId === studentId);
};

export const addEvaluation = (evaluation: Omit<Evaluation, 'id'>): void => {
  const evals = getEvaluations();
  const newEval = { ...evaluation, id: `e${Date.now()}` };
  evals.push(newEval);
  localStorage.setItem(STORAGE_KEYS.EVALUATIONS, JSON.stringify(evals));
};
