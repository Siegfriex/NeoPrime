# NeoPrime 프론트엔드 요구사항 명세서 (FRD)
## Frontend Requirements Document

**버전**: 1.0  
**작성일**: 2026-01-21  
**기준**: 실제 구현 코드 분석 완료  
**검증 상태**: ✅ 코드베이스 검증 완료

---

## 📋 문서 개요

### 1.1 목적
본 문서는 NeoPrime 웹 대시보드의 실제 구현된 프론트엔드 화면 및 기능에 대한 상세 명세서입니다. 실제 코드베이스를 기준으로 작성되었으며, 향후 유지보수 및 확장 개발의 기준 문서로 사용됩니다.

### 1.2 범위
- **플랫폼**: 웹 대시보드 (React 19.2.3 + TypeScript 5.8.2 + Vite 6.2.0)
- **대상 사용자**: 원장, 강사
- **페이지 수**: 11개
- **컴포넌트 수**: 4개 (공통)
- **서비스 레이어**: 3개

### 1.3 기술 스택

```json
{
  "core": {
    "react": "^19.2.3",
    "react-dom": "^19.2.3",
    "react-router-dom": "^7.12.0",
    "typescript": "~5.8.2",
    "vite": "^6.2.0"
  },
  "ui": {
    "recharts": "^3.6.0",
    "lucide-react": "^0.562.0"
  },
  "ai": {
    "@google/genai": "^1.37.0"
  }
}
```

### 1.4 프로젝트 구조

```
frontend/neoprime/
├── components/          # 공통 컴포넌트 (4개)
│   ├── ChatBot.tsx     # AI 챗봇
│   ├── Header.tsx      # 헤더
│   ├── Layout.tsx      # 레이아웃 래퍼
│   └── Sidebar.tsx     # 사이드바 네비게이션
├── pages/              # 페이지 컴포넌트 (11개)
│   ├── Dashboard.tsx
│   ├── StudentList.tsx
│   ├── StudentDetail.tsx
│   ├── StudentAdd.tsx
│   ├── EvaluationEntry.tsx
│   ├── Analytics.tsx
│   ├── AdmissionSimulator.tsx
│   ├── Login.tsx
│   ├── Signup.tsx
│   ├── Settings.tsx
│   └── Profile.tsx
├── services/           # 비즈니스 로직 (3개)
│   ├── geminiService.ts
│   ├── mockData.ts
│   └── storageService.ts
├── App.tsx            # 라우팅 설정
├── types.ts           # TypeScript 타입 정의
└── index.tsx          # 엔트리 포인트
```

---

## 🗺️ 라우팅 구조

### 2.1 라우터 설정

**라우터 타입**: HashRouter (SPA)  
**파일**: `App.tsx`

```typescript
// 인증 레이아웃 (사이드바/헤더 없음)
<Route path="/auth" element={<AuthLayout />}>
  <Route path="login" element={<Login />} />
  <Route path="signup" element={<Signup />} />
</Route>

// 메인 레이아웃 (사이드바 + 헤더)
<Route path="/" element={<Layout />}>
  <Route index element={<Dashboard />} />
  <Route path="students" element={<StudentList />} />
  <Route path="students/new" element={<StudentAdd />} />
  <Route path="students/:id" element={<StudentDetail />} />
  <Route path="evaluations/new" element={<EvaluationEntry />} />
  <Route path="analytics" element={<Analytics />} />
  <Route path="simulation" element={<AdmissionSimulator />} />
  <Route path="settings" element={<Settings />} />
  <Route path="profile" element={<Profile />} />
</Route>
```

### 2.2 라우팅 맵

| 경로 | 컴포넌트 | 레이아웃 | 설명 |
|------|---------|---------|------|
| `/` | Dashboard | Layout | 메인 대시보드 |
| `/students` | StudentList | Layout | 학생 목록 & 분석 |
| `/students/new` | StudentAdd | Layout | 학생 추가 |
| `/students/:id` | StudentDetail | Layout | 학생 상세 |
| `/evaluations/new` | EvaluationEntry | Layout | 평가 입력 |
| `/analytics` | Analytics | Layout | 고급 분석 |
| `/simulation` | AdmissionSimulator | Layout | 입시 시뮬레이터 |
| `/settings` | Settings | Layout | 설정 |
| `/profile` | Profile | Layout | 프로필 |
| `/auth/login` | Login | AuthLayout | 로그인 |
| `/auth/signup` | Signup | AuthLayout | 회원가입 |

---

## 📊 데이터 구조

### 3.1 타입 정의

**파일**: `types.ts`

#### Student 인터페이스

```typescript
interface Student {
  id: string;
  name: string;
  grade: '1학년' | '2학년' | '3학년' | '재수';
  school: string;
  targetUniversity: string;
  major: string;
  currentLevel: 'A+' | 'A' | 'B+' | 'B' | 'C';
  instructorId: string;
  avatarUrl: string;
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
```

#### EvaluationScore 인터페이스

```typescript
interface EvaluationScore {
  composition: number;  // 0-10 (구도)
  tone: number;         // 0-10 (톤/명암)
  idea: number;         // 0-10 (발상)
  completeness: number; // 0-10 (완성도)
}
```

#### Evaluation 인터페이스

```typescript
interface Evaluation {
  id: string;
  studentId: string;
  date: string; // ISO format
  scores: EvaluationScore;
  totalScore: number; // 0-100 (scaled)
  notes: string;
  aiFeedback?: {
    strengths: string;
    weaknesses: string;
    actionPlan: string;
  };
  instructorId: string;
}
```

### 3.2 Mock 데이터

**파일**: `services/mockData.ts`

- **학생 수**: 20명
- **대학별 분포**:
  - 홍익대: 12명
  - 서울대: 3명
  - 이화여대: 3명
  - 국민대: 2명

---

## 🎨 화면별 상세 명세

### 화면 1: Dashboard (`/`)

**파일**: `pages/Dashboard.tsx`  
**라인 수**: 539줄  
**상태**: ✅ 구현 완료

#### 1.1 레이아웃 구조

```
┌─────────────────────────────────────────────────────────┐
│ KPI Strip (12 cols)                                     │
│ ┌──────────────┐ ┌────┐ ┌────┐                        │
│ │ Season Bar   │ │KPI1 │ │KPI2│                        │
│ │ (8 cols)     │ │(2)  │ │(2) │                        │
│ └──────────────┘ └────┘ └────┘                        │
├─────────────────────────────────────────────────────────┤
│ Strategy & Gaps (12 cols)                              │
│ ┌──────────────────┐ ┌──────────────┐                 │
│ │ University Chart │ │ Gap Analysis │                 │
│ │ (8 cols)         │ │ (4 cols)     │                 │
│ └──────────────────┘ └──────────────┘                 │
├─────────────────────────────────────────────────────────┤
│ Risk Table (12 cols)                                    │
│ ┌──────────────────────────────────────────────────┐   │
│ │ University Risk Diagnosis Table                  │   │
│ └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│ Action Queue & Trends (12 cols)                        │
│ ┌──────────┐ ┌──────────────────────────────────┐     │
│ │ Action   │ │ Cohort Performance Trend         │     │
│ │ Queue    │ │ (Area Chart)                     │     │
│ │ (4 cols) │ │ (6 cols)                         │     │
│ └──────────┘ └──────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│ Critical Students & Reports (12 cols)                  │
│ ┌──────────────┐ ┌──────────┐ ┌──────────┐           │
│ │ Critical     │ │ Data     │ │ Report   │           │
│ │ Students     │ │ Health   │ │ Button   │           │
│ │ (6 cols)     │ │ (3 cols) │ │ (3 cols) │           │
│ └──────────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────┘
```

#### 1.2 컴포넌트 명세

##### SeasonContextBar (시즌 컨텍스트 바)

**위치**: KPI Strip 좌측 (8 cols)

**Props**: 없음 (내부 상태 사용)

**상태**:
```typescript
const SEASON_TARGET_PASS = 52;  // 목표 합격 인원
const SEASON_CURRENT_PRED = 45; // 현재 예상 합격 인원
```

**UI 요소**:
- 시즌 정보: "2026 시즌 • 7주차"
- 현재/목표 표시: "45명 합격 예상 / 52명 목표"
- 갭 표시: "-7명" (목표 대비)
- 프로그레스 바: 45/52 (86.5%)
- 80% 기준선 표시

**스타일**:
- 배경: `bg-white`
- 테두리: `border border-gray-200`
- 프로그레스 바 색상: `#FC6401` (NeoPrime Orange)

##### KPI 카드 (재원생)

**위치**: KPI Strip 중앙 (2 cols)

**데이터**:
```typescript
const studentCount = STUDENTS.length; // 20명
const yearOverYear = "+5%"; // 작년 대비
```

**UI 요소**:
- 아이콘: `Users` (파란색 배경)
- 수치: "20명"
- 라벨: "재원생"
- 배지: "작년 대비 +5%" (초록색)

##### KPI 카드 (리스크 경고)

**위치**: KPI Strip 우측 (2 cols)

**데이터**:
```typescript
const criticalStudents = STUDENTS.filter(
  s => s.currentLevel === 'C' || s.currentLevel === 'B'
).slice(0, 5);
```

**UI 요소**:
- 아이콘: `AlertTriangle` (빨간색 배경)
- 수치: "5명"
- 라벨: "리스크 경고"
- 배지: "조치 필요" (빨간색)

##### 대학별 지원 라인 분포 차트

**위치**: Strategy & Gaps 좌측 (8 cols)

**차트 타입**: ComposedChart (Bar + Line)

**데이터 처리**:
```typescript
const univStats = useMemo(() => {
  // 대학별 그룹핑
  const stats: Record<string, UnivAggData> = {};
  
  STUDENTS.forEach(s => {
    if (!stats[s.targetUniversity]) {
      stats[s.targetUniversity] = {
        name: displayName,
        applicants: 0,
        levels: { top: 0, high: 0, mid: 0, low: 0 },
        predPassCount: 0,
        predPassRate: 0,
        lastYearPassRate: lastYearRate,
        riskLevel: 'Low',
        trend: rawTrend.map((v, i) => ({ i, v }))
      };
    }
    
    // 레벨별 분류
    if (s.currentLevel === 'A+') stats[s.targetUniversity].levels.top += 1;
    else if (s.currentLevel === 'A') stats[s.targetUniversity].levels.high += 1;
    else if (s.currentLevel === 'B+') stats[s.targetUniversity].levels.mid += 1;
    else stats[s.targetUniversity].levels.low += 1;
  });
  
  // 예상 합격자 계산
  Object.values(stats).forEach(u => {
    const weightedScore = 
      (u.levels.top * 1.0) + 
      (u.levels.high * 0.8) + 
      (u.levels.mid * 0.4) + 
      (u.levels.low * 0.1);
    u.predPassCount = Math.round(weightedScore);
    u.predPassRate = Math.round((u.predPassCount / u.applicants) * 100);
    
    // 리스크 레벨 판정
    const gap = u.predPassRate - u.lastYearPassRate;
    const lowRatio = (u.levels.low + u.levels.mid) / u.applicants;
    
    if (gap < -10 || lowRatio > 0.6) u.riskLevel = 'High';
    else if (gap < -5 || lowRatio > 0.4) u.riskLevel = 'Mid';
    else u.riskLevel = 'Low';
  });
  
  return Object.values(stats).sort((a, b) => b.applicants - a.applicants).slice(0, 5);
}, []);
```

**차트 구성**:
- **X축**: 대학명 (홍익대, 서울대, 이화여대, 국민대, 건국대)
- **Y축 Left**: 지원자 수 (Stacked Bar)
  - 최상위: `#FC6401`
  - 상위: `#FEA267`
  - 중위: `#FFC199`
  - 하위: `#E5E7EB`
- **Y축 Right**: 합격률 % (Dashed Line)
  - 작년 합격률: 회색 점선

**인터랙션**:
- 대학 클릭 → `/analytics?univ=대학명` 이동
- 호버 시 툴팁 표시

##### 전략적 갭 분석 카드

**위치**: Strategy & Gaps 우측 (4 cols)

**스타일**:
- 배경: Dark Mode (`#1F2937`)
- 오렌지 블러 효과: 우상단

**데이터**:
- 홍익대 티어 격차: -18%p
- 2025 합격자: 42% 최상위/상위
- 2026 현재: 24% 최상위/상위

**액션 버튼**:
- "중위권 후보 보기" → Analytics 이동

##### 대학별 리스크 진단 테이블

**위치**: Risk Table 섹션 (12 cols)

**테이블 컬럼**:
1. 대학명
2. 지원자 수
3. 예상 합격률 %
4. 작년 대비 (±%)
5. 최근 추세 (Sparkline)
6. 리스크 레벨 (배지)

**인터랙션**:
- 행 클릭 → Analytics 이동
- 호버 시 배경 변경 (`hover:bg-gray-50`)
- Sparkline 호버 시 불투명도 증가

**데이터 소스**: `univStats` (Top 5 대학)

##### 실행 큐 (Action Queue)

**위치**: Action Queue & Trends 좌측 (4 cols)

**데이터 구조**:
```typescript
const actionQueue = [
  {
    priority: 'P0',
    title: '홍익대 발상 워크샵 배정',
    description: '중위 티어 학생(12명) 특별 세션',
    completed: false
  },
  {
    priority: 'P1',
    title: '서울대 평가 누락 확인',
    description: '서울대 지망생 3명 누락 기록 검토',
    completed: false
  }
];
```

**UI 요소**:
- 타이틀: "실행 큐 (Action Queue)"
- 배지: "3개 대기중"
- 체크박스 리스트
- "+ 전략 과제 추가" 버튼 (점선 테두리)

##### 코호트 성과 추이 차트

**위치**: Action Queue & Trends 우측 (6 cols)

**차트 타입**: AreaChart (Dual Line)

**데이터**:
```typescript
const cohortSeasonalData = [
  { month: '3월', curScore: 72, prevScore: 70 },
  { month: '4월', curScore: 74, prevScore: 72 },
  { month: '5월', curScore: 75, prevScore: 73 },
  { month: '6월', curScore: 78, prevScore: 75 },
  { month: '7월', curScore: 80, prevScore: 77 },
  { month: '8월', curScore: 82, prevScore: 78 },
  { month: '9월', curScore: 85, prevScore: 80 },
  { month: '10월', curScore: 86, prevScore: 82 },
];
```

**차트 구성**:
- **X축**: 월 (3월~10월)
- **Y축**: 평균 점수 (60-90 범위)
- **라인 1**: 2026 현재 (실선, 면적, 오렌지)
- **라인 2**: 2025 작년 (점선, 회색)

**인사이트 카드**:
- 현재 평균: 86점 (+4 상승)
- 모멘텀: "가속화" (초록색, TrendingUp 아이콘)

##### 집중 관리 대상

**위치**: Critical Students & Reports 좌측 (6 cols)

**데이터**:
```typescript
const criticalStudents = STUDENTS
  .filter(s => s.currentLevel === 'C' || s.currentLevel === 'B')
  .slice(0, 5);
```

**UI 요소**:
- 아바타 + 이름 + 목표 대학 + 레벨
- 우측 화살표 → StudentDetail 이동
- 최대 3명 표시

##### 데이터 건전성 & 리포트

**위치**: Critical Students & Reports 중앙/우측 (6 cols)

**데이터 건전성 카드**:
- 유효율: 94%
- 아이콘: `CheckCircle2` (초록색)
- 누락: "이번 주 12건의 평가 누락"

**리포트 생성 버튼**:
- 배경: `#FC6401`
- 아이콘: `FileText`
- 그림자 효과: `shadow-lg shadow-[#FC6401]/20`
- 호버 시 스케일 애니메이션: `active:scale-95`

---

### 화면 2: StudentList (`/students`)

**파일**: `pages/StudentList.tsx`  
**라인 수**: 563줄  
**상태**: ✅ 구현 완료

#### 2.1 레이아웃 구조

```
┌─────────────────────────────────────────────────────────┐
│ Page Header                                              │
│ ┌──────────────────────────────┐ ┌──────────┐          │
│ │ Title + Subtitle             │ │ Add Btn  │          │
│ └──────────────────────────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────┤
│ Search Bar                                               │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 🔍 학생 이름, 학교 또는 목표 대학 검색...        │   │
│ └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│ University Groups (Accordion)                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 📚 홍익대 (12명 지원) ▼                         │   │
│ │ ┌────────────────────────────────────────────┐ │   │
│ │ │ Analysis Dashboard                          │ │   │
│ │ │ ┌──────────────────┐ ┌──────────────────┐ │ │   │
│ │ │ │ Scatter Plot     │ │ Side Panel        │ │   │
│ │ │ │ (Chart Area)     │ │ (Conditional)    │ │   │
│ │ │ └──────────────────┘ └──────────────────┘ │   │
│ │ │ Student Cards Grid                          │   │
│ │ └────────────────────────────────────────────┘ │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 2.2 상태 관리

```typescript
const [searchTerm, setSearchTerm] = useState('');
const [expandedUniv, setExpandedUniv] = useState<string | null>(null);
const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);
const [viewMode, setViewMode] = useState<'standard' | 'cluster'>('standard');
const [showZones, setShowZones] = useState(true);
const [showTrend, setShowTrend] = useState(false);
const [selectedPoint, setSelectedPoint] = useState<any>(null);
```

#### 2.3 주요 기능

##### 대학별 그룹화

**로직**:
```typescript
const groupedStudents = useMemo(() => {
  return STUDENTS.reduce((acc, student) => {
    const univ = student.targetUniversity;
    if (!acc[univ]) acc[univ] = [];
    acc[univ].push(student);
    return acc;
  }, {} as Record<string, Student[]>);
}, []);
```

**필터링**:
```typescript
const filteredGroups = useMemo(() => {
  return Object.entries(groupedStudents).reduce((acc, [univ, students]) => {
    const filtered = students.filter(s => 
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.school.toLowerCase().includes(searchTerm.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[univ] = filtered;
    }
    return acc;
  }, {} as Record<string, Student[]>);
}, [groupedStudents, searchTerm]);
```

##### 상대적 위치 분석 (Scatter Plot)

**데이터 계산**:
```typescript
const getAnalysisData = (students: Student[]) => {
  const avgAcademic = students.reduce(
    (sum, s) => sum + (s.academicScores.korean.standardScore || 100), 
    0
  ) / students.length;
  
  return students.map(s => {
    const rawAcademic = s.academicScores.korean.standardScore || 100;
    const rawPractical = getPracticalScore(s.currentLevel);
    
    // 정규화 (0-100)
    const academicIndex = Math.min(
      Math.max(50 + (rawAcademic - avgAcademic) * 2.5, 20), 
      98
    );
    const practicalIndex = Math.min(Math.max(rawPractical, 20), 98);
    
    // 라인 타입 판정
    let lineType: 'Safe' | 'Reach' | 'Stable' = 'Reach';
    let predictedProb = 30;
    
    if (academicIndex > 75 && practicalIndex > 75) {
      lineType = 'Safe';
      predictedProb = 85 + Math.random() * 10;
    } else if (academicIndex > 60 || practicalIndex > 80) {
      lineType = 'Stable';
      predictedProb = 60 + Math.random() * 15;
    }
    
    // 클러스터 할당
    let cluster = 0; // 0: Balanced/Low, 1: Elite, 2: Academic, 3: Practical
    if (academicIndex > 70 && practicalIndex > 70) cluster = 1;
    else if (academicIndex > practicalIndex + 10) cluster = 2;
    else if (practicalIndex > academicIndex + 10) cluster = 3;
    
    return {
      id: s.id,
      name: s.name,
      grade: s.grade,
      academicIndex: Math.round(academicIndex),
      practicalIndex: Math.round(practicalIndex),
      lineType,
      predictedProb: Math.round(predictedProb),
      cluster,
      originalLevel: s.currentLevel,
      avatarUrl: s.avatarUrl
    };
  });
};
```

**실기 점수 매핑**:
```typescript
const getPracticalScore = (level: string) => {
  switch(level) {
    case 'A+': return 98;
    case 'A': return 92;
    case 'B+': return 85;
    case 'B': return 78;
    case 'C': return 65;
    default: return 50;
  }
};
```

**차트 구성**:
- **X축**: 학업 상대 위치 (20-100)
- **Y축**: 실기 상대 위치 (20-100)
- **Quadrant 배경**:
  - Elite Group (우상단, 연한 초록)
  - Risk Group (좌하단, 연한 빨강)
  - Academic Driven (우하단, 연한 파랑)
  - Practical Driven (좌상단, 연한 오렌지)
- **포인트 크기**: 합격 확률 80%+ → r=6, 그 외 r=4
- **포인트 색상**: 뷰 모드에 따라 동적 변경
- **선택 효과**: 클릭 시 r=8, 테두리 추가

**뷰 모드**:
- **기본 보기**: 라인 타입별 색상 (Safe/Stable/Reach)
- **군집 보기**: 4가지 클러스터 색상

**Zone & Trend 토글**:
- **Zone**: Target Zone 표시 (75-100 사분면)
- **Trend**: 회귀선 표시

##### 인터랙티브 사이드 패널

**트리거**: 차트 포인트 클릭

**조건부 렌더링**:
```typescript
{selectedPoint && (
  <div className="lg:w-1/3 animate-in slide-in-from-right-4">
    {/* Side Panel Content */}
  </div>
)}
```

**내용**:
- 헤더: 아바타 + 이름 + 대학 + 학년
- 합격 예측 확률: 프로그레스 바
- Target Zone 거리 (Gap) 분석
- 전략 가이드 텍스트
- "상세 프로필 및 리포트" 버튼 → StudentDetail 이동

---

### 화면 3: StudentDetail (`/students/:id`)

**파일**: `pages/StudentDetail.tsx`  
**라인 수**: 549줄  
**상태**: ✅ 구현 완료

#### 3.1 레이아웃 구조

```
┌─────────────────────────────────────────────────────────┐
│ Sticky Header (Executive Summary)                       │
│ ┌──────┐ ┌──────────────────────┐ ┌──────────────┐    │
│ │ ←    │ │ Name + Badges         │ │ Level + Btn  │    │
│ │      │ │ Ga/Na/Da Lines        │ │              │    │
│ └──────┘ └──────────────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│ Main Content (3열 그리드)                               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│ │ 좌측     │ │ 중앙      │ │ 우측      │               │
│ │ (4 cols) │ │ (4 cols)  │ │ (4 cols)  │               │
│ │          │ │           │ │           │               │
│ │ - 입시   │ │ - 작품    │ │ - 강사    │               │
│ │   위치   │ │   갤러리  │ │   편향    │               │
│ │ - 유사   │ │ - 평가    │ │ - 리소스  │               │
│ │   사례   │ │   이력    │ │   플랜    │               │
│ │          │ │ - 학업    │ │ - 상담    │               │
│ │          │ │   점수    │ │   아젠다  │               │
│ └──────────┘ └──────────┘ └──────────┘               │
├─────────────────────────────────────────────────────────┤
│ Bottom Section (2열 그리드)                             │
│ ┌──────────────┐ ┌──────────────┐                      │
│ │ 평가 타임라인│ │ To-Do List   │                      │
│ │ (Line Chart) │ │              │                      │
│ └──────────────┘ └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

#### 3.2 상태 관리

```typescript
const { id } = useParams<{ id: string }>();
const [student, setStudent] = useState<Student | undefined>(undefined);
const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
const [currentImageIndex, setCurrentImageIndex] = useState(0);
const [todoList, setTodoList] = useState([
  { id: 1, text: '가/나/다군 지원 전략 상담 일정 잡기', done: false, due: '2일 남음' },
  { id: 2, text: '"아이디어 발상" 보충 워크샵 배정', done: true, due: '완료' },
  { id: 3, text: '6월 모의고사 이후 성적 추이 검토', done: false, due: '1주 남음' },
]);
```

#### 3.3 주요 섹션

##### Sticky Header

**구성**:
- 좌측: 뒤로 가기 버튼 + 학생 이름 + 학년 배지 + 상태 배지
- 중앙: 가/나/다군 목표 대학 라인
- 우측: 현재 레벨 표시 + "상담 시작" 버튼

**가/나/다군 데이터**:
```typescript
const recruitmentStrategy = [
  { group: '가군', univ: '서울대', line: '상향(Reach)', prob: 35, color: 'bg-rose-500' },
  { group: '나군', univ: '홍익대', line: '적정(Safe)', prob: 78, color: 'bg-[#FC6401]' },
  { group: '다군', univ: '이화여대', line: '소신(Top)', prob: 92, color: 'bg-emerald-500' },
];
```

##### 작품 갤러리 (Carousel)

**구현**:
```typescript
const hasImages = student.artworks && student.artworks.length > 0;
const nextImage = () => {
  if (hasImages) {
    setCurrentImageIndex((prev) => (prev + 1) % student.artworks.length);
  }
};
const prevImage = () => {
  if (hasImages) {
    setCurrentImageIndex((prev) => (prev - 1 + student.artworks.length) % student.artworks.length);
  }
};
```

**UI 요소**:
- 이미지 슬라이더
- 좌/우 네비게이션 화살표 (호버 시 표시)
- 인디케이터 도트
- 편집 버튼 (호버 시 표시) → EvaluationEntry 이동

##### 평가 이력 트렌드 차트

**차트 타입**: LineChart

**데이터 변환**:
```typescript
const chartData = [...evaluations].reverse().map(e => ({
  date: e.date.substring(5), // MM-DD
  score: e.totalScore,
  fullDate: e.date
}));
```

**차트 구성**:
- X축: 날짜 (MM-DD)
- Y축: 총점 (50-100)
- 기준선: 70점, 80점, 90점
- 최근 평가 하이라이트

##### 학업 점수 비교 테이블

**데이터 구조**:
```typescript
const academicTableData = [
  { subject: '국어', student: student.academicScores.korean.standardScore, avg: 138, type: 'score' },
  { subject: '영어', student: student.academicScores.english.grade, avg: 1, type: 'grade' },
  { subject: '수학', student: student.academicScores.math.standardScore, avg: 135, type: 'score' },
  { subject: '탐구1', student: student.academicScores.social1.standardScore, avg: 66, type: 'score' },
  { subject: '탐구2', student: student.academicScores.social2.standardScore, avg: 65, type: 'score' },
];
```

**갭 계산**:
```typescript
let gap = 0;
let displayGap = '';
let isPositive = false;

if (row.type === 'grade') {
  // Lower grade is better
  gap = (row.avg || 0) - (row.student || 0);
  isPositive = gap >= 0;
  displayGap = gap === 0 ? '-' : `${gap > 0 ? '-' : '+'}${Math.abs(gap)}`;
} else {
  // Higher score is better
  gap = (row.student || 0) - (row.avg || 0);
  isPositive = gap >= 0;
  displayGap = gap === 0 ? '-' : `${gap > 0 ? '+' : ''}${gap}`;
}
```

**갭 표시**:
- 양수: 초록색 (`text-emerald-600`)
- 음수: 빨간색 (`text-rose-500`)

##### 강사 편향 보정

**데이터**:
```typescript
const instructorBias = {
  name: '한 강사',
  biasScore: -2.5,
  note: '한 강사는 "톤(Tone)"을 엄격하게 평가하는 경향이 있음; 보정된 점수는 약 86.5점 예상.'
};
```

**시각화**:
- Dot Plot (원점수 vs 보정값)
- 연결선 (점선)
- 설명 텍스트

---

### 화면 4: EvaluationEntry (`/evaluations/new`)

**파일**: `pages/EvaluationEntry.tsx`  
**라인 수**: 438줄  
**상태**: ✅ 구현 완료

#### 4.1 레이아웃 구조

```
┌─────────────────────────────────────────────────────────┐
│ Page Header                                              │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Title + Subtitle                                 │   │
│ └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│ Main Content (3열 그리드)                               │
│ ┌──────────────────┐ ┌──────────┐                      │
│ │ 좌측 (2 cols)    │ │ 우측     │                      │
│ │                  │ │ (1 col)  │                      │
│ │ - 학생 선택      │ │          │                      │
│ │ - 4축 점수 입력  │ │ - 프리뷰 │                      │
│ │ - 강사 노트      │ │ - AI     │                      │
│ │ - Thinking 토글  │ │   버튼   │                      │
│ └──────────────────┘ └──────────┘                      │
└─────────────────────────────────────────────────────────┘
```

#### 4.2 상태 관리

```typescript
const [selectedStudentId, setSelectedStudentId] = useState('');
const [scores, setScores] = useState({ 
  composition: 5, 
  tone: 5, 
  idea: 5, 
  completeness: 5 
});
const [notes, setNotes] = useState('');
const [useThinking, setUseThinking] = useState(false);
const [isModalOpen, setIsModalOpen] = useState(false);
const [isGenerating, setIsGenerating] = useState(false);
const [generatedFeedback, setGeneratedFeedback] = useState<any>(null);
const [thinkingStep, setThinkingStep] = useState(0);
```

#### 4.3 주요 기능

##### 학생 선택

**구현**:
```typescript
const [allStudents, setAllStudents] = useState<Student[]>([]);

useEffect(() => {
  setAllStudents(getStudents());
}, []);

// URL 파라미터에서 학생 ID 가져오기
useEffect(() => {
  const sid = searchParams.get('studentId');
  if (sid) setSelectedStudentId(sid);
}, [searchParams]);
```

**UI**:
- 드롭다운 선택
- 선택 시 아바타 + 정보 카드 표시

##### 4축 평가 점수 입력

**Range Slider**:
- 구도 (Composition): 0-10 (0.5 step)
- 소묘/톤 (Tone): 0-10 (0.5 step)
- 발상 (Idea): 0-10 (0.5 step)
- 완성도 (Completeness): 0-10 (0.5 step)

**핸들러**:
```typescript
const handleScoreChange = (key: string, value: number) => {
  setScores(prev => ({ ...prev, [key]: value }));
};
```

##### Thinking Mode 토글

**구현**:
```typescript
const [useThinking, setUseThinking] = useState(false);

// Thinking 애니메이션 메시지
const thinkingMessages = [
  "구도 밸런스 분석 중...",
  "학업 성취도 데이터 조회 중...",
  "과거 합격생 포트폴리오 비교 중...",
  "시각적 패턴 매칭 중...",
  "전략적 조언 합성 중..."
];

useEffect(() => {
  let interval: any;
  if (isGenerating && useThinking) {
    interval = setInterval(() => {
      setThinkingStep((prev) => (prev + 1) % thinkingMessages.length);
    }, 1500);
  }
  return () => clearInterval(interval);
}, [isGenerating, useThinking]);
```

**UI**:
- 체크박스 토글
- 설명 텍스트
- Brain 아이콘 (활성화 시 오렌지)

##### AI 피드백 생성

**핸들러**:
```typescript
const handleGenerateAI = async () => {
  if (!selectedStudent) return;
  
  setIsModalOpen(true);
  setIsGenerating(true);
  setGeneratedFeedback(null);
  setThinkingStep(0);

  if (useThinking) {
    await new Promise(resolve => setTimeout(resolve, 3000));
  }

  const feedback = await generateAIFeedback(
    selectedStudent, 
    scores, 
    notes, 
    useThinking
  );
  setGeneratedFeedback(feedback);
  setIsGenerating(false);
};
```

**피드백 구조**:
```typescript
{
  strengths: string,
  weaknesses: string,
  actionPlan: string,
  comparisonInsight: {
    similarities: string,
    differences: string,
    usp: string
  }
}
```

**모달 레이아웃**:
- 2컬럼 그리드
- 좌측: 텍스트 피드백 (강점/약점/액션 플랜)
- 우측: 비교 분석 (유사점/차이점/USP)
- 하단: 클립보드 복사 + 저장 버튼

##### 평가 저장

**핸들러**:
```typescript
const handleSave = () => {
  if (!selectedStudent) return;

  const totalScore = scores.composition + scores.tone + scores.idea + scores.completeness;
  
  addEvaluation({
    studentId: selectedStudent.id,
    date: new Date().toISOString().split('T')[0],
    scores: scores,
    totalScore: totalScore * 2.5, // Scaling to 100
    notes: notes,
    instructorId: 'i1',
    aiFeedback: generatedFeedback ? {
      strengths: generatedFeedback.strengths,
      weaknesses: generatedFeedback.weaknesses,
      actionPlan: generatedFeedback.actionPlan
    } : undefined
  });

  alert('평가가 저장되었습니다!');
  setIsModalOpen(false);
  navigate(`/students/${selectedStudent.id}`);
};
```

---

### 화면 5: Analytics (`/analytics`)

**파일**: `pages/Analytics.tsx`  
**라인 수**: 635줄  
**상태**: ✅ 구현 완료

#### 5.1 UI 컨셉

**스타일**: VS Code 스타일 "Analysis Lab"

**레이아웃**: 3단 구조
1. 좌측 사이드바 (280px): 데이터 탐색기
2. 중앙 상단: 메트릭 스트립
3. 중앙 메인: 3-Tab 분석 뷰
4. 하단: AI 콘솔 (Resizable)

#### 5.2 상태 관리

```typescript
const [consoleHeight, setConsoleHeight] = useState(35);
const [isConsoleCollapsed, setIsConsoleCollapsed] = useState(false);
const [selectedFileId, setSelectedFileId] = useState<string>('cohort_hongik_all');
const [activeTab, setActiveTab] = useState<'explain' | 'compare' | 'simulate'>('explain');
const [treeData, setTreeData] = useState(DATA_TREE);
const [simValues, setSimValues] = useState({ practical: 50, sat: 50, competition: 50 });
const [input, setInput] = useState('');
const [isProcessing, setIsProcessing] = useState(false);
const [logs, setLogs] = useState<LogMessage[]>([...]);
```

#### 5.3 데이터 트리 구조

```typescript
const DATA_TREE: DataNode[] = [
  {
    id: 'root_2026',
    name: '2026 정시 시즌',
    type: 'folder',
    level: 0,
    isOpen: true,
    children: [
      {
        id: 'univ_hongik',
        name: '홍익대 (Hongik Univ)',
        type: 'folder',
        level: 1,
        isOpen: true,
        children: [
          { id: 'cohort_hongik_all', name: '전체 지원자 분석.dta', type: 'file', level: 2 },
          { id: 'cohort_hongik_high', name: '상위권(High) 그룹.dta', type: 'file', level: 2 },
        ]
      },
      {
        id: 'univ_snu',
        name: '서울대 (SNU)',
        type: 'folder',
        level: 1,
        isOpen: false,
        children: [
          { id: 'cohort_snu_craft', name: '공예과 지원자.dta', type: 'file', level: 2 }
        ]
      },
      { id: 'student_kim', name: '개인: 김지민.std', type: 'file', level: 1 }
    ]
  },
  {
    id: 'root_2025',
    name: '2025 합격 데이터 (Ref)',
    type: 'folder',
    level: 0,
    isOpen: false,
    children: []
  },
  {
    id: 'shared_drive',
    name: '공유 드라이브',
    type: 'folder',
    level: 0,
    isOpen: false,
    children: []
  }
];
```

#### 5.4 3-Tab 분석 뷰

##### Explain Tab

**차트 타입**: BarChart (Waterfall)

**데이터**:
```typescript
const WATERFALL_DATA = [
  { name: '기본 점수', value: 80, fill: '#E5E7EB' },
  { name: '수능', value: 12, fill: '#10B981' },
  { name: '내신', value: 3, fill: '#10B981' },
  { name: '실기(구도)', value: 5, fill: '#3B82F6' },
  { name: '실기(완성도)', value: -4, fill: '#F43F5E' },
  { name: '최종 예측', value: 96, isTotal: true, fill: '#FF5F00' },
];
```

**인사이트 오버레이**:
- 리스크 감지 배지
- 설명 텍스트

##### Compare Tab

**차트 타입**: RadarChart

**데이터**:
```typescript
const RADAR_DATA = [
  { subject: '구도', A: 92, B: 85, full: 100 },
  { subject: '톤/명암', A: 88, B: 90, full: 100 },
  { subject: '발상', A: 75, B: 88, full: 100 },
  { subject: '완성도', A: 95, B: 80, full: 100 },
  { subject: '학업', A: 85, B: 82, full: 100 },
];
```

**Gap Analysis**:
- 각 항목별 갭 표시
- 양수/음수 색상 구분

##### Simulate Tab

**슬라이더**:
- 실기 점수 향상 (0-100%)
- 수능 등급 컷 (0-100%)
- 경쟁률 변동 (0-100%)

**차트 타입**: PieChart (Gauge 스타일)

**예측 확률 계산**:
```typescript
const predictedProb = Math.min(
  99, 
  Math.floor(simValues.practical * 0.6 + 30)
);
```

#### 5.5 AI 콘솔

**로그 타입**:
- System: 시스템 메시지 (회색)
- User: 사용자 명령어 (검정)
- AI: AI 응답 (회색)

**명령어 처리**:
```typescript
const handleCommand = (e?: React.FormEvent) => {
  e?.preventDefault();
  if (!input.trim()) return;
  const cmd = input.trim();
  setInput('');
  addLog('user', cmd);
  setIsProcessing(true);

  setTimeout(() => {
    setIsProcessing(false);
    if (cmd.includes('비교') || cmd.includes('compare')) {
      setActiveTab('compare');
      addLog('system', 'Switched to [Compare] mode.');
      addLog('ai', '경쟁 그룹 데이터를 오버레이했습니다...');
    } else if (cmd.includes('시뮬') || cmd.includes('simulate')) {
      setActiveTab('simulate');
      addLog('system', 'Switched to [Simulate] mode.');
      addLog('ai', '전략 시뮬레이터를 실행합니다...');
    } else {
      addLog('ai', '요청하신 내용을 분석 중입니다...');
    }
  }, 1000);
};
```

**Resize 기능**:
- 기본 높이: 35%
- 최소 높이: 60px
- 최대 높이: 60%
- 드래그 핸들

---

### 화면 6: AdmissionSimulator (`/simulation`)

**파일**: `pages/AdmissionSimulator.tsx`  
**라인 수**: 514줄  
**상태**: ✅ 구현 완료

#### 6.1 레이아웃 구조

```
┌─────────────────────────────────────────────────────────┐
│ Header                                                  │
│ ┌──────────────────────┐ ┌──────────────────────────┐ │
│ │ Title + Beta Badge   │ │ Scenario Presets         │ │
│ └──────────────────────┘ └──────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Main Content (3/9 Split)                               │
│ ┌──────────────┐ ┌──────────────────────────────────┐ │
│ │ 좌측 (3 cols)│ │ 우측 (9 cols)                     │ │
│ │              │ │                                  │ │
│ │ - 학생 선택  │ │ - Top Cards (대학별 확률)        │ │
│ │ - 목표 대학  │ │ - Radar Chart                    │ │
│ │ - 점수 슬라이│ │ - Bar Chart                      │ │
│ │   더         │ │ - Meta-Insight                   │ │
│ └──────────────┘ └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 6.2 상태 관리

```typescript
const [selectedTargets, setSelectedTargets] = useState<TargetUniv[]>([DEFAULT_UNIVS[0]]);
const [baseScores, setBaseScores] = useState<SimulationState>({...});
const [simScores, setSimScores] = useState<SimulationState>({...});
const [activeScenario, setActiveScenario] = useState<'current' | 'realistic' | 'aggressive'>('current');
```

#### 6.3 목표 대학 데이터

```typescript
const DEFAULT_UNIVS: TargetUniv[] = [
  {
    id: 'hongik',
    name: '홍익대',
    major: '시각디자인',
    group: '나군',
    weights: { kor: 1.0, math: 0.8, eng: 0.5, social: 1.0, prac: 0 },
    cutline: 135
  },
  {
    id: 'snu',
    name: '서울대',
    major: '공예',
    group: '가군',
    weights: { kor: 1.0, math: 1.0, eng: 0.5, social: 1.0, prac: 1.5 },
    cutline: 420
  },
  {
    id: 'ewha',
    name: '이화여대',
    major: '디자인',
    group: '다군',
    weights: { kor: 1.0, math: 0.5, eng: 0.5, social: 1.0, prac: 1.2 },
    cutline: 380
  },
  {
    id: 'kookmin',
    name: '국민대',
    major: '시각디자인',
    group: '가군',
    weights: { kor: 1.0, math: 0.3, eng: 0.5, social: 1.0, prac: 1.0 },
    cutline: 350
  }
];
```

#### 6.4 합격 확률 계산 엔진

```typescript
const calculateProbability = (
  scores: SimulationState,
  target: TargetUniv
): number => {
  // 환산점수 계산
  const convertedScore = 
    (scores.korean * target.weights.kor) +
    (scores.math * target.weights.math) +
    (scores.english * 10 * target.weights.eng) + // Grade to score
    ((scores.social1 + scores.social2) / 2 * target.weights.social) +
    (scores.practical * target.weights.prac);
  
  // 최대 점수 계산
  const maxScore = 
    (150 * target.weights.kor) +
    (150 * target.weights.math) +
    (10 * target.weights.eng) +
    (80 * target.weights.social) +
    (100 * target.weights.prac);
  
  // 확률 계산
  const ratio = convertedScore / maxScore;
  const probability = Math.min(95, Math.max(5, ratio * 100));
  
  return Math.round(probability);
};
```

#### 6.5 시나리오 프리셋

**Current**:
- 현재 점수 그대로

**Realistic**:
- 실기 +5점
- 수학 +3점

**Aggressive**:
- 실기 +10점
- 수학 +8점
- 탐구 +5점

#### 6.6 차트

##### Radar Chart

**데이터**:
- 국어/수학/탐구/실기 4축
- 현재 점수 vs 시뮬레이션 점수 오버레이

##### Bar Chart

**데이터**:
- 대학별 확률 변화
- 현재 vs 시뮬레이션 비교
- 변화량 시각화

---

### 화면 7: StudentAdd (`/students/new`)

**파일**: `pages/StudentAdd.tsx`  
**라인 수**: 472줄  
**상태**: ✅ 구현 완료

#### 7.1 폼 구조

**섹션**:
1. 기본 정보
2. 입시 전략
3. 학업 프로필
4. 실기 프로필
5. 보호자 정보
6. 계정 설정

#### 7.2 상태 관리

```typescript
const [activeSection, setActiveSection] = useState('basic');
const [formData, setFormData] = useState({
  // 기본 정보
  name: '',
  englishName: '',
  birthDate: '',
  grade: '3학년',
  school: '',
  majorTrack: '시각디자인',
  contact: '',
  email: '',
  
  // 입시 전략
  targetGa: { univ: '', major: '' },
  targetNa: { univ: '', major: '' },
  targetDa: { univ: '', major: '' },
  strategyTags: ['나군 메인'],
  strategyNote: '',
  
  // 학업 프로필
  gpa: '',
  scores: {
    korean: { score: '', grade: '' },
    math: { score: '', grade: '' },
    english: { grade: '' },
    social1: { subject: '', score: '' },
    social2: { subject: '', score: '' },
  },
  
  // 실기 프로필
  practicalLevel: 'B+',
  mainInstructor: '',
  initialEval: {
    composition: 5,
    tone: 5,
    idea: 5,
    completeness: 5
  },
  
  // 보호자 정보
  guardianName: '',
  guardianRelation: '모',
  guardianContact: '',
  contactChannel: { call: true, sms: true, kakao: false, email: false },
  
  // 계정 설정
  accountType: 'invite'
});
```

---

### 화면 8-11: Login, Signup, Settings, Profile

#### Login (`/auth/login`)

**파일**: `pages/Login.tsx`  
**라인 수**: 90줄  
**상태**: ✅ 구현 완료

**폼 필드**:
- 이메일
- 비밀번호
- 로그인 유지 체크박스
- 비밀번호 찾기 링크

**인증 로직**:
```typescript
const handleLogin = (e: React.FormEvent) => {
  e.preventDefault();
  // Mock Auth Logic
  navigate('/');
};
```

#### Signup (`/auth/signup`)

**파일**: `pages/Signup.tsx`  
**라인 수**: 68줄  
**상태**: ✅ 구현 완료

**폼 필드**:
- 이름
- 학원명
- 이메일
- 비밀번호

**처리 로직**:
```typescript
const handleSignup = (e: React.FormEvent) => {
  e.preventDefault();
  alert("가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다.");
  navigate('/auth/login');
};
```

#### Settings (`/settings`)

**파일**: `pages/Settings.tsx`  
**라인 수**: 146줄  
**상태**: ✅ 구현 완료

**탭 구조**:
- 내 계정
- 학원 정보 (준비 중)
- 강사 관리 (준비 중)
- 데이터 관리

**내 계정 설정**:
- 프로필 사진 변경
- 이름, 직책, 이메일 수정
- 알림 설정 (체크박스)

#### Profile (`/profile`)

**파일**: `pages/Profile.tsx`  
**라인 수**: 101줄  
**상태**: ✅ 구현 완료

**구성**:
- 프로필 헤더 (배경 그라데이션)
- 프로필 사진 및 편집 버튼
- 사용자 정보 표시
- 최근 활동 로그
- 구독 정보

---

## 🧩 공통 컴포넌트 명세

### 컴포넌트 1: Layout

**파일**: `components/Layout.tsx`  
**라인 수**: 24줄

**구조**:
```typescript
<div className="h-screen w-screen bg-[#F9FAFB] flex">
  <Sidebar />
  <div className="flex-1 flex flex-col min-w-0 pl-[280px]">
    <Header />
    <main className="flex-1 pt-[60px] h-full relative overflow-hidden">
      <Outlet />
    </main>
  </div>
  <ChatBot />
</div>
```

**특징**:
- 사이드바 고정 너비: 280px
- 헤더 고정 높이: 60px
- ChatBot 플로팅 버튼 포함

### 컴포넌트 2: Sidebar

**파일**: `components/Sidebar.tsx`  
**라인 수**: 73줄

**네비게이션 메뉴**:
```typescript
const navItems = [
  { to: '/', icon: LayoutDashboard, label: '대시보드' },
  { to: '/students', icon: Users, label: '학생 관리' },
  { to: '/simulation', icon: Calculator, label: '합격 시뮬레이터' },
  { to: '/evaluations/new', icon: FileEdit, label: '평가 입력' },
  { to: '/analytics', icon: BarChart2, label: '데이터 분석' },
];
```

**활성 라우트 스타일**:
- 배경: `bg-[#FC6401]`
- 텍스트: `text-white`
- 그림자: `shadow-md shadow-[#FC6401]/25`

**하단 섹션**:
- 사용자 프로필
- 설정 링크
- 로그아웃 링크

### 컴포넌트 3: Header

**파일**: `components/Header.tsx`  
**라인 수**: 57줄

**구성**:
- Breadcrumbs (좌측)
- 글로벌 컨텍스트 선택기 (2026 시즌, 강남 본원)
- 검색 바 (전역 검색)
- 알림 아이콘 (프로필 페이지 링크)

**스타일**:
- 고정 헤더: `fixed top-0 left-[280px] right-0`
- 배경: `bg-white/80 backdrop-blur-md`
- 테두리: `border-b border-gray-200`

### 컴포넌트 4: ChatBot

**파일**: `components/ChatBot.tsx`  
**라인 수**: 158줄

**위치**: 우하단 플로팅

**상태 관리**:
```typescript
const [isOpen, setIsOpen] = useState(false);
const [messages, setMessages] = useState<Message[]>([...]);
const [input, setInput] = useState('');
const [isTyping, setIsTyping] = useState(false);
const [chatSession, setChatSession] = useState<any>(null);
```

**Gemini 통합**:
```typescript
useEffect(() => {
  if (isOpen && !chatSession) {
    setChatSession(createChatSession());
  }
}, [isOpen]);

const handleSend = async (e?: React.FormEvent) => {
  const result = await chatSession.sendMessageStream({ message: userMessage });
  
  let fullText = '';
  setMessages(prev => [...prev, { role: 'model', text: '' }]);
  
  for await (const chunk of result) {
    const c = chunk as GenerateContentResponse;
    if (c.text) {
      fullText += c.text;
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = { role: 'model', text: fullText };
        return newMessages;
      });
    }
  }
};
```

**UI 구조**:
- Floating Button (우하단)
- 채팅 창 (380-450px width, 600px height)
- Header (Dark, 모델명 표시)
- Messages Area (스크롤)
- Input Area (전송 버튼)

---

## 🔧 서비스 레이어 명세

### 서비스 1: geminiService

**파일**: `services/geminiService.ts`  
**라인 수**: 361줄

#### generateAIFeedback()

**시그니처**:
```typescript
export const generateAIFeedback = async (
  student: Student,
  scores: EvaluationScore,
  notes: string,
  useThinking: boolean = false
): Promise<FeedbackResponse>
```

**기능**:
- Gemini 3 Pro/Flash를 사용한 구조화된 피드백 생성
- Structured Output (JSON Schema) 지원
- Thinking 모드 지원 (`thinkingConfig`)
- Fallback Mock 응답

**응답 구조**:
```typescript
{
  strengths: string,
  weaknesses: string,
  actionPlan: string,
  comparisonInsight: {
    similarities: string,
    differences: string,
    usp: string
  }
}
```

#### createChatSession()

**시그니처**:
```typescript
export const createChatSession = () => ChatSession
```

**기능**:
- Gemini 3 Pro 챗 세션 생성
- System Instruction 설정
- 학원생 데이터 컨텍스트 주입
- 스트리밍 응답 지원

#### analyzeAcademyData()

**시그니처**:
```typescript
export const analyzeAcademyData = async (
  query: string,
  historyContext?: string
): Promise<AnalyzeAcademyDataResponse | null>
```

**분석 모드**:
- **explain**: 인과관계 분석
- **compare**: 세그먼트 비교
- **simulate**: 시나리오 예측

### 서비스 2: storageService

**파일**: `services/storageService.ts`  
**라인 수**: 67줄

#### 학생 CRUD

```typescript
export const getStudents = (): Student[]
export const getStudentById = (id: string): Student | undefined
export const addStudent = (student: Student): void
export const updateStudent = (updatedStudent: Student): void
```

#### 평가 CRUD

```typescript
export const getEvaluations = (): Evaluation[]
export const getEvaluationsByStudentId = (studentId: string): Evaluation[]
export const addEvaluation = (evaluation: Omit<Evaluation, 'id'>): void
```

**저장소**: LocalStorage

**키**:
- `neoprime_students`
- `neoprime_evaluations`

**초기화**: Mock 데이터로 자동 초기화

### 서비스 3: mockData

**파일**: `services/mockData.ts`  
**라인 수**: 426줄

**데이터**:
- `STUDENTS`: 20명의 학생 데이터
- `EVALUATIONS`: 평가 이력 데이터

**학생 데이터 구조**:
- 기본 정보 (이름, 학년, 학교, 목표 대학, 전공)
- 현재 레벨 (A+/A/B+/B/C)
- 아바타 URL (Dicebear API)
- 작품 이미지 URL (Unsplash)
- 학업 점수 (국어/영어/수학/탐구1/탐구2)
- 목표 대학 평균 점수
- 합격 이력
- 유사 합격 사례

---

## 🎨 디자인 시스템

### 색상 팔레트

```css
/* Primary */
--primary: #FC6401              /* NeoPrime Orange */
--primary-hover: #E55A00
--primary-light: #FFF0E6
--primary-border: rgba(252, 100, 1, 0.2)

/* Grayscale */
--gray-50: #F9FAFB
--gray-100: #F3F4F6
--gray-200: #E5E7EB
--gray-300: #D1D5DB
--gray-400: #9CA3AF
--gray-500: #6B7280
--gray-600: #4B5563
--gray-700: #374151
--gray-800: #1F2937
--gray-900: #111827

/* Semantic */
--success: #10B981           /* Emerald-500 */
--warning: #F59E0B           /* Amber-500 */
--error: #F43F5E             /* Rose-500 */
--info: #3B82F6              /* Blue-500 */
```

### 타이포그래피

```
text-xs: 12px
text-sm: 14px
text-base: 16px
text-lg: 18px
text-xl: 20px
text-2xl: 24px
text-3xl: 30px
text-4xl: 36px

font-medium: 500
font-semibold: 600
font-bold: 700
font-extrabold: 800
```

### 간격

```
space-1: 4px
space-2: 8px
space-3: 12px
space-4: 16px
space-5: 20px
space-6: 24px
space-8: 32px
```

### Border Radius

```
rounded-lg: 8px          # 버튼, 입력
rounded-xl: 12px         # 카드
rounded-2xl: 16px        # 메인 카드
rounded-3xl: 24px        # 대형 컨테이너
rounded-full: 50%        # 아바타, 배지
```

---

## 📱 반응형 디자인

### 브레이크포인트

```css
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### 주요 반응형 패턴

**Dashboard**:
- KPI Strip: 12 cols → 8/2/2 cols (lg)
- Strategy & Gaps: 12 cols → 8/4 cols (lg)

**StudentList**:
- 학생 카드 그리드: 3열 → 2열 (md) → 1열 (sm)

**StudentDetail**:
- Main Content: 3열 → 1열 (lg)

---

## 🔄 상태 관리 패턴

### 로컬 상태 (useState)

**사용 패턴**:
- 폼 입력값
- UI 상태 (모달 열림/닫힘, 탭 선택 등)
- 필터/검색어

### 계산된 값 (useMemo)

**사용 패턴**:
- 대학별 그룹화 데이터
- 필터링된 학생 목록
- 차트 데이터 변환

### 사이드 이펙트 (useEffect)

**사용 패턴**:
- 데이터 로드 (컴포넌트 마운트 시)
- URL 파라미터 파싱
- 자동 스크롤

### 라우팅 상태

**사용 패턴**:
- `useParams`: 동적 라우트 파라미터
- `useSearchParams`: 쿼리 파라미터
- `useNavigate`: 프로그래밍 방식 네비게이션

---

## 🚀 성능 최적화

### 코드 스플리팅

**현재 상태**: 미구현 (단일 번들)

**권장 사항**:
- 페이지별 코드 스플리팅
- 차트 라이브러리 지연 로딩

### 메모이제이션

**구현됨**:
- `useMemo`를 사용한 계산된 값 캐싱
- 차트 데이터 변환 최적화

### 이미지 최적화

**현재 상태**:
- 외부 이미지 사용 (Unsplash, Dicebear)
- 최적화 미적용

**권장 사항**:
- 이미지 CDN 사용
- WebP 포맷 지원
- Lazy Loading

---

## 🔐 보안 고려사항

### 현재 상태

**인증**:
- Mock 인증 로직만 구현
- 실제 백엔드 연동 미구현

**데이터 보호**:
- LocalStorage 사용 (민감 정보 저장 위험)
- API 키 환경 변수 처리 필요

### 권장 사항

1. **환경 변수**:
   - `.env.local` 파일 사용
   - `VITE_GEMINI_API_KEY` 설정

2. **인증**:
   - JWT 토큰 기반 인증
   - 토큰 갱신 로직

3. **데이터 검증**:
   - 입력값 검증 (Zod/Yup)
   - XSS 방지

---

## 📝 향후 개선 사항

### Priority 0 (즉시)

1. **백엔드 API 연동**
   - FastAPI/Django 백엔드 구축
   - RESTful API 엔드포인트 정의

2. **인증 시스템**
   - JWT 기반 인증
   - 권한 관리 (원장/강사)

3. **환경 변수 설정**
   - `.env.local` 파일 생성
   - API 키 관리

### Priority 1 (단기)

4. **에러 처리**
   - 전역 에러 바운더리
   - 사용자 친화적 에러 메시지

5. **로딩 상태**
   - 스켈레톤 UI
   - 로딩 인디케이터

6. **폼 검증**
   - 입력값 검증
   - 에러 메시지 표시

### Priority 2 (중기)

7. **테스트**
   - Unit 테스트 (Vitest)
   - E2E 테스트 (Playwright)

8. **문서화**
   - 컴포넌트 Props 문서화
   - API 엔드포인트 명세서

9. **접근성**
   - ARIA 레이블
   - 키보드 네비게이션

---

## 📚 참고 문서

### 관련 문서

1. `Frontend_IA_실제구현_v2.md` - 실제 구현 기준 IA 문서
2. `Frontend_구현현황_v1.md` - 구현 현황 보고서
3. `Frontend_코드베이스_분석보고서_v1.md` - 코드베이스 분석 보고서
4. `NeoPrime_기능명세서_v1.md` - 기능 명세서 (기존)

### 외부 리소스

- [React 19 문서](https://react.dev)
- [React Router v7 문서](https://reactrouter.com)
- [Recharts 문서](https://recharts.org)
- [Gemini API 문서](https://ai.google.dev)

---

## 📄 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|:----:|:----:|:------:|:---------|
| 1.0 | 2026-01-21 | AI Assistant | 초안 작성 - 실제 구현 기준 FRD |

---

**작성자**: AI Assistant (Claude)  
**검증 상태**: ✅ 코드베이스 검증 완료  
**기준**: 실제 구현 코드 분석 (2026-01-21)
