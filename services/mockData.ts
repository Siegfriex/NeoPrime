import { Student, Evaluation } from '../types';

// --- Helpers ---
const getDate = (daysAgo: number) => {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().split('T')[0];
};

// --- Students Data ---
export const STUDENTS: Student[] = [
  // --- Hongik Univ. Cohort ---
  {
    id: 's1',
    name: 'Ji-min Kim',
    grade: '3rd Year',
    school: 'Sehwa High',
    targetUniversity: 'Hongik Univ.',
    major: 'Visual Design',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jimin',
    artworks: [
      'https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=1000&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1544531586-fde5298cdd40?q=80&w=1000&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 135, percentile: 96, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 128, percentile: 89, grade: 2 },
      social1: { subjectName: "Life & Ethics", standardScore: 65, percentile: 94, grade: 1 },
      social2: { subjectName: "Social Culture", standardScore: 63, percentile: 92, grade: 1 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 132, percentile: 94 },
      english: { grade: 1.2 },
      math: { standardScore: 125, percentile: 85 },
      social1: { standardScore: 64, percentile: 93 },
      social2: { standardScore: 62, percentile: 90 }
    },
    admissionHistory: [
        { university: 'Hongik Univ.', major: 'Visual Design', result: 'Pending', type: 'Su-si (Early)', year: 2026 }
    ],
    similarCases: [
      {
        id: 'sc1',
        anonymizedName: 'Student K.',
        year: 2025,
        matchRate: 98,
        university: 'Hongik Univ.',
        major: 'Visual Design',
        result: 'Accepted',
        comparison: {
          academic: 'Similar',
          practical: 'Lower',
          note: 'Accepted with slightly lower practical scores due to excellent interview.'
        }
      }
    ]
  },
  {
    id: 's6',
    name: 'Ha-eun Jung',
    grade: '3rd Year',
    school: 'Kyunggi High',
    targetUniversity: 'Hongik Univ.',
    major: 'Industrial Design',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Haeun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 130, percentile: 92, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 124, percentile: 85, grade: 2 },
      social1: { standardScore: 63, percentile: 90, grade: 2 },
      social2: { standardScore: 60, percentile: 88, grade: 2 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 132, percentile: 94 },
        english: { grade: 1.2 },
        math: { standardScore: 125, percentile: 85 },
        social1: { standardScore: 64, percentile: 93 },
        social2: { standardScore: 62, percentile: 90 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's7',
    name: 'Woo-jin Kim',
    grade: 'Repeater',
    school: 'N/A',
    targetUniversity: 'Hongik Univ.',
    major: 'Visual Design',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Woojin',
    artworks: [],
    academicScores: {
        korean: { standardScore: 128, percentile: 88, grade: 2 },
        english: { grade: 2 },
        math: { standardScore: 120, percentile: 80, grade: 3 },
        social1: { standardScore: 60, percentile: 85, grade: 2 },
        social2: { standardScore: 58, percentile: 82, grade: 3 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 132, percentile: 94 },
        english: { grade: 1.2 },
        math: { standardScore: 125, percentile: 85 },
        social1: { standardScore: 64, percentile: 93 },
        social2: { standardScore: 62, percentile: 90 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's8',
    name: 'Seo-yeon Choi',
    grade: '3rd Year',
    school: 'Eun-gwang Girls High',
    targetUniversity: 'Hongik Univ.',
    major: 'Metal Craft',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seoyeon',
    artworks: [],
    academicScores: {
        korean: { standardScore: 125, percentile: 85, grade: 3 },
        english: { grade: 2 },
        math: { standardScore: 118, percentile: 75, grade: 3 },
        social1: { standardScore: 58, percentile: 80, grade: 3 },
        social2: { standardScore: 55, percentile: 75, grade: 3 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 128, percentile: 90 },
        english: { grade: 1.5 },
        math: { standardScore: 120, percentile: 80 },
        social1: { standardScore: 60, percentile: 85 },
        social2: { standardScore: 58, percentile: 82 }
    },
    admissionHistory: [],
    similarCases: []
  },

  // --- SNU Cohort ---
  {
    id: 's2',
    name: 'Min-su Lee',
    grade: '3rd Year',
    school: 'Whimoon High',
    targetUniversity: 'SNU',
    major: 'Crafts',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Minsu',
    artworks: [
      'https://images.unsplash.com/photo-1579783902614-a3fb39279c0f?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 140, percentile: 99, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 138, percentile: 96, grade: 1 },
      social1: { subjectName: "Ethics", standardScore: 68, percentile: 98, grade: 1 },
      social2: { subjectName: "Geography", standardScore: 66, percentile: 96, grade: 1 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 138, percentile: 98 },
      english: { grade: 1.0 },
      math: { standardScore: 135, percentile: 95 },
      social1: { standardScore: 66, percentile: 96 },
      social2: { standardScore: 65, percentile: 95 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's11',
    name: 'Hyun-woo Lee',
    grade: 'Repeater',
    school: 'N/A',
    targetUniversity: 'SNU',
    major: 'Design',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Hyunwoo',
    artworks: [],
    academicScores: {
        korean: { standardScore: 142, percentile: 99, grade: 1 },
        english: { grade: 1 },
        math: { standardScore: 135, percentile: 95, grade: 1 },
        social1: { standardScore: 67, percentile: 97, grade: 1 },
        social2: { standardScore: 68, percentile: 98, grade: 1 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 138, percentile: 98 },
        english: { grade: 1.0 },
        math: { standardScore: 135, percentile: 95 },
        social1: { standardScore: 66, percentile: 96 },
        social2: { standardScore: 65, percentile: 95 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's12',
    name: 'Ga-young Kim',
    grade: '3rd Year',
    school: 'Sunhwa Arts',
    targetUniversity: 'SNU',
    major: 'Crafts',
    currentLevel: 'A+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Gayoung',
    artworks: [],
    academicScores: {
        korean: { standardScore: 136, percentile: 95, grade: 1 },
        english: { grade: 1 },
        math: { standardScore: 130, percentile: 90, grade: 2 },
        social1: { standardScore: 65, percentile: 94, grade: 1 },
        social2: { standardScore: 64, percentile: 92, grade: 1 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 138, percentile: 98 },
        english: { grade: 1.0 },
        math: { standardScore: 135, percentile: 95 },
        social1: { standardScore: 66, percentile: 96 },
        social2: { standardScore: 65, percentile: 95 }
    },
    admissionHistory: [],
    similarCases: []
  },

  // --- Ewha Cohort ---
  {
    id: 's3',
    name: 'Su-jin Park',
    grade: '2nd Year',
    school: 'Hyundai High',
    targetUniversity: 'Ewha Womans Univ.',
    major: 'Industrial Design',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sujin',
    artworks: [
      'https://images.unsplash.com/photo-1547891654-e66ed7ebb968?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 125, percentile: 88, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 115, percentile: 78, grade: 3 },
      social1: { subjectName: "History", standardScore: 58, percentile: 80, grade: 2 },
      social2: { subjectName: "Politics", standardScore: 55, percentile: 75, grade: 3 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 128, percentile: 90 },
      english: { grade: 1.5 },
      math: { standardScore: 120, percentile: 82 },
      social1: { standardScore: 60, percentile: 85 },
      social2: { standardScore: 58, percentile: 82 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's14',
    name: 'Ji-hye Han',
    grade: '3rd Year',
    school: 'Sookmyung Girls',
    targetUniversity: 'Ewha Womans Univ.',
    major: 'Fashion Design',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jihye',
    artworks: [],
    academicScores: {
        korean: { standardScore: 130, percentile: 92, grade: 2 },
        english: { grade: 1 },
        math: { standardScore: 118, percentile: 80, grade: 3 },
        social1: { standardScore: 62, percentile: 88, grade: 2 },
        social2: { standardScore: 60, percentile: 85, grade: 2 }
    },
    targetUnivAvgScores: {
        korean: { standardScore: 128, percentile: 90 },
        english: { grade: 1.5 },
        math: { standardScore: 120, percentile: 82 },
        social1: { standardScore: 60, percentile: 85 },
        social2: { standardScore: 58, percentile: 82 }
    },
    admissionHistory: [],
    similarCases: []
  },

  // --- Others ---
  {
    id: 's4',
    name: 'Do-hyun Choi',
    grade: 'Repeater',
    school: 'N/A',
    targetUniversity: 'Kookmin Univ.',
    major: 'Visual Design',
    currentLevel: 'A+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Dohyun',
    artworks: [
      'https://images.unsplash.com/photo-1569172131007-195881aa38db?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 128, percentile: 90, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 110, percentile: 70, grade: 3 },
      social1: { subjectName: "Culture", standardScore: 62, percentile: 88, grade: 2 },
      social2: { subjectName: "Ethics", standardScore: 60, percentile: 85, grade: 2 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 125, percentile: 85 },
      english: { grade: 2.1 },
      math: { standardScore: 112, percentile: 72 },
      social1: { standardScore: 60, percentile: 85 },
      social2: { standardScore: 58, percentile: 80 }
    },
    admissionHistory: [],
    similarCases: []
  },
  {
    id: 's5',
    name: 'Ye-eun Jang',
    grade: '1st Year',
    school: 'Apgujeong High',
    targetUniversity: 'Konkuk Univ.',
    major: 'Communication Design',
    currentLevel: 'C',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yeeun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 110, percentile: 70, grade: 4 },
      english: { grade: 3 },
      math: { standardScore: 100, percentile: 50, grade: 5 },
      social1: { subjectName: "History", standardScore: 50, percentile: 60, grade: 4 },
      social2: { subjectName: "Geography", standardScore: 48, percentile: 55, grade: 4 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 120, percentile: 82 },
      english: { grade: 2.5 },
      math: { standardScore: 110, percentile: 70 },
      social1: { standardScore: 55, percentile: 75 },
      social2: { standardScore: 54, percentile: 72 }
    },
    admissionHistory: [],
    similarCases: []
  }
];

// --- Evaluations Data ---
export const EVALUATIONS: Evaluation[] = [
  // --- Ji-min Kim (s1) [Star Student, steady rise] ---
  { id: 'e1_1', studentId: 's1', date: getDate(60), scores: { composition: 7, tone: 7, idea: 6, completeness: 7 }, totalScore: 70, notes: 'Base level.', instructorId: 'i1' },
  { id: 'e1_2', studentId: 's1', date: getDate(53), scores: { composition: 7.5, tone: 7, idea: 6.5, completeness: 7 }, totalScore: 72, notes: 'Slight improvement in composition.', instructorId: 'i1' },
  { id: 'e1_3', studentId: 's1', date: getDate(46), scores: { composition: 8, tone: 7.5, idea: 7, completeness: 7.5 }, totalScore: 75, notes: 'Good progress.', instructorId: 'i1' },
  { id: 'e1_4', studentId: 's1', date: getDate(39), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 80, notes: 'Contrast is getting better.', instructorId: 'i1' },
  { id: 'e1_5', studentId: 's1', date: getDate(32), scores: { composition: 8.5, tone: 8, idea: 8, completeness: 8.5 }, totalScore: 82.5, notes: 'Very stable.', instructorId: 'i1' },
  { id: 'e1_6', studentId: 's1', date: getDate(25), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 88, notes: 'Excellent detail.', instructorId: 'i1' },
  { id: 'e1_7', studentId: 's1', date: getDate(18), scores: { composition: 9, tone: 9, idea: 8.5, completeness: 9 }, totalScore: 90, notes: 'A-tier quality.', instructorId: 'i1' },
  { id: 'e1_8', studentId: 's1', date: getDate(11), scores: { composition: 9.5, tone: 9, idea: 9, completeness: 9.5 }, totalScore: 92.5, notes: 'Exam ready.', instructorId: 'i1' },
  { id: 'e1_9', studentId: 's1', date: getDate(4), scores: { composition: 9.5, tone: 9.5, idea: 9, completeness: 9.5 }, totalScore: 94, notes: 'Perfect balance.', instructorId: 'i1' },

  // --- Ha-eun Jung (s6) [Consistent A-] ---
  { id: 'e6_1', studentId: 's6', date: getDate(60), scores: { composition: 8, tone: 8, idea: 7, completeness: 7 }, totalScore: 75, notes: 'Good.', instructorId: 'i1' },
  { id: 'e6_2', studentId: 's6', date: getDate(45), scores: { composition: 8.5, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 80, notes: 'Nice tones.', instructorId: 'i1' },
  { id: 'e6_3', studentId: 's6', date: getDate(30), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8 }, totalScore: 82.5, notes: 'Solid work.', instructorId: 'i1' },
  { id: 'e6_4', studentId: 's6', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 85, notes: 'Consistent.', instructorId: 'i1' },
  { id: 'e6_5', studentId: 's6', date: getDate(5), scores: { composition: 9, tone: 9, idea: 8, completeness: 8.5 }, totalScore: 86, notes: 'Very good.', instructorId: 'i1' },

  // --- Woo-jin Kim (s7) [Fluctuating B+] ---
  { id: 'e7_1', studentId: 's7', date: getDate(55), scores: { composition: 6, tone: 7, idea: 8, completeness: 6 }, totalScore: 65, notes: 'Rushed.', instructorId: 'i1' },
  { id: 'e7_2', studentId: 's7', date: getDate(40), scores: { composition: 7, tone: 7.5, idea: 8, completeness: 7 }, totalScore: 72, notes: 'Better.', instructorId: 'i1' },
  { id: 'e7_3', studentId: 's7', date: getDate(25), scores: { composition: 6.5, tone: 7, idea: 8.5, completeness: 6.5 }, totalScore: 68, notes: 'Slump?', instructorId: 'i1' },
  { id: 'e7_4', studentId: 's7', date: getDate(10), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'Recovery.', instructorId: 'i1' },

  // --- Min-su Lee (s2) [Volatile SNU Student] ---
  { id: 'e2_1', studentId: 's2', date: getDate(60), scores: { composition: 6, tone: 8, idea: 5, completeness: 7 }, totalScore: 65, notes: 'Concept weak.', instructorId: 'i1' },
  { id: 'e2_2', studentId: 's2', date: getDate(50), scores: { composition: 7, tone: 8.5, idea: 6, completeness: 7.5 }, totalScore: 72.5, notes: 'Better tech.', instructorId: 'i1' },
  { id: 'e2_3', studentId: 's2', date: getDate(40), scores: { composition: 6.5, tone: 8, idea: 5.5, completeness: 7 }, totalScore: 68, notes: 'Unstable.', instructorId: 'i1' },
  { id: 'e2_4', studentId: 's2', date: getDate(30), scores: { composition: 8, tone: 9, idea: 7, completeness: 8 }, totalScore: 80, notes: 'Big jump.', instructorId: 'i1' },
  { id: 'e2_5', studentId: 's2', date: getDate(20), scores: { composition: 7.5, tone: 8.5, idea: 6.5, completeness: 8 }, totalScore: 75, notes: 'Okay.', instructorId: 'i1' },
  { id: 'e2_6', studentId: 's2', date: getDate(10), scores: { composition: 8.5, tone: 9.5, idea: 7.5, completeness: 8.5 }, totalScore: 85, notes: 'Peak performance.', instructorId: 'i1' },

  // --- Su-jin Park (s3) [Ewha B-Tier] ---
  { id: 'e3_1', studentId: 's3', date: getDate(60), scores: { composition: 7, tone: 7, idea: 7, completeness: 6 }, totalScore: 67.5, notes: 'Average.', instructorId: 'i2' },
  { id: 'e3_2', studentId: 's3', date: getDate(45), scores: { composition: 7.5, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 70, notes: 'Slow improv.', instructorId: 'i2' },
  { id: 'e3_3', studentId: 's3', date: getDate(30), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 72.5, notes: 'Steady.', instructorId: 'i2' },
  { id: 'e3_4', studentId: 's3', date: getDate(15), scores: { composition: 8, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'Good finish.', instructorId: 'i2' },

  // --- Do-hyun Choi (s4) [Kookmin A+] ---
  { id: 'e4_1', studentId: 's4', date: getDate(50), scores: { composition: 9, tone: 9, idea: 9, completeness: 8 }, totalScore: 87.5, notes: 'Strong.', instructorId: 'i2' },
  { id: 'e4_2', studentId: 's4', date: getDate(35), scores: { composition: 9.5, tone: 9, idea: 9, completeness: 9 }, totalScore: 91, notes: 'Very strong.', instructorId: 'i2' },
  { id: 'e4_3', studentId: 's4', date: getDate(20), scores: { composition: 9, tone: 9.5, idea: 9.5, completeness: 9 }, totalScore: 92.5, notes: 'Excellent.', instructorId: 'i2' },
  { id: 'e4_4', studentId: 's4', date: getDate(5), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: 'Masterpiece.', instructorId: 'i2' },

  // --- Seo-yeon Choi (s8) [Hongik B] ---
  { id: 'e8_1', studentId: 's8', date: getDate(45), scores: { composition: 6, tone: 6, idea: 6, completeness: 6 }, totalScore: 60, notes: 'Weak.', instructorId: 'i2' },
  { id: 'e8_2', studentId: 's8', date: getDate(30), scores: { composition: 7, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 66, notes: 'Trying.', instructorId: 'i2' },
  { id: 'e8_3', studentId: 's8', date: getDate(15), scores: { composition: 7.5, tone: 7, idea: 7, completeness: 7 }, totalScore: 71, notes: 'Better.', instructorId: 'i2' },

  // --- Ga-young Kim (s12) [SNU A+] ---
  { id: 'e12_1', studentId: 's12', date: getDate(55), scores: { composition: 9, tone: 8.5, idea: 9, completeness: 8.5 }, totalScore: 87.5, notes: 'Great.', instructorId: 'i1' },
  { id: 'e12_2', studentId: 's12', date: getDate(40), scores: { composition: 9, tone: 9, idea: 9, completeness: 9 }, totalScore: 90, notes: 'Superb.', instructorId: 'i1' },
  { id: 'e12_3', studentId: 's12', date: getDate(25), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92.5, notes: 'Amazing.', instructorId: 'i1' },
  { id: 'e12_4', studentId: 's12', date: getDate(10), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: 'Top tier.', instructorId: 'i1' },

  // --- Hyun-woo Lee (s11) [SNU A] ---
  { id: 'e11_1', studentId: 's11', date: getDate(45), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'Solid.', instructorId: 'i1' },
  { id: 'e11_2', studentId: 's11', date: getDate(30), scores: { composition: 8.5, tone: 8, idea: 8.5, completeness: 8 }, totalScore: 82.5, notes: 'Good.', instructorId: 'i1' },
  { id: 'e11_3', studentId: 's11', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: 'Improving.', instructorId: 'i1' },

  // --- Ji-hye Han (s14) [Ewha A] ---
  { id: 'e14_1', studentId: 's14', date: getDate(40), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'Good.', instructorId: 'i2' },
  { id: 'e14_2', studentId: 's14', date: getDate(25), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8 }, totalScore: 82.5, notes: 'Nice.', instructorId: 'i2' },
  { id: 'e14_3', studentId: 's14', date: getDate(10), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: 'Strong.', instructorId: 'i2' }

].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

export const getStudentById = (id: string) => STUDENTS.find(s => s.id === id);
export const getEvaluationsByStudentId = (id: string) => EVALUATIONS.filter(e => e.studentId === id).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());