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
    name: '김지민',
    grade: '3학년',
    school: '세화고',
    targetUniversity: '홍익대',
    major: '시각디자인',
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
      social1: { subjectName: "생활과 윤리", standardScore: 65, percentile: 94, grade: 1 },
      social2: { subjectName: "사회문화", standardScore: 63, percentile: 92, grade: 1 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 132, percentile: 94 },
      english: { grade: 1.2 },
      math: { standardScore: 125, percentile: 85 },
      social1: { standardScore: 64, percentile: 93 },
      social2: { standardScore: 62, percentile: 90 }
    },
    admissionHistory: [
        { university: '홍익대', major: '시각디자인', result: 'Pending', type: 'Su-si (Early)', year: 2026 }
    ],
    similarCases: [
      {
        id: 'sc1',
        anonymizedName: '학생 K.',
        year: 2025,
        matchRate: 98,
        university: '홍익대',
        major: '시각디자인',
        result: 'Accepted',
        comparison: {
          academic: 'Similar',
          practical: 'Lower',
          note: '우수한 면접 점수로 실기 점수를 만회하여 합격.'
        }
      }
    ]
  },
  {
    id: 's6',
    name: '정하은',
    grade: '3학년',
    school: '경기여고',
    targetUniversity: '홍익대',
    major: '산업디자인',
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
    name: '김우진',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '홍익대',
    major: '시각디자인',
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
    name: '최서연',
    grade: '3학년',
    school: '은광여고',
    targetUniversity: '홍익대',
    major: '금속조형',
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
    name: '이민수',
    grade: '3학년',
    school: '휘문고',
    targetUniversity: '서울대',
    major: '공예',
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
      social1: { subjectName: "윤리와 사상", standardScore: 68, percentile: 98, grade: 1 },
      social2: { subjectName: "한국지리", standardScore: 66, percentile: 96, grade: 1 }
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
    name: '이현우',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '서울대',
    major: '디자인',
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
    name: '김가영',
    grade: '3학년',
    school: '선화예고',
    targetUniversity: '서울대',
    major: '공예',
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
    name: '박수진',
    grade: '2학년',
    school: '현대고',
    targetUniversity: '이화여대',
    major: '산업디자인',
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
      social1: { subjectName: "동아시아사", standardScore: 58, percentile: 80, grade: 2 },
      social2: { subjectName: "정치와 법", standardScore: 55, percentile: 75, grade: 3 }
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
    name: '한지혜',
    grade: '3학년',
    school: '숙명여고',
    targetUniversity: '이화여대',
    major: '패션디자인',
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
    name: '최도현',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '국민대',
    major: '시각디자인',
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
      social1: { subjectName: "사회문화", standardScore: 62, percentile: 88, grade: 2 },
      social2: { subjectName: "윤리와 사상", standardScore: 60, percentile: 85, grade: 2 }
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
    name: '장예은',
    grade: '1학년',
    school: '압구정고',
    targetUniversity: '건국대',
    major: '커뮤니케이션',
    currentLevel: 'C',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yeeun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 110, percentile: 70, grade: 4 },
      english: { grade: 3 },
      math: { standardScore: 100, percentile: 50, grade: 5 },
      social1: { subjectName: "한국사", standardScore: 50, percentile: 60, grade: 4 },
      social2: { subjectName: "지리", standardScore: 48, percentile: 55, grade: 4 }
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

// --- Evaluations Data (노트 한글화) ---
export const EVALUATIONS: Evaluation[] = [
  // --- Ji-min Kim (s1) [Star Student, steady rise] ---
  { id: 'e1_1', studentId: 's1', date: getDate(60), scores: { composition: 7, tone: 7, idea: 6, completeness: 7 }, totalScore: 70, notes: '기본기 점검.', instructorId: 'i1' },
  { id: 'e1_2', studentId: 's1', date: getDate(53), scores: { composition: 7.5, tone: 7, idea: 6.5, completeness: 7 }, totalScore: 72, notes: '구도에서 약간의 개선.', instructorId: 'i1' },
  { id: 'e1_3', studentId: 's1', date: getDate(46), scores: { composition: 8, tone: 7.5, idea: 7, completeness: 7.5 }, totalScore: 75, notes: '발전 속도 좋음.', instructorId: 'i1' },
  { id: 'e1_4', studentId: 's1', date: getDate(39), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 80, notes: '대비감이 좋아짐.', instructorId: 'i1' },
  { id: 'e1_5', studentId: 's1', date: getDate(32), scores: { composition: 8.5, tone: 8, idea: 8, completeness: 8.5 }, totalScore: 82.5, notes: '매우 안정적임.', instructorId: 'i1' },
  { id: 'e1_6', studentId: 's1', date: getDate(25), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 88, notes: '디테일 묘사 훌륭함.', instructorId: 'i1' },
  { id: 'e1_7', studentId: 's1', date: getDate(18), scores: { composition: 9, tone: 9, idea: 8.5, completeness: 9 }, totalScore: 90, notes: 'A권대 진입.', instructorId: 'i1' },
  { id: 'e1_8', studentId: 's1', date: getDate(11), scores: { composition: 9.5, tone: 9, idea: 9, completeness: 9.5 }, totalScore: 92.5, notes: '시험 준비 완료.', instructorId: 'i1' },
  { id: 'e1_9', studentId: 's1', date: getDate(4), scores: { composition: 9.5, tone: 9.5, idea: 9, completeness: 9.5 }, totalScore: 94, notes: '완벽한 밸런스.', instructorId: 'i1' },

  // --- Ha-eun Jung (s6) [Consistent A-] ---
  { id: 'e6_1', studentId: 's6', date: getDate(60), scores: { composition: 8, tone: 8, idea: 7, completeness: 7 }, totalScore: 75, notes: '무난함.', instructorId: 'i1' },
  { id: 'e6_2', studentId: 's6', date: getDate(45), scores: { composition: 8.5, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 80, notes: '톤이 좋음.', instructorId: 'i1' },
  { id: 'e6_3', studentId: 's6', date: getDate(30), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8 }, totalScore: 82.5, notes: '견고한 기본기.', instructorId: 'i1' },
  { id: 'e6_4', studentId: 's6', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 85, notes: '일관성 있음.', instructorId: 'i1' },
  { id: 'e6_5', studentId: 's6', date: getDate(5), scores: { composition: 9, tone: 9, idea: 8, completeness: 8.5 }, totalScore: 86, notes: '아주 좋음.', instructorId: 'i1' },

  // --- Woo-jin Kim (s7) [Fluctuating B+] ---
  { id: 'e7_1', studentId: 's7', date: getDate(55), scores: { composition: 6, tone: 7, idea: 8, completeness: 6 }, totalScore: 65, notes: '급하게 마무리됨.', instructorId: 'i1' },
  { id: 'e7_2', studentId: 's7', date: getDate(40), scores: { composition: 7, tone: 7.5, idea: 8, completeness: 7 }, totalScore: 72, notes: '나아짐.', instructorId: 'i1' },
  { id: 'e7_3', studentId: 's7', date: getDate(25), scores: { composition: 6.5, tone: 7, idea: 8.5, completeness: 6.5 }, totalScore: 68, notes: '슬럼프?', instructorId: 'i1' },
  { id: 'e7_4', studentId: 's7', date: getDate(10), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '회복세.', instructorId: 'i1' },

  // --- Min-su Lee (s2) [Volatile SNU Student] ---
  { id: 'e2_1', studentId: 's2', date: getDate(60), scores: { composition: 6, tone: 8, idea: 5, completeness: 7 }, totalScore: 65, notes: '컨셉이 약함.', instructorId: 'i1' },
  { id: 'e2_2', studentId: 's2', date: getDate(50), scores: { composition: 7, tone: 8.5, idea: 6, completeness: 7.5 }, totalScore: 72.5, notes: '테크닉 향상.', instructorId: 'i1' },
  { id: 'e2_3', studentId: 's2', date: getDate(40), scores: { composition: 6.5, tone: 8, idea: 5.5, completeness: 7 }, totalScore: 68, notes: '불안정함.', instructorId: 'i1' },
  { id: 'e2_4', studentId: 's2', date: getDate(30), scores: { composition: 8, tone: 9, idea: 7, completeness: 8 }, totalScore: 80, notes: '큰 도약.', instructorId: 'i1' },
  { id: 'e2_5', studentId: 's2', date: getDate(20), scores: { composition: 7.5, tone: 8.5, idea: 6.5, completeness: 8 }, totalScore: 75, notes: '보통.', instructorId: 'i1' },
  { id: 'e2_6', studentId: 's2', date: getDate(10), scores: { composition: 8.5, tone: 9.5, idea: 7.5, completeness: 8.5 }, totalScore: 85, notes: '최고 기록.', instructorId: 'i1' },

  // --- Su-jin Park (s3) [Ewha B-Tier] ---
  { id: 'e3_1', studentId: 's3', date: getDate(60), scores: { composition: 7, tone: 7, idea: 7, completeness: 6 }, totalScore: 67.5, notes: '평균.', instructorId: 'i2' },
  { id: 'e3_2', studentId: 's3', date: getDate(45), scores: { composition: 7.5, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 70, notes: '느린 향상.', instructorId: 'i2' },
  { id: 'e3_3', studentId: 's3', date: getDate(30), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 72.5, notes: '꾸준함.', instructorId: 'i2' },
  { id: 'e3_4', studentId: 's3', date: getDate(15), scores: { composition: 8, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: '마무리가 좋음.', instructorId: 'i2' },

  // --- Do-hyun Choi (s4) [Kookmin A+] ---
  { id: 'e4_1', studentId: 's4', date: getDate(50), scores: { composition: 9, tone: 9, idea: 9, completeness: 8 }, totalScore: 87.5, notes: '강렬함.', instructorId: 'i2' },
  { id: 'e4_2', studentId: 's4', date: getDate(35), scores: { composition: 9.5, tone: 9, idea: 9, completeness: 9 }, totalScore: 91, notes: '매우 강렬함.', instructorId: 'i2' },
  { id: 'e4_3', studentId: 's4', date: getDate(20), scores: { composition: 9, tone: 9.5, idea: 9.5, completeness: 9 }, totalScore: 92.5, notes: '훌륭함.', instructorId: 'i2' },
  { id: 'e4_4', studentId: 's4', date: getDate(5), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '마스터피스.', instructorId: 'i2' },

  // --- Seo-yeon Choi (s8) [Hongik B] ---
  { id: 'e8_1', studentId: 's8', date: getDate(45), scores: { composition: 6, tone: 6, idea: 6, completeness: 6 }, totalScore: 60, notes: '약함.', instructorId: 'i2' },
  { id: 'e8_2', studentId: 's8', date: getDate(30), scores: { composition: 7, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 66, notes: '노력 중.', instructorId: 'i2' },
  { id: 'e8_3', studentId: 's8', date: getDate(15), scores: { composition: 7.5, tone: 7, idea: 7, completeness: 7 }, totalScore: 71, notes: '나아짐.', instructorId: 'i2' },

  // --- Ga-young Kim (s12) [SNU A+] ---
  { id: 'e12_1', studentId: 's12', date: getDate(55), scores: { composition: 9, tone: 8.5, idea: 9, completeness: 8.5 }, totalScore: 87.5, notes: '대단함.', instructorId: 'i1' },
  { id: 'e12_2', studentId: 's12', date: getDate(40), scores: { composition: 9, tone: 9, idea: 9, completeness: 9 }, totalScore: 90, notes: '최상급.', instructorId: 'i1' },
  { id: 'e12_3', studentId: 's12', date: getDate(25), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92.5, notes: '놀라움.', instructorId: 'i1' },
  { id: 'e12_4', studentId: 's12', date: getDate(10), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '탑 티어.', instructorId: 'i1' },

  // --- Hyun-woo Lee (s11) [SNU A] ---
  { id: 'e11_1', studentId: 's11', date: getDate(45), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '견고함.', instructorId: 'i1' },
  { id: 'e11_2', studentId: 's11', date: getDate(30), scores: { composition: 8.5, tone: 8, idea: 8.5, completeness: 8 }, totalScore: 82.5, notes: '좋음.', instructorId: 'i1' },
  { id: 'e11_3', studentId: 's11', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: '향상됨.', instructorId: 'i1' },

  // --- Ji-hye Han (s14) [Ewha A] ---
  { id: 'e14_1', studentId: 's14', date: getDate(40), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '좋음.', instructorId: 'i2' },
  { id: 'e14_2', studentId: 's14', date: getDate(25), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8 }, totalScore: 82.5, notes: '나이스.', instructorId: 'i2' },
  { id: 'e14_3', studentId: 's14', date: getDate(10), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: '강점.', instructorId: 'i2' }

].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

export const getStudentById = (id: string) => STUDENTS.find(s => s.id === id);
export const getEvaluationsByStudentId = (id: string) => EVALUATIONS.filter(e => e.studentId === id).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());