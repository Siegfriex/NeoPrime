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
  {
    id: 's15',
    name: '강민준',
    grade: '2학년',
    school: '명덕고',
    targetUniversity: '홍익대',
    major: '시각디자인',
    currentLevel: 'A-',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Minjun',
    artworks: [
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 133, percentile: 95, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 126, percentile: 87, grade: 2 },
      social1: { subjectName: "생활과 윤리", standardScore: 64, percentile: 93, grade: 1 },
      social2: { subjectName: "사회문화", standardScore: 62, percentile: 91, grade: 1 }
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
    id: 's16',
    name: '윤서아',
    grade: '3학년',
    school: '덕성여고',
    targetUniversity: '홍익대',
    major: '산업디자인',
    currentLevel: 'B+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seoa',
    artworks: [],
    academicScores: {
      korean: { standardScore: 129, percentile: 91, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 123, percentile: 84, grade: 2 },
      social1: { standardScore: 62, percentile: 89, grade: 2 },
      social2: { standardScore: 59, percentile: 86, grade: 2 }
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
    id: 's17',
    name: '조현우',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '홍익대',
    major: '금속조형',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Hyunwoo2',
    artworks: [
      'https://images.unsplash.com/photo-1578301978018-3005759f48f7?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 131, percentile: 93, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 125, percentile: 86, grade: 2 },
      social1: { standardScore: 63, percentile: 91, grade: 1 },
      social2: { standardScore: 61, percentile: 89, grade: 1 }
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
    id: 's18',
    name: '임지우',
    grade: '3학년',
    school: '진선여고',
    targetUniversity: '홍익대',
    major: '시각디자인',
    currentLevel: 'A+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jiwu',
    artworks: [
      'https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1000&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 137, percentile: 97, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 130, percentile: 91, grade: 1 },
      social1: { subjectName: "생활과 윤리", standardScore: 66, percentile: 95, grade: 1 },
      social2: { subjectName: "사회문화", standardScore: 64, percentile: 93, grade: 1 }
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
        id: 'sc18_1',
        anonymizedName: '학생 L.',
        year: 2025,
        matchRate: 95,
        university: '홍익대',
        major: '시각디자인',
        result: 'Accepted',
        comparison: {
          academic: 'Higher',
          practical: 'Similar',
          note: '학업 성적이 우수하여 실기 점수 보완.'
        }
      }
    ]
  },
  {
    id: 's19',
    name: '배도윤',
    grade: '2학년',
    school: '한영고',
    targetUniversity: '홍익대',
    major: '산업디자인',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Doyun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 127, percentile: 89, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 121, percentile: 81, grade: 3 },
      social1: { standardScore: 61, percentile: 87, grade: 2 },
      social2: { standardScore: 58, percentile: 83, grade: 2 }
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
    id: 's20',
    name: '송하늘',
    grade: '3학년',
    school: '이화여고',
    targetUniversity: '홍익대',
    major: '금속조형',
    currentLevel: 'C',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Haneul',
    artworks: [],
    academicScores: {
      korean: { standardScore: 122, percentile: 83, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 115, percentile: 77, grade: 3 },
      social1: { standardScore: 57, percentile: 79, grade: 3 },
      social2: { standardScore: 54, percentile: 74, grade: 3 }
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
  {
    id: 's21',
    name: '오준서',
    grade: '3학년',
    school: '서울고',
    targetUniversity: '서울대',
    major: '디자인',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Junseo',
    artworks: [
      'https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 139, percentile: 98, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 137, percentile: 97, grade: 1 },
      social1: { subjectName: "윤리와 사상", standardScore: 67, percentile: 97, grade: 1 },
      social2: { subjectName: "한국지리", standardScore: 65, percentile: 95, grade: 1 }
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
    id: 's22',
    name: '신유진',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '서울대',
    major: '공예',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yujin',
    artworks: [],
    academicScores: {
      korean: { standardScore: 141, percentile: 99, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 134, percentile: 94, grade: 1 },
      social1: { standardScore: 66, percentile: 96, grade: 1 },
      social2: { standardScore: 65, percentile: 95, grade: 1 }
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
    id: 's23',
    name: '황민재',
    grade: '2학년',
    school: '중앙고',
    targetUniversity: '서울대',
    major: '디자인',
    currentLevel: 'A+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Minjae',
    artworks: [
      'https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1000&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 138, percentile: 98, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 136, percentile: 96, grade: 1 },
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
    similarCases: [
      {
        id: 'sc23_1',
        anonymizedName: '학생 M.',
        year: 2025,
        matchRate: 97,
        university: '서울대',
        major: '디자인',
        result: 'Accepted',
        comparison: {
          academic: 'Similar',
          practical: 'Higher',
          note: '실기 점수가 평균보다 높아 합격.'
        }
      }
    ]
  },
  {
    id: 's24',
    name: '노서연',
    grade: '3학년',
    school: '세화여고',
    targetUniversity: '서울대',
    major: '공예',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seoyeon2',
    artworks: [],
    academicScores: {
      korean: { standardScore: 137, percentile: 96, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 132, percentile: 92, grade: 1 },
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
  {
    id: 's25',
    name: '문지훈',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '서울대',
    major: '디자인',
    currentLevel: 'B',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jihun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 135, percentile: 94, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 129, percentile: 88, grade: 2 },
      social1: { standardScore: 64, percentile: 93, grade: 1 },
      social2: { standardScore: 63, percentile: 91, grade: 1 }
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
    id: 's26',
    name: '류다은',
    grade: '3학년',
    school: '경기여고',
    targetUniversity: '서울대',
    major: '공예',
    currentLevel: 'A+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Daeun',
    artworks: [
      'https://images.unsplash.com/photo-1579783902614-a3fb39279c0f?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 140, percentile: 99, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 138, percentile: 97, grade: 1 },
      social1: { subjectName: "윤리와 사상", standardScore: 69, percentile: 99, grade: 1 },
      social2: { subjectName: "한국지리", standardScore: 67, percentile: 97, grade: 1 }
    },
    targetUnivAvgScores: {
      korean: { standardScore: 138, percentile: 98 },
      english: { grade: 1.0 },
      math: { standardScore: 135, percentile: 95 },
      social1: { standardScore: 66, percentile: 96 },
      social2: { standardScore: 65, percentile: 95 }
    },
    admissionHistory: [
      { university: '서울대', major: '공예', result: 'Pending', type: 'Su-si (Early)', year: 2026 }
    ],
    similarCases: []
  },
  {
    id: 's27',
    name: '안준혁',
    grade: '2학년',
    school: '대원고',
    targetUniversity: '서울대',
    major: '디자인',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Junhyuk',
    artworks: [],
    academicScores: {
      korean: { standardScore: 136, percentile: 95, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 131, percentile: 91, grade: 1 },
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
  {
    id: 's28',
    name: '정예린',
    grade: '2학년',
    school: '현대고',
    targetUniversity: '이화여대',
    major: '산업디자인',
    currentLevel: 'B+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yerin',
    artworks: [],
    academicScores: {
      korean: { standardScore: 127, percentile: 90, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 119, percentile: 81, grade: 3 },
      social1: { subjectName: "동아시아사", standardScore: 59, percentile: 82, grade: 2 },
      social2: { subjectName: "정치와 법", standardScore: 56, percentile: 76, grade: 3 }
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
    id: 's29',
    name: '김나연',
    grade: '3학년',
    school: '이화여고',
    targetUniversity: '이화여대',
    major: '패션디자인',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Nayeon',
    artworks: [
      'https://images.unsplash.com/photo-1547891654-e66ed7ebb968?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 131, percentile: 93, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 120, percentile: 82, grade: 2 },
      social1: { standardScore: 63, percentile: 89, grade: 2 },
      social2: { standardScore: 61, percentile: 86, grade: 2 }
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
    id: 's30',
    name: '이채원',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '이화여대',
    major: '산업디자인',
    currentLevel: 'A+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Chaewon',
    artworks: [
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 129, percentile: 91, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 121, percentile: 83, grade: 2 },
      social1: { standardScore: 61, percentile: 87, grade: 2 },
      social2: { standardScore: 59, percentile: 84, grade: 2 }
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
    id: 's31',
    name: '박소은',
    grade: '3학년',
    school: '덕성여고',
    targetUniversity: '이화여대',
    major: '시각디자인',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Soeun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 126, percentile: 89, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 116, percentile: 79, grade: 3 },
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
    id: 's32',
    name: '최민지',
    grade: '2학년',
    school: '진선여고',
    targetUniversity: '이화여대',
    major: '패션디자인',
    currentLevel: 'B+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Minji',
    artworks: [],
    academicScores: {
      korean: { standardScore: 128, percentile: 90, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 118, percentile: 80, grade: 3 },
      social1: { standardScore: 60, percentile: 85, grade: 2 },
      social2: { standardScore: 58, percentile: 82, grade: 2 }
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
    id: 's33',
    name: '강서현',
    grade: '3학년',
    school: '숙명여고',
    targetUniversity: '이화여대',
    major: '산업디자인',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seohyun',
    artworks: [
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 130, percentile: 92, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 119, percentile: 81, grade: 3 },
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
  {
    id: 's34',
    name: '윤지안',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '이화여대',
    major: '시각디자인',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jian',
    artworks: [],
    academicScores: {
      korean: { standardScore: 125, percentile: 88, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 115, percentile: 78, grade: 3 },
      social1: { subjectName: "동아시아사", standardScore: 57, percentile: 79, grade: 2 },
      social2: { subjectName: "정치와 법", standardScore: 54, percentile: 74, grade: 3 }
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
    id: 's35',
    name: '홍예나',
    grade: '1학년',
    school: '이화여고',
    targetUniversity: '이화여대',
    major: '패션디자인',
    currentLevel: 'C',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yena',
    artworks: [],
    academicScores: {
      korean: { standardScore: 120, percentile: 85, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 110, percentile: 70, grade: 3 },
      social1: { standardScore: 55, percentile: 75, grade: 3 },
      social2: { standardScore: 53, percentile: 72, grade: 3 }
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
    id: 's36',
    name: '김태현',
    grade: '3학년',
    school: '경기고',
    targetUniversity: '국민대',
    major: '시각디자인',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Taehyun',
    artworks: [],
    academicScores: {
      korean: { standardScore: 127, percentile: 89, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 111, percentile: 71, grade: 3 },
      social1: { subjectName: "사회문화", standardScore: 61, percentile: 87, grade: 2 },
      social2: { subjectName: "윤리와 사상", standardScore: 59, percentile: 84, grade: 2 }
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
    id: 's37',
    name: '이서윤',
    grade: '2학년',
    school: '명덕고',
    targetUniversity: '국민대',
    major: '산업디자인',
    currentLevel: 'B+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seoyoon',
    artworks: [],
    academicScores: {
      korean: { standardScore: 126, percentile: 88, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 109, percentile: 69, grade: 3 },
      social1: { standardScore: 60, percentile: 85, grade: 2 },
      social2: { standardScore: 58, percentile: 81, grade: 2 }
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
    id: 's38',
    name: '장우빈',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '국민대',
    major: '시각디자인',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Woobin',
    artworks: [
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 129, percentile: 91, grade: 2 },
      english: { grade: 1 },
      math: { standardScore: 113, percentile: 73, grade: 3 },
      social1: { subjectName: "사회문화", standardScore: 63, percentile: 89, grade: 2 },
      social2: { subjectName: "윤리와 사상", standardScore: 61, percentile: 86, grade: 2 }
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
    id: 's39',
    name: '정민서',
    grade: '3학년',
    school: '한영고',
    targetUniversity: '국민대',
    major: '금속조형',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Minseo',
    artworks: [],
    academicScores: {
      korean: { standardScore: 124, percentile: 87, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 108, percentile: 68, grade: 3 },
      social1: { standardScore: 59, percentile: 83, grade: 2 },
      social2: { standardScore: 57, percentile: 79, grade: 3 }
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
    id: 's40',
    name: '오지호',
    grade: '2학년',
    school: '대원고',
    targetUniversity: '국민대',
    major: '시각디자인',
    currentLevel: 'B+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jiho',
    artworks: [],
    academicScores: {
      korean: { standardScore: 125, percentile: 85, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 110, percentile: 70, grade: 3 },
      social1: { subjectName: "사회문화", standardScore: 60, percentile: 85, grade: 2 },
      social2: { subjectName: "윤리와 사상", standardScore: 58, percentile: 80, grade: 2 }
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
    id: 's41',
    name: '신예준',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '국민대',
    major: '산업디자인',
    currentLevel: 'A+',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yejun',
    artworks: [
      'https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 130, percentile: 92, grade: 1 },
      english: { grade: 1 },
      math: { standardScore: 114, percentile: 74, grade: 2 },
      social1: { standardScore: 64, percentile: 91, grade: 1 },
      social2: { standardScore: 62, percentile: 88, grade: 1 }
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
    id: 's42',
    name: '류하람',
    grade: '3학년',
    school: '경기여고',
    targetUniversity: '국민대',
    major: '시각디자인',
    currentLevel: 'A',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Haram',
    artworks: [],
    academicScores: {
      korean: { standardScore: 128, percentile: 90, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 112, percentile: 72, grade: 2 },
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
    id: 's43',
    name: '노서진',
    grade: '1학년',
    school: '명덕고',
    targetUniversity: '국민대',
    major: '금속조형',
    currentLevel: 'C',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seojin',
    artworks: [],
    academicScores: {
      korean: { standardScore: 115, percentile: 75, grade: 4 },
      english: { grade: 3 },
      math: { standardScore: 105, percentile: 60, grade: 4 },
      social1: { standardScore: 54, percentile: 70, grade: 3 },
      social2: { standardScore: 52, percentile: 67, grade: 3 }
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
    id: 's44',
    name: '황민규',
    grade: '2학년',
    school: '한영고',
    targetUniversity: '국민대',
    major: '산업디자인',
    currentLevel: 'B',
    instructorId: 'i2',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mingyu',
    artworks: [],
    academicScores: {
      korean: { standardScore: 123, percentile: 86, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 107, percentile: 67, grade: 3 },
      social1: { standardScore: 58, percentile: 81, grade: 2 },
      social2: { standardScore: 56, percentile: 77, grade: 3 }
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
  },
  {
    id: 's45',
    name: '임준영',
    grade: '3학년',
    school: '대원고',
    targetUniversity: '건국대',
    major: '시각디자인',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Junyoung',
    artworks: [],
    academicScores: {
      korean: { standardScore: 122, percentile: 84, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 108, percentile: 68, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 56, percentile: 76, grade: 3 },
      social2: { subjectName: "지리", standardScore: 54, percentile: 72, grade: 3 }
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
  },
  {
    id: 's46',
    name: '김다혜',
    grade: '2학년',
    school: '압구정고',
    targetUniversity: '건국대',
    major: '커뮤니케이션',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Dahye',
    artworks: [],
    academicScores: {
      korean: { standardScore: 121, percentile: 83, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 106, percentile: 66, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 55, percentile: 75, grade: 3 },
      social2: { subjectName: "지리", standardScore: 53, percentile: 71, grade: 3 }
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
  },
  {
    id: 's47',
    name: '박시우',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '건국대',
    major: '시각디자인',
    currentLevel: 'A+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Siwoo',
    artworks: [
      'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 124, percentile: 87, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 109, percentile: 69, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 57, percentile: 77, grade: 2 },
      social2: { subjectName: "지리", standardScore: 55, percentile: 73, grade: 2 }
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
  },
  {
    id: 's48',
    name: '최예성',
    grade: '3학년',
    school: '경기고',
    targetUniversity: '건국대',
    major: '커뮤니케이션',
    currentLevel: 'B',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yesung',
    artworks: [],
    academicScores: {
      korean: { standardScore: 119, percentile: 81, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 104, percentile: 64, grade: 4 },
      social1: { subjectName: "한국사", standardScore: 54, percentile: 73, grade: 3 },
      social2: { subjectName: "지리", standardScore: 52, percentile: 69, grade: 3 }
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
  },
  {
    id: 's49',
    name: '강하늘',
    grade: '2학년',
    school: '명덕고',
    targetUniversity: '건국대',
    major: '시각디자인',
    currentLevel: 'B+',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Haneul2',
    artworks: [],
    academicScores: {
      korean: { standardScore: 120, percentile: 82, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 107, percentile: 67, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 55, percentile: 75, grade: 3 },
      social2: { subjectName: "지리", standardScore: 53, percentile: 71, grade: 3 }
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
  },
  {
    id: 's50',
    name: '윤서준',
    grade: '재수',
    school: 'N/A',
    targetUniversity: '건국대',
    major: '커뮤니케이션',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Seojun',
    artworks: [
      'https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=1000&auto=format&fit=crop'
    ],
    academicScores: {
      korean: { standardScore: 123, percentile: 86, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 111, percentile: 71, grade: 2 },
      social1: { subjectName: "한국사", standardScore: 56, percentile: 76, grade: 2 },
      social2: { subjectName: "지리", standardScore: 54, percentile: 72, grade: 2 }
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
  },
  {
    id: 's51',
    name: '조민아',
    grade: '3학년',
    school: '압구정고',
    targetUniversity: '건국대',
    major: '시각디자인',
    currentLevel: 'A',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mina',
    artworks: [],
    academicScores: {
      korean: { standardScore: 121, percentile: 83, grade: 2 },
      english: { grade: 2 },
      math: { standardScore: 108, percentile: 68, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 55, percentile: 75, grade: 3 },
      social2: { subjectName: "지리", standardScore: 53, percentile: 71, grade: 3 }
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
  },
  {
    id: 's52',
    name: '홍준서',
    grade: '1학년',
    school: '대원고',
    targetUniversity: '건국대',
    major: '커뮤니케이션',
    currentLevel: 'C',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Junseo2',
    artworks: [],
    academicScores: {
      korean: { standardScore: 112, percentile: 72, grade: 4 },
      english: { grade: 3 },
      math: { standardScore: 102, percentile: 52, grade: 4 },
      social1: { subjectName: "한국사", standardScore: 51, percentile: 62, grade: 4 },
      social2: { subjectName: "지리", standardScore: 49, percentile: 57, grade: 4 }
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
  },
  {
    id: 's53',
    name: '신유나',
    grade: '2학년',
    school: '경기여고',
    targetUniversity: '건국대',
    major: '시각디자인',
    currentLevel: 'B',
    instructorId: 'i1',
    avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yuna',
    artworks: [],
    academicScores: {
      korean: { standardScore: 118, percentile: 80, grade: 3 },
      english: { grade: 2 },
      math: { standardScore: 105, percentile: 65, grade: 3 },
      social1: { subjectName: "한국사", standardScore: 54, percentile: 73, grade: 3 },
      social2: { subjectName: "지리", standardScore: 52, percentile: 69, grade: 3 }
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
  { id: 'e14_3', studentId: 's14', date: getDate(10), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: '강점.', instructorId: 'i2' },

  // --- New Students Evaluations (s15-s53) ---
  
  // --- Min-jun Kang (s15) [Hongik A-] ---
  { id: 'e15_1', studentId: 's15', date: getDate(50), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '기본기 양호.', instructorId: 'i1' },
  { id: 'e15_2', studentId: 's15', date: getDate(35), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 향상.', instructorId: 'i1' },
  { id: 'e15_3', studentId: 's15', date: getDate(20), scores: { composition: 8.5, tone: 8, idea: 8, completeness: 8 }, totalScore: 81, notes: '안정적 성장.', instructorId: 'i1' },
  { id: 'e15_4', studentId: 's15', date: getDate(7), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: 'A- 수준 도달.', instructorId: 'i1' },

  // --- Seo-a Yoon (s16) [Hongik B+] ---
  { id: 'e16_1', studentId: 's16', date: getDate(48), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '평균 수준.', instructorId: 'i2' },
  { id: 'e16_2', studentId: 's16', date: getDate(33), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '조금씩 나아짐.', instructorId: 'i2' },
  { id: 'e16_3', studentId: 's16', date: getDate(18), scores: { composition: 8, tone: 7.5, idea: 8, completeness: 7.5 }, totalScore: 77.5, notes: 'B+ 진입.', instructorId: 'i2' },

  // --- Hyun-woo Jo (s17) [Hongik A] ---
  { id: 'e17_1', studentId: 's17', date: getDate(45), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: '재수생 치고 안정적.', instructorId: 'i1' },
  { id: 'e17_2', studentId: 's17', date: getDate(30), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8 }, totalScore: 82, notes: '기본기 탄탄.', instructorId: 'i1' },
  { id: 'e17_3', studentId: 's17', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 8.5 }, totalScore: 86, notes: 'A권 진입.', instructorId: 'i1' },

  // --- Ji-wu Lim (s18) [Hongik A+] ---
  { id: 'e18_1', studentId: 's18', date: getDate(55), scores: { composition: 8.5, tone: 8, idea: 8.5, completeness: 8 }, totalScore: 82, notes: '뛰어난 발상력.', instructorId: 'i1' },
  { id: 'e18_2', studentId: 's18', date: getDate(40), scores: { composition: 9, tone: 8.5, idea: 9, completeness: 8.5 }, totalScore: 87.5, notes: '최상급 수준.', instructorId: 'i1' },
  { id: 'e18_3', studentId: 's18', date: getDate(25), scores: { composition: 9.5, tone: 9, idea: 9, completeness: 9 }, totalScore: 91, notes: '탑 티어.', instructorId: 'i1' },
  { id: 'e18_4', studentId: 's18', date: getDate(10), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽함.', instructorId: 'i1' },

  // --- Do-yun Bae (s19) [Hongik B] ---
  { id: 'e19_1', studentId: 's19', date: getDate(42), scores: { composition: 6.5, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 67.5, notes: '기본기 보완 필요.', instructorId: 'i2' },
  { id: 'e19_2', studentId: 's19', date: getDate(27), scores: { composition: 7, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 71, notes: '느리지만 꾸준함.', instructorId: 'i2' },
  { id: 'e19_3', studentId: 's19', date: getDate(12), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i2' },

  // --- Ha-neul Song (s20) [Hongik C] ---
  { id: 'e20_1', studentId: 's20', date: getDate(38), scores: { composition: 5.5, tone: 6, idea: 6, completeness: 5.5 }, totalScore: 57.5, notes: '기초부터 다시.', instructorId: 'i2' },
  { id: 'e20_2', studentId: 's20', date: getDate(23), scores: { composition: 6, tone: 6.5, idea: 6, completeness: 6 }, totalScore: 61, notes: '조금씩 개선.', instructorId: 'i2' },
  { id: 'e20_3', studentId: 's20', date: getDate(8), scores: { composition: 6.5, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 65, notes: 'C권 상위.', instructorId: 'i2' },

  // --- Jun-seo Oh (s21) [SNU A] ---
  { id: 'e21_1', studentId: 's21', date: getDate(47), scores: { composition: 8, tone: 8.5, idea: 7.5, completeness: 8 }, totalScore: 80, notes: '학업 우수, 실기 보완.', instructorId: 'i1' },
  { id: 'e21_2', studentId: 's21', date: getDate(32), scores: { composition: 8.5, tone: 9, idea: 8, completeness: 8.5 }, totalScore: 85, notes: '균형잡힌 성장.', instructorId: 'i1' },
  { id: 'e21_3', studentId: 's21', date: getDate(17), scores: { composition: 9, tone: 9, idea: 8.5, completeness: 9 }, totalScore: 88.5, notes: 'A권 안정화.', instructorId: 'i1' },

  // --- Yu-jin Shin (s22) [SNU B+] ---
  { id: 'e22_1', studentId: 's22', date: getDate(44), scores: { composition: 7, tone: 7.5, idea: 6.5, completeness: 7 }, totalScore: 70, notes: '재수생, 기초 점검.', instructorId: 'i1' },
  { id: 'e22_2', studentId: 's22', date: getDate(29), scores: { composition: 7.5, tone: 8, idea: 7, completeness: 7.5 }, totalScore: 75, notes: '점진적 향상.', instructorId: 'i1' },
  { id: 'e22_3', studentId: 's22', date: getDate(14), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: 'B+ 수준.', instructorId: 'i1' },

  // --- Min-jae Hwang (s23) [SNU A+] ---
  { id: 'e23_1', studentId: 's23', date: getDate(52), scores: { composition: 8.5, tone: 8.5, idea: 8.5, completeness: 8 }, totalScore: 83.5, notes: '2학년 치고 뛰어남.', instructorId: 'i1' },
  { id: 'e23_2', studentId: 's23', date: getDate(37), scores: { composition: 9, tone: 9, idea: 9, completeness: 8.5 }, totalScore: 88.5, notes: '최상급 재능.', instructorId: 'i1' },
  { id: 'e23_3', studentId: 's23', date: getDate(22), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92, notes: 'A+ 수준.', instructorId: 'i1' },
  { id: 'e23_4', studentId: 's23', date: getDate(7), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽한 작품.', instructorId: 'i1' },

  // --- Seo-yeon Noh (s24) [SNU A] ---
  { id: 'e24_1', studentId: 's24', date: getDate(46), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '안정적 A권.', instructorId: 'i1' },
  { id: 'e24_2', studentId: 's24', date: getDate(31), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i1' },
  { id: 'e24_3', studentId: 's24', date: getDate(16), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i1' },

  // --- Ji-hun Moon (s25) [SNU B] ---
  { id: 'e25_1', studentId: 's25', date: getDate(43), scores: { composition: 6.5, tone: 7, idea: 6, completeness: 6.5 }, totalScore: 65, notes: '재수생, 기초 보완.', instructorId: 'i1' },
  { id: 'e25_2', studentId: 's25', date: getDate(28), scores: { composition: 7, tone: 7.5, idea: 6.5, completeness: 7 }, totalScore: 70, notes: '느린 향상.', instructorId: 'i1' },
  { id: 'e25_3', studentId: 's25', date: getDate(13), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7.5 }, totalScore: 73.5, notes: 'B권 진입.', instructorId: 'i1' },

  // --- Dae-un Ryu (s26) [SNU A+] ---
  { id: 'e26_1', studentId: 's26', date: getDate(49), scores: { composition: 9, tone: 8.5, idea: 9, completeness: 8.5 }, totalScore: 87.5, notes: '학업 실기 모두 우수.', instructorId: 'i1' },
  { id: 'e26_2', studentId: 's26', date: getDate(34), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92, notes: '최상급.', instructorId: 'i1' },
  { id: 'e26_3', studentId: 's26', date: getDate(19), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽함.', instructorId: 'i1' },

  // --- Jun-hyuk Ahn (s27) [SNU B+] ---
  { id: 'e27_1', studentId: 's27', date: getDate(41), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i1' },
  { id: 'e27_2', studentId: 's27', date: getDate(26), scores: { composition: 8, tone: 8, idea: 8, completeness: 7.5 }, totalScore: 78.5, notes: '점진적 성장.', instructorId: 'i1' },
  { id: 'e27_3', studentId: 's27', date: getDate(11), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i1' },

  // --- Ye-rin Jung (s28) [Ewha B+] ---
  { id: 'e28_1', studentId: 's28', date: getDate(48), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '2학년, 기본기 양호.', instructorId: 'i2' },
  { id: 'e28_2', studentId: 's28', date: getDate(33), scores: { composition: 8, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 76, notes: '조금씩 향상.', instructorId: 'i2' },
  { id: 'e28_3', studentId: 's28', date: getDate(18), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 진입.', instructorId: 'i2' },

  // --- Na-yeon Kim (s29) [Ewha A] ---
  { id: 'e29_1', studentId: 's29', date: getDate(45), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: '안정적 A권.', instructorId: 'i2' },
  { id: 'e29_2', studentId: 's29', date: getDate(30), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i2' },
  { id: 'e29_3', studentId: 's29', date: getDate(15), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i2' },

  // --- Chae-won Lee (s30) [Ewha A+] ---
  { id: 'e30_1', studentId: 's30', date: getDate(50), scores: { composition: 8.5, tone: 8.5, idea: 8.5, completeness: 8 }, totalScore: 83.5, notes: '재수생, 뛰어난 실기.', instructorId: 'i2' },
  { id: 'e30_2', studentId: 's30', date: getDate(35), scores: { composition: 9, tone: 9, idea: 9, completeness: 8.5 }, totalScore: 88.5, notes: '최상급 수준.', instructorId: 'i2' },
  { id: 'e30_3', studentId: 's30', date: getDate(20), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92, notes: 'A+ 수준.', instructorId: 'i2' },
  { id: 'e30_4', studentId: 's30', date: getDate(5), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽함.', instructorId: 'i2' },

  // --- So-eun Park (s31) [Ewha B] ---
  { id: 'e31_1', studentId: 's31', date: getDate(44), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '평균 수준.', instructorId: 'i2' },
  { id: 'e31_2', studentId: 's31', date: getDate(29), scores: { composition: 7.5, tone: 7, idea: 7, completeness: 7 }, totalScore: 71, notes: '느린 향상.', instructorId: 'i2' },
  { id: 'e31_3', studentId: 's31', date: getDate(14), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i2' },

  // --- Min-ji Choi (s32) [Ewha B+] ---
  { id: 'e32_1', studentId: 's32', date: getDate(42), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i2' },
  { id: 'e32_2', studentId: 's32', date: getDate(27), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 성장.', instructorId: 'i2' },
  { id: 'e32_3', studentId: 's32', date: getDate(12), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i2' },

  // --- Seo-hyun Kang (s33) [Ewha A] ---
  { id: 'e33_1', studentId: 's33', date: getDate(43), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '안정적 A권.', instructorId: 'i2' },
  { id: 'e33_2', studentId: 's33', date: getDate(28), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i2' },
  { id: 'e33_3', studentId: 's33', date: getDate(13), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i2' },

  // --- Jian Yoon (s34) [Ewha B] ---
  { id: 'e34_1', studentId: 's34', date: getDate(41), scores: { composition: 6.5, tone: 7, idea: 6.5, completeness: 6.5 }, totalScore: 66.5, notes: '재수생, 기초 점검.', instructorId: 'i2' },
  { id: 'e34_2', studentId: 's34', date: getDate(26), scores: { composition: 7, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 71, notes: '조금씩 나아짐.', instructorId: 'i2' },
  { id: 'e34_3', studentId: 's34', date: getDate(11), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 진입.', instructorId: 'i2' },

  // --- Ye-na Hong (s35) [Ewha C] ---
  { id: 'e35_1', studentId: 's35', date: getDate(36), scores: { composition: 5.5, tone: 6, idea: 5.5, completeness: 5.5 }, totalScore: 56.5, notes: '1학년, 기초부터.', instructorId: 'i2' },
  { id: 'e35_2', studentId: 's35', date: getDate(21), scores: { composition: 6, tone: 6.5, idea: 6, completeness: 6 }, totalScore: 61, notes: '조금씩 개선.', instructorId: 'i2' },
  { id: 'e35_3', studentId: 's35', date: getDate(6), scores: { composition: 6.5, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 65, notes: 'C권 상위.', instructorId: 'i2' },

  // --- Tae-hyun Kim (s36) [Kookmin A] ---
  { id: 'e36_1', studentId: 's36', date: getDate(46), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: '안정적 A권.', instructorId: 'i2' },
  { id: 'e36_2', studentId: 's36', date: getDate(31), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i2' },
  { id: 'e36_3', studentId: 's36', date: getDate(16), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i2' },

  // --- Seo-yoon Lee (s37) [Kookmin B+] ---
  { id: 'e37_1', studentId: 's37', date: getDate(44), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i2' },
  { id: 'e37_2', studentId: 's37', date: getDate(29), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 성장.', instructorId: 'i2' },
  { id: 'e37_3', studentId: 's37', date: getDate(14), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i2' },

  // --- Woobin Jang (s38) [Kookmin A] ---
  { id: 'e38_1', studentId: 's38', date: getDate(47), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '재수생, 안정적.', instructorId: 'i2' },
  { id: 'e38_2', studentId: 's38', date: getDate(32), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i2' },
  { id: 'e38_3', studentId: 's38', date: getDate(17), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i2' },

  // --- Min-seo Jung (s39) [Kookmin B] ---
  { id: 'e39_1', studentId: 's39', date: getDate(45), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '평균 수준.', instructorId: 'i2' },
  { id: 'e39_2', studentId: 's39', date: getDate(30), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '조금씩 향상.', instructorId: 'i2' },
  { id: 'e39_3', studentId: 's39', date: getDate(15), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i2' },

  // --- Ji-ho Oh (s40) [Kookmin B+] ---
  { id: 'e40_1', studentId: 's40', date: getDate(43), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i2' },
  { id: 'e40_2', studentId: 's40', date: getDate(28), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 성장.', instructorId: 'i2' },
  { id: 'e40_3', studentId: 's40', date: getDate(13), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i2' },

  // --- Ye-jun Shin (s41) [Kookmin A+] ---
  { id: 'e41_1', studentId: 's41', date: getDate(48), scores: { composition: 8.5, tone: 8.5, idea: 8.5, completeness: 8 }, totalScore: 83.5, notes: '재수생, 뛰어난 실기.', instructorId: 'i2' },
  { id: 'e41_2', studentId: 's41', date: getDate(33), scores: { composition: 9, tone: 9, idea: 9, completeness: 8.5 }, totalScore: 88.5, notes: '최상급 수준.', instructorId: 'i2' },
  { id: 'e41_3', studentId: 's41', date: getDate(18), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92, notes: 'A+ 수준.', instructorId: 'i2' },
  { id: 'e41_4', studentId: 's41', date: getDate(3), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽함.', instructorId: 'i2' },

  // --- Haram Ryu (s42) [Kookmin A] ---
  { id: 'e42_1', studentId: 's42', date: getDate(46), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '안정적 A권.', instructorId: 'i2' },
  { id: 'e42_2', studentId: 's42', date: getDate(31), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i2' },
  { id: 'e42_3', studentId: 's42', date: getDate(16), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i2' },

  // --- Seo-jin Noh (s43) [Kookmin C] ---
  { id: 'e43_1', studentId: 's43', date: getDate(35), scores: { composition: 5.5, tone: 6, idea: 5.5, completeness: 5.5 }, totalScore: 56.5, notes: '1학년, 기초부터.', instructorId: 'i2' },
  { id: 'e43_2', studentId: 's43', date: getDate(20), scores: { composition: 6, tone: 6.5, idea: 6, completeness: 6 }, totalScore: 61, notes: '조금씩 개선.', instructorId: 'i2' },
  { id: 'e43_3', studentId: 's43', date: getDate(5), scores: { composition: 6.5, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 65, notes: 'C권 상위.', instructorId: 'i2' },

  // --- Min-gyu Hwang (s44) [Kookmin B] ---
  { id: 'e44_1', studentId: 's44', date: getDate(42), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '2학년, 평균 수준.', instructorId: 'i2' },
  { id: 'e44_2', studentId: 's44', date: getDate(27), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '조금씩 향상.', instructorId: 'i2' },
  { id: 'e44_3', studentId: 's44', date: getDate(12), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i2' },

  // --- Jun-young Lim (s45) [Konkuk A] ---
  { id: 'e45_1', studentId: 's45', date: getDate(47), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: '안정적 A권.', instructorId: 'i1' },
  { id: 'e45_2', studentId: 's45', date: getDate(32), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i1' },
  { id: 'e45_3', studentId: 's45', date: getDate(17), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i1' },

  // --- Da-hye Kim (s46) [Konkuk B+] ---
  { id: 'e46_1', studentId: 's46', date: getDate(45), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i1' },
  { id: 'e46_2', studentId: 's46', date: getDate(30), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 성장.', instructorId: 'i1' },
  { id: 'e46_3', studentId: 's46', date: getDate(15), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i1' },

  // --- Si-woo Park (s47) [Konkuk A+] ---
  { id: 'e47_1', studentId: 's47', date: getDate(49), scores: { composition: 8.5, tone: 8.5, idea: 8.5, completeness: 8 }, totalScore: 83.5, notes: '재수생, 뛰어난 실기.', instructorId: 'i1' },
  { id: 'e47_2', studentId: 's47', date: getDate(34), scores: { composition: 9, tone: 9, idea: 9, completeness: 8.5 }, totalScore: 88.5, notes: '최상급 수준.', instructorId: 'i1' },
  { id: 'e47_3', studentId: 's47', date: getDate(19), scores: { composition: 9.5, tone: 9, idea: 9.5, completeness: 9 }, totalScore: 92, notes: 'A+ 수준.', instructorId: 'i1' },
  { id: 'e47_4', studentId: 's47', date: getDate(4), scores: { composition: 9.5, tone: 9.5, idea: 9.5, completeness: 9.5 }, totalScore: 95, notes: '완벽함.', instructorId: 'i1' },

  // --- Ye-sung Choi (s48) [Konkuk B] ---
  { id: 'e48_1', studentId: 's48', date: getDate(44), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '평균 수준.', instructorId: 'i1' },
  { id: 'e48_2', studentId: 's48', date: getDate(29), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '조금씩 향상.', instructorId: 'i1' },
  { id: 'e48_3', studentId: 's48', date: getDate(14), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i1' },

  // --- Ha-neul Kang (s49) [Konkuk B+] ---
  { id: 'e49_1', studentId: 's49', date: getDate(43), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7 }, totalScore: 73.5, notes: '2학년, 무난함.', instructorId: 'i1' },
  { id: 'e49_2', studentId: 's49', date: getDate(28), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 7.5 }, totalScore: 77.5, notes: '점진적 성장.', instructorId: 'i1' },
  { id: 'e49_3', studentId: 's49', date: getDate(13), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: 'B+ 수준.', instructorId: 'i1' },

  // --- Seo-jun Yoon (s50) [Konkuk A] ---
  { id: 'e50_1', studentId: 's50', date: getDate(48), scores: { composition: 8, tone: 8, idea: 8, completeness: 8 }, totalScore: 80, notes: '재수생, 안정적.', instructorId: 'i1' },
  { id: 'e50_2', studentId: 's50', date: getDate(33), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i1' },
  { id: 'e50_3', studentId: 's50', date: getDate(18), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i1' },

  // --- Mina Jo (s51) [Konkuk A] ---
  { id: 'e51_1', studentId: 's51', date: getDate(46), scores: { composition: 8, tone: 8, idea: 7.5, completeness: 8 }, totalScore: 78.5, notes: '안정적 A권.', instructorId: 'i1' },
  { id: 'e51_2', studentId: 's51', date: getDate(31), scores: { composition: 8.5, tone: 8.5, idea: 8, completeness: 8.5 }, totalScore: 83.5, notes: '일관성 좋음.', instructorId: 'i1' },
  { id: 'e51_3', studentId: 's51', date: getDate(16), scores: { composition: 9, tone: 8.5, idea: 8.5, completeness: 9 }, totalScore: 87.5, notes: 'A권 상위.', instructorId: 'i1' },

  // --- Jun-seo Hong (s52) [Konkuk C] ---
  { id: 'e52_1', studentId: 's52', date: getDate(32), scores: { composition: 5.5, tone: 6, idea: 5.5, completeness: 5.5 }, totalScore: 56.5, notes: '1학년, 기초부터.', instructorId: 'i1' },
  { id: 'e52_2', studentId: 's52', date: getDate(17), scores: { composition: 6, tone: 6.5, idea: 6, completeness: 6 }, totalScore: 61, notes: '조금씩 개선.', instructorId: 'i1' },
  { id: 'e52_3', studentId: 's52', date: getDate(2), scores: { composition: 6.5, tone: 6.5, idea: 6.5, completeness: 6.5 }, totalScore: 65, notes: 'C권 상위.', instructorId: 'i1' },

  // --- Yuna Shin (s53) [Konkuk B] ---
  { id: 'e53_1', studentId: 's53', date: getDate(41), scores: { composition: 7, tone: 7, idea: 7, completeness: 6.5 }, totalScore: 68.5, notes: '2학년, 평균 수준.', instructorId: 'i1' },
  { id: 'e53_2', studentId: 's53', date: getDate(26), scores: { composition: 7.5, tone: 7.5, idea: 7, completeness: 7 }, totalScore: 72.5, notes: '조금씩 향상.', instructorId: 'i1' },
  { id: 'e53_3', studentId: 's53', date: getDate(11), scores: { composition: 7.5, tone: 7.5, idea: 7.5, completeness: 7.5 }, totalScore: 75, notes: 'B권 안정화.', instructorId: 'i1' }

].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

export const getStudentById = (id: string) => STUDENTS.find(s => s.id === id);
export const getEvaluationsByStudentId = (id: string) => EVALUATIONS.filter(e => e.studentId === id).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());