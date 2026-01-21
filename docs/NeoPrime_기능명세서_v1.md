# NeoPrime 기능 명세서 (Functional Requirements Specification)

**Version**: 1.0  
**Date**: 2026-01-21  
**Author**: Product Spec Agent  
**Status**: Draft  
**Document ID**: FRS-NEOPRIME-001

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|:----:|:----:|:------:|:---------|
| 1.0 | 2026-01-21 | Product Spec Agent | 초안 작성 - 전체 기능 명세 |

---

## 목차

1. [문서 개요](#1-문서-개요)
2. [섹션 1: 기능 명세 – 웹 대시보드](#섹션-1-기능-명세--웹-대시보드)
3. [섹션 2: 기능 명세 – 모바일 앱](#섹션-2-기능-명세--모바일-앱)
4. [섹션 3: 기능 명세 – Ask NeoPrime (Analytics) 상세](#섹션-3-기능-명세--ask-neoprime-analytics-상세)
5. [섹션 4: 비기능 명세 – 공통](#섹션-4-비기능-명세--공통)
6. [섹션 5: 릴리즈 단계별 우선순위 태깅](#섹션-5-릴리즈-단계별-우선순위-태깅)

---

## 1. 문서 개요

### 1.1 목적

본 문서는 NeoPrime 플랫폼의 기능 요구사항(Functional Requirements)과 비기능 요구사항(Non-Functional Requirements)을 정의합니다. 개발팀이 바로 티켓으로 분해하여 구현할 수 있도록 계량 가능한 수용 기준(Acceptance Criteria)을 포함합니다.

### 1.2 범위

| 플랫폼 | 대상 사용자 | 플랜 구분 |
|:------:|:-----------|:----------|
| **웹 대시보드** | 원장, 강사 | Elite / Standard |
| **모바일 앱** | 학생, 학부모 | B2B2C |

### 1.3 핵심 도메인 개념

| 개념 | 설명 |
|:-----|:-----|
| **Theory Engine v3** | 합격 예측 엔진 (RAWSCORE → INDEX → PERCENTAGE → RESTRICT → COMPUTE 5단계 파이프라인) |
| **Meta-AI** | 학원별 비밀 인텔리전스 - tenant별 파라미터/헤드 커스터마이징 |
| **Ask NeoPrime** | Gemini 3.0 Pro 기반 자연어 분석 콘솔 (`analyzeAcademyData` 인터페이스) |
| **Elite Partner** | 학원별 독립 모델 + 전체 기능 사용 가능 |
| **Standard Plan** | 공통 엔진만 사용 + 일부 기능 제한 |

### 1.4 용어 정의

```typescript
// 플랜 타입
type PlanType = 'elite' | 'standard' | 'public';

// 사용자 역할
type UserRole = 'director' | 'teacher' | 'student' | 'parent';

// 라인 분류
type AdmissionLine = 'TOP' | 'HIGH' | 'MID' | 'LOW' | 'DISQUALIFIED';

// 4축 평가
interface FourAxisScore {
  composition: number;  // 구도 (0-10)
  tone: number;         // 톤/명암 (0-10)
  concept: number;      // 발상/컨셉 (0-10)
  completion: number;   // 완성도/태도 (0-10)
}
```

---

# 섹션 1: 기능 명세 – 웹 대시보드

## TAB-W01: 대시보드 홈

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W01` |
| **URL** | `/` |
| **접근 권한** | 원장, 강사 |
| **플랜 제한** | 없음 (Elite/Standard 공통) |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W01-01` | `DashboardSummaryCard` | 총 학생 수, 평균 레벨, 예상 합격 인원을 카드 형태로 표시 | P0 | 1 | All |
| `F-W01-02` | `LevelDistributionChart` | A+~F 레벨별 학생 분포 바 차트 | P0 | 1 | All |
| `F-W01-03` | `UniversityAdmissionForecast` | 대학별 예상 합격 인원 프로그레스 바 | P0 | 1 | All |
| `F-W01-04` | `QuickActionButtons` | 학생 추가, 평가 입력, 리포트 다운로드 바로가기 | P1 | 1 | All |
| `F-W01-05` | `WeeklyEvaluationStatus` | 이번 주 평가 완료/미완료 학생 수 표시 | P1 | 1 | All |
| `F-W01-06` | `RecentAlerts` | 최근 알림 목록 (최대 5개) | P2 | 2 | All |
| `F-W01-07` | `RiskStudentBadge` | LOW/RISK 라인 학생 수 경고 뱃지 | P1 | 1 | Elite |
| `F-W01-08` | `MetaAIInsightWidget` | Ask NeoPrime 인사이트 요약 위젯 (Elite 전용) | P1 | 2 | Elite |

### F-W01-01: `DashboardSummaryCard`

**설명**: 학원 전체 현황을 요약 카드 3개로 표시

**입력 데이터**:
```typescript
interface DashboardSummaryRequest {
  academyId: string;
  seasonId: string;  // 현재 시즌 (예: "2026-winter")
}
```

**출력 데이터**:
```typescript
interface DashboardSummaryResponse {
  totalStudents: number;
  averageLevel: string;  // "B+", "A-" 등
  expectedAdmissions: {
    total: number;
    byLine: Record<AdmissionLine, number>;
  };
  lastUpdated: ISO8601String;
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 페이지 로드 시 3개 카드가 동시에 렌더링되며, 로딩 상태(Skeleton)가 1초 이내 해제된다.
- [ ] AC2: 총 학생 수는 현재 시즌에 등록된 활성 학생만 카운트한다 (탈퇴/휴학 제외).
- [ ] AC3: 평균 레벨은 가장 최근 평가 기준으로 계산하며, 평가 미완료 학생은 "미정"으로 표시한다.
- [ ] AC4: 예상 합격 인원은 Theory Engine v3의 최신 예측 결과를 기반으로 하며, 24시간 캐시를 사용한다.
- [ ] AC5: 강사 계정은 담당 학생만 필터링하여 표시한다.

---

### F-W01-02: `LevelDistributionChart`

**설명**: 학원 전체 학생의 레벨 분포를 바 차트로 시각화

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 차트는 A+, A, A-, B+, B, B-, C+, C, C-, D, F 총 11개 레벨을 표시한다.
- [ ] AC2: 바 클릭 시 해당 레벨 학생 리스트 모달이 열린다.
- [ ] AC3: 툴팁에 학생 수와 비율(%)이 표시된다.
- [ ] AC4: 반응형으로 모바일 뷰에서는 수평 바 차트로 전환된다.

---

### F-W01-07: `RiskStudentBadge` (Elite 전용)

**설명**: LOW/RISK 라인 학생 경고 표시 (Elite 플랜에서만 활성화)

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: LOW 라인 학생이 5명 이상이면 빨간색 뱃지가 표시된다.
- [ ] AC2: Standard 플랜에서는 해당 위젯이 "Elite 플랜 전용" 메시지와 함께 비활성화된다.
- [ ] AC3: 뱃지 클릭 시 리스크 학생 상세 목록 페이지로 이동한다.
- [ ] AC4: Meta-AI가 제안하는 개선 방향이 툴팁에 표시된다 (Elite 전용).

---

## TAB-W02: 학생 리스트

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W02` |
| **URL** | `/students/list` |
| **접근 권한** | 원장 (전체), 강사 (담당만) |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W02-01` | `StudentListTable` | 학생 목록 테이블 (이름, 학년, 레벨, 담당강사) | P0 | 1 | All |
| `F-W02-02` | `GradeFilter` | 학년별 필터 (고1/고2/고3/재수) | P0 | 1 | All |
| `F-W02-03` | `TeacherFilter` | 담당 강사별 필터 | P1 | 1 | All |
| `F-W02-04` | `StudentSearch` | 이름/학교 검색 (debounce 300ms) | P0 | 1 | All |
| `F-W02-05` | `SortOptions` | 이름/최근평가일/성장률/합격확률 정렬 | P1 | 1 | All |
| `F-W02-06` | `StudentRowClick` | 행 클릭 시 학생 상세 페이지 이동 | P0 | 1 | All |
| `F-W02-07` | `AddStudentButton` | 학생 추가 버튼 → `/students/new` 이동 | P0 | 1 | All |
| `F-W02-08` | `Pagination` | 20명/50명/100명 단위 페이지네이션 | P1 | 1 | All |
| `F-W02-09` | `BulkExport` | 학생 목록 Excel/CSV 내보내기 | P2 | 2 | Elite |
| `F-W02-10` | `LineColorCoding` | 라인별 색상 코딩 (TOP=녹색, LOW=빨간색) | P1 | 1 | All |

### F-W02-01: `StudentListTable`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 테이블 컬럼은 [체크박스, 이름, 학년, 전공, 현재 레벨, 라인, 담당강사, 최근평가일, 액션]으로 구성된다.
- [ ] AC2: 초기 로딩 시 최대 20명을 표시하며, 스크롤/페이지네이션으로 추가 로드한다.
- [ ] AC3: 강사 계정 로그인 시 자동으로 `teacherId` 필터가 적용되어 담당 학생만 표시된다.
- [ ] AC4: 레벨 컬럼은 배지 형태로 표시하며, A 계열=파랑, B 계열=녹색, C 이하=주황색으로 구분한다.
- [ ] AC5: 빈 상태(학생 0명)일 경우 "등록된 학생이 없습니다. 학생을 추가해주세요." 메시지와 CTA 버튼을 표시한다.

---

## TAB-W03: 학생 상세

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W03` |
| **URL** | `/students/:studentId` |
| **접근 권한** | 원장, 강사 (담당 학생) |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W03-01` | `StudentProfileHeader` | 학생 기본 정보 헤더 (이름, 학교, 학년, 희망대학) | P0 | 1 | All |
| `F-W03-02` | `GrowthCurveChart` | 주차별 종합 점수 추이 라인 차트 | P0 | 1 | All |
| `F-W03-03` | `FourAxisRadarChart` | 4축 레이더 차트 (구도/톤/발상/완성도) | P1 | 1 | All |
| `F-W03-04` | `EvaluationTimeline` | 과거 평가 기록 타임라인 (최근 12주) | P0 | 1 | All |
| `F-W03-05` | `AdmissionPredictionPanel` | 대학별 합격 확률 및 라인 표시 | P0 | 1 | All |
| `F-W03-06` | `SimilarCasesSection` | 유사 프로필 학생 합격 결과 (최대 10명) | P1 | 2 | Elite |
| `F-W03-07` | `LatestFeedbackCard` | 최근 AI 피드백 3단 구조 표시 | P0 | 1 | All |
| `F-W03-08` | `QuickEvaluationButton` | "평가 입력" 버튼 → 해당 학생 선택된 평가 페이지 이동 | P0 | 1 | All |
| `F-W03-09` | `EditStudentButton` | 학생 정보 수정 버튼 | P1 | 1 | All |
| `F-W03-10` | `IndividualReportDownload` | 개별 학생 리포트 PDF 다운로드 | P2 | 2 | All |
| `F-W03-11` | `MetaAIStudentInsight` | Meta-AI 기반 학생 개인 인사이트 (Elite 전용) | P1 | 2 | Elite |

### F-W03-05: `AdmissionPredictionPanel`

**입력 인터페이스**:
```typescript
interface AdmissionPredictionRequest {
  studentId: string;
  targetUniversities: string[];  // ["홍대", "이대", "경희"]
  engineVersion: string;  // "v3.2.1"
}
```

**출력 인터페이스**:
```typescript
interface AdmissionPredictionResponse {
  studentId: string;
  predictions: Array<{
    university: string;
    major: string;
    admissionType: string;
    probability: number;  // 0.0 ~ 1.0
    line: AdmissionLine;
    confidence: number;  // 모델 신뢰도
    reasoning: string;  // "최근 3주 평균 A- 수준, 커트라인 대비 +5점"
    similarCaseCount: number;
    similarCaseSuccessRate: number;
  }>;
  computedAt: ISO8601String;
  engineVersion: string;
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 희망 대학 최대 5개까지 동시에 예측 결과를 표시한다.
- [ ] AC2: 각 대학별로 확률(%), 라인(뱃지), 신뢰도가 표시된다.
- [ ] AC3: 확률이 80% 이상이면 녹색, 50-79%이면 주황색, 50% 미만이면 빨간색으로 표시한다.
- [ ] AC4: 클릭 시 상세 예측 근거(reasoning)가 모달로 표시된다.
- [ ] AC5: Theory Engine 버전과 계산 시점이 하단에 표시된다.

---

## TAB-W04: 주간 평가 입력

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W04` |
| **URL** | `/evaluations/new` |
| **접근 권한** | 원장, 강사 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W04-01` | `StudentSelector` | 평가 대상 학생 드롭다운 (검색 가능) | P0 | 1 | All |
| `F-W04-02` | `CompositionScoreInput` | 구도 점수 입력 (0-10, 0.5 단위 슬라이더) | P0 | 1 | All |
| `F-W04-03` | `ToneScoreInput` | 톤/명암 점수 입력 | P0 | 1 | All |
| `F-W04-04` | `ConceptScoreInput` | 발상/컨셉 점수 입력 | P0 | 1 | All |
| `F-W04-05` | `CompletionScoreInput` | 완성도/태도 점수 입력 | P0 | 1 | All |
| `F-W04-06` | `WorkDescriptionTextarea` | 작품 상태 자유 텍스트 (최대 500자) | P0 | 1 | All |
| `F-W04-07` | `GenerateAIFeedbackButton` | AI 피드백 생성 버튼 | P0 | 1 | All |
| `F-W04-08` | `FeedbackPreviewPanel` | 생성된 피드백 미리보기 (3단 구조) | P0 | 1 | All |
| `F-W04-09` | `FeedbackEditMode` | 피드백 직접 수정 모드 | P1 | 1 | All |
| `F-W04-10` | `SaveEvaluationButton` | 평가 저장 버튼 | P0 | 1 | All |
| `F-W04-11` | `NextStudentButton` | 다음 학생 평가 버튼 (연속 평가 모드) | P1 | 1 | All |
| `F-W04-12` | `BulkEvaluationMode` | 일괄 평가 모드 (여러 학생 연속) | P2 | 2 | Elite |
| `F-W04-13` | `PreviousEvaluationReference` | 이전 평가 참조 패널 (최근 4주) | P1 | 1 | All |
| `F-W04-14` | `AutoSaveDraft` | 자동 임시 저장 (30초 간격) | P2 | 2 | All |

### F-W04-07: `GenerateAIFeedbackButton`

**API 인터페이스**:
```typescript
interface GenerateFeedbackRequest {
  studentId: string;
  academyId: string;
  weekNumber: number;
  scores: FourAxisScore;
  workDescription: string;
  styleGuideVersion: string;  // "v2.1"
  tenantConfig?: TenantAIConfig;  // Elite 전용 - 학원별 커스텀 파라미터
}

interface GenerateFeedbackResponse {
  feedbackId: string;
  feedback: {
    positive: string;      // 1. 잘된 점
    coreIssue: string;     // 2. 핵심 문제
    nextAction: string;    // 3. 다음 1주 액션
  };
  overallLevel: string;    // "A-", "B+" 등
  suggestedLevel: string;  // AI 추천 레벨
  generatedAt: ISO8601String;
  modelVersion: string;    // "gemini-3.0-pro"
  tokensUsed: number;
}

// Elite 전용 - 학원별 AI 설정
interface TenantAIConfig {
  styleEmphasis: 'strict' | 'balanced' | 'encouraging';
  feedbackLength: 'short' | 'medium' | 'long';
  customPromptSuffix?: string;
  directorVoiceWeights?: {
    vocabulary: number;  // 0-1
    structure: number;
    directness: number;
  };
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 버튼 클릭 후 로딩 스피너가 표시되며, 3초 이내에 피드백이 생성된다.
- [ ] AC2: 생성된 피드백은 반드시 3단 구조(잘된 점/핵심 문제/다음 액션)를 유지한다.
- [ ] AC3: Elite 플랜에서는 `TenantAIConfig`에 따라 학원 맞춤형 톤이 적용된다.
- [ ] AC4: Standard 플랜에서는 공통 스타일 가이드(v2.1)가 적용된다.
- [ ] AC5: 생성 실패 시 "다시 시도" 버튼과 함께 에러 메시지가 표시된다.
- [ ] AC6: 피드백 텍스트 길이는 200-800자 범위를 유지한다.

---

## TAB-W05: Ask NeoPrime (Analytics 통합 콘솔)

> **중요**: 기존의 분산된 Analytics 탭(`/analytics/admission`, `/analytics/growth`, `/analytics/teacher-bias`)을  
> 단일 AI 콘솔 "Ask NeoPrime"으로 통합합니다.

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W05` |
| **URL** | `/analytics` (단일 진입점) |
| **접근 권한** | 원장 (전체), 강사 (제한적) |
| **플랜 제한** | 핵심 기능 Elite 전용, 기본 조회는 Standard 허용 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W05-01` | `NaturalLanguageQueryInput` | 자연어 질의 입력창 | P0 | 2 | All |
| `F-W05-02` | `PresetQuestionChips` | 프리셋 질문 칩 (자주 묻는 질문) | P0 | 2 | All |
| `F-W05-03` | `InsightCardsPanel` | 인사이트 카드 4종 (리스크/기회/커리큘럼/세그먼트) | P0 | 2 | Elite |
| `F-W05-04` | `ExplainMode` | Explain 모드 - 특정 지표/학생 설명 | P0 | 2 | All |
| `F-W05-05` | `CompareMode` | Compare 모드 - 세그먼트/기간 비교 | P1 | 2 | Elite |
| `F-W05-06` | `SimulateMode` | Simulate 모드 - "만약 ~하면" 시뮬레이션 | P1 | 2 | Elite |
| `F-W05-07` | `DeepDiveFactorAnalysis` | 딥다이브: 요인 분석 | P1 | 2 | Elite |
| `F-W05-08` | `DeepDiveSegmentCompare` | 딥다이브: 세그먼트 비교 | P1 | 2 | Elite |
| `F-W05-09` | `DeepDiveSimulation` | 딥다이브: 시뮬레이션 결과 | P1 | 2 | Elite |
| `F-W05-10` | `ConversationHistory` | 대화 히스토리 (최근 20개) | P2 | 3 | All |
| `F-W05-11` | `ExportAnalysisReport` | 분석 결과 PDF/Excel 내보내기 | P2 | 3 | Elite |
| `F-W05-12` | `SaveQueryTemplate` | 자주 쓰는 질문 저장 | P2 | 3 | Elite |

**상세 명세는 [섹션 3](#섹션-3-기능-명세--ask-neoprime-analytics-상세)에서 별도 기술**

---

## TAB-W06: 설정

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-W06` |
| **URL** | `/settings/*` |
| **접근 권한** | 원장 (전체), 강사 (계정 설정만) |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W06-01` | `AccountSettings` | 계정 설정 (비밀번호, 이메일) | P0 | 1 | All |
| `F-W06-02` | `NotificationPreferences` | 알림 설정 (이메일, 푸시) | P1 | 1 | All |
| `F-W06-03` | `AcademyProfile` | 학원 기본 정보 관리 | P0 | 1 | All |
| `F-W06-04` | `TeacherManagement` | 강사 계정 관리 (CRUD) | P0 | 1 | All |
| `F-W06-05` | `DataExportRequest` | 데이터 내보내기 요청 | P2 | 2 | All |
| `F-W06-06` | `DataDeletionRequest` | 데이터 삭제 요청 (GDPR) | P1 | 2 | All |
| `F-W06-07` | `PlanManagement` | 플랜 관리 및 결제 정보 | P1 | 2 | All |
| `F-W06-08` | `MetaAIConfiguration` | Meta-AI 설정 (학원별 AI 파라미터) | P1 | 2 | Elite |
| `F-W06-09` | `StyleGuideCustomization` | 피드백 스타일 가이드 커스터마이징 | P2 | 3 | Elite |
| `F-W06-10` | `APIKeyManagement` | API 키 관리 (외부 연동용) | P2 | 3 | Elite |

### F-W06-08: `MetaAIConfiguration` (Elite 전용)

**설명**: 학원별 Meta-AI 파라미터 설정 - Elite 플랜의 핵심 차별점

**설정 인터페이스**:
```typescript
interface MetaAIConfigurationSettings {
  academyId: string;
  
  // 피드백 스타일
  feedbackStyle: {
    tone: 'strict' | 'balanced' | 'encouraging';
    verbosity: 'concise' | 'standard' | 'detailed';
    emphasisAreas: ('composition' | 'tone' | 'concept' | 'completion')[];
  };
  
  // 예측 모델 가중치
  predictionWeights: {
    recentEvaluationWeight: number;  // 0-1, 최근 평가 가중치
    growthMomentumWeight: number;    // 0-1, 성장 모멘텀 가중치
    historicalDataWeight: number;    // 0-1, 과거 데이터 가중치
  };
  
  // 커스텀 프롬프트
  customPromptPrefix?: string;
  customPromptSuffix?: string;
  
  // 대학별 커트라인 보정
  cutoffAdjustments?: Record<string, number>;  // {"홍대": +2, "이대": -1}
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 설정 변경 시 실시간 미리보기가 제공된다 (샘플 피드백 생성).
- [ ] AC2: 설정은 학원별로 완전히 격리되어 저장된다 (멀티테넌시).
- [ ] AC3: 설정 변경 히스토리가 기록되며, 이전 버전으로 롤백이 가능하다.
- [ ] AC4: Standard 플랜에서는 해당 메뉴가 "Elite 플랜 전용"으로 잠금 처리된다.

---

# 섹션 2: 기능 명세 – 모바일 앱

## TAB-M01: 홈

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-M01` |
| **URL** | `/` |
| **접근 권한** | 학생, 학부모 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase |
|:--------|:-------|:-----|:--------:|:-----:|
| `F-M01-01` | `GreetingHeader` | "안녕하세요, [이름]님!" 인사말 | P0 | 1 |
| `F-M01-02` | `WeeklyScoreCard` | 이번 주 평가 결과 카드 (레벨 + 변화) | P0 | 1 |
| `F-M01-03` | `GrowthIndicator` | 지난주 대비 성장 표시 (↑/↓/→) | P0 | 1 |
| `F-M01-04` | `AdmissionSummary` | 목표 대학 합격 확률 요약 (상위 3개) | P0 | 1 |
| `F-M01-05` | `NextWeekActionCard` | AI 추천 다음 주 액션 플랜 | P1 | 1 |
| `F-M01-06` | `NotificationBadge` | 새 알림 개수 뱃지 | P1 | 1 |
| `F-M01-07` | `DetailLink` | "자세히 보기" → 성과 페이지 이동 | P0 | 1 |
| `F-M01-08` | `PullToRefresh` | 당겨서 새로고침 | P2 | 2 |
| `F-M01-09` | `ParentChildToggle` | 학부모: 자녀 선택 토글 (다자녀 지원) | P1 | 2 |

### F-M01-02: `WeeklyScoreCard`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 이번 주 평가가 있으면 레벨(A-, B+ 등)이 크게 표시된다.
- [ ] AC2: 평가 미완료 시 "이번 주 평가를 기다리는 중" 메시지가 표시된다.
- [ ] AC3: 지난주 대비 변화가 색상으로 구분된다 (상승=녹색, 유지=회색, 하락=빨간색).
- [ ] AC4: 카드 탭 시 주간 리포트 상세 페이지로 이동한다.
- [ ] AC5: 학부모 계정은 자녀의 정보가 표시되며, 상단에 자녀 이름이 명시된다.

---

## TAB-M02: 주간 리포트

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-M02` |
| **URL** | `/performance/weekly` |
| **접근 권한** | 학생, 학부모 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase |
|:--------|:-------|:-----|:--------:|:-----:|
| `F-M02-01` | `WeeklyLevelDisplay` | 이번 주 종합 레벨 대형 표시 | P0 | 1 |
| `F-M02-02` | `FourAxisScoreDisplay` | 4축 점수 막대 그래프 | P0 | 1 |
| `F-M02-03` | `MiniGrowthChart` | 최근 4주 추이 미니 라인 차트 | P0 | 1 |
| `F-M02-04` | `FeedbackDetail` | 3단 구조 피드백 전체 표시 | P0 | 1 |
| `F-M02-05` | `WeekComparison` | 지난주 대비 변화 상세 | P1 | 1 |
| `F-M02-06` | `WeekSelector` | 과거 주차 선택 (최근 12주) | P1 | 1 |
| `F-M02-07` | `ShareReport` | 카카오톡/이미지 공유 | P2 | 2 |
| `F-M02-08` | `FeedbackReaction` | 피드백 도움됨/안됨 반응 버튼 | P2 | 2 |

### F-M02-04: `FeedbackDetail`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 피드백은 "잘된 점", "핵심 문제", "다음 1주 액션" 3개 섹션으로 구분된다.
- [ ] AC2: 각 섹션은 접기/펼치기가 가능하며, 기본적으로 모두 펼쳐진 상태이다.
- [ ] AC3: 텍스트는 가독성을 위해 최소 16pt 폰트를 사용한다.
- [ ] AC4: 강사가 직접 수정한 피드백인 경우 "강사 수정" 뱃지가 표시된다.
- [ ] AC5: AI 생성 피드백인 경우 "AI 생성" 뱃지와 함께 신뢰도 표시 (선택적).

---

## TAB-M03: 합격 확률

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-M03` |
| **URL** | `/admission/probability` |
| **접근 권한** | 학생, 학부모 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase |
|:--------|:-------|:-----|:--------:|:-----:|
| `F-M03-01` | `UniversityProbabilityBars` | 대학별 합격 확률 프로그레스 바 | P0 | 1 |
| `F-M03-02` | `LineBadges` | TOP/HIGH/MID/LOW 라인 뱃지 | P0 | 1 |
| `F-M03-03` | `ProbabilityChangeIndicator` | 지난주 대비 확률 변화 표시 | P1 | 1 |
| `F-M03-04` | `RiskAnalysisSection` | 합격률 낮은 대학 주의사항 | P1 | 1 |
| `F-M03-05` | `SimilarCasesLink` | 유사 사례 페이지 링크 | P0 | 1 |
| `F-M03-06` | `TargetUniversityEdit` | 목표 대학 추가/삭제 | P1 | 2 |
| `F-M03-07` | `CutoffComparison` | 합격선 대비 현재 위치 시각화 | P2 | 2 |
| `F-M03-08` | `SimplifiedExplanation` | 학생/학부모 이해용 간략 설명 | P0 | 1 |

### F-M03-01: `UniversityProbabilityBars`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 최대 5개 대학의 합격 확률이 수직 프로그레스 바로 표시된다.
- [ ] AC2: 확률 80% 이상은 녹색, 50-79%는 주황색, 50% 미만은 빨간색이다.
- [ ] AC3: 각 바 옆에 라인 뱃지(TOP/HIGH/MID/LOW)가 표시된다.
- [ ] AC4: 바 탭 시 해당 대학 상세 정보 바텀 시트가 열린다.
- [ ] AC5: 학부모 계정에서는 복잡한 숫자 대신 "안정권", "도전권", "어려움" 텍스트 병행 표시.

---

## TAB-M04: 유사 사례

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-M04` |
| **URL** | `/admission/similar-cases` |
| **접근 권한** | 학생, 학부모 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase |
|:--------|:-------|:-----|:--------:|:-----:|
| `F-M04-01` | `SimilarityExplanation` | "나와 비슷한 프로필 선배들" 설명 | P0 | 1 |
| `F-M04-02` | `SimilarCaseCards` | 유사 학생 카드 리스트 (익명화) | P0 | 1 |
| `F-M04-03` | `AggregatedStatistics` | "유사 50명 중 40명 합격" 통계 | P0 | 1 |
| `F-M04-04` | `SuccessPatternAnalysis` | 합격자 공통점 분석 | P1 | 2 |
| `F-M04-05` | `UniversityFilter` | 특정 대학 합격자 필터 | P1 | 2 |
| `F-M04-06` | `CaseDetailModal` | 개별 사례 상세 모달 | P2 | 2 |

### F-M04-02: `SimilarCaseCards`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 각 카드에는 익명화된 식별자 (예: "선배 A", "2025 합격생 #12")가 표시된다.
- [ ] AC2: 유사도 점수, 최종 레벨, 합격 대학, 전공이 표시된다.
- [ ] AC3: 개인정보(이름, 학교)는 절대 노출되지 않는다.
- [ ] AC4: 유사 사례는 최소 5명 이상일 때만 표시하며, 5명 미만이면 "데이터 부족" 메시지.
- [ ] AC5: 카드는 합격 여부에 따라 색상 구분 (합격=녹색 테두리, 불합격=회색).

---

## TAB-M05: 내 정보

| 항목 | 내용 |
|:-----|:-----|
| **탭 ID** | `TAB-M05` |
| **URL** | `/profile` |
| **접근 권한** | 학생, 학부모 |

### 기능 목록

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase |
|:--------|:-------|:-----|:--------:|:-----:|
| `F-M05-01` | `ProfileDisplay` | 프로필 사진, 이름 표시 | P0 | 1 |
| `F-M05-02` | `BasicInfoDisplay` | 학년, 전공, 학원 정보 표시 | P0 | 1 |
| `F-M05-03` | `TargetUniversitiesDisplay` | 목표 대학 리스트 표시 | P0 | 1 |
| `F-M05-04` | `EditProfileLink` | 프로필 수정 페이지 링크 | P1 | 1 |
| `F-M05-05` | `TargetUniversityEdit` | 목표 대학 변경 페이지 링크 | P1 | 1 |
| `F-M05-06` | `NotificationSettings` | 푸시 알림 ON/OFF 토글 | P1 | 1 |
| `F-M05-07` | `LogoutButton` | 로그아웃 버튼 | P0 | 1 |
| `F-M05-08` | `AppVersionInfo` | 앱 버전 정보 | P2 | 2 |
| `F-M05-09` | `PrivacyPolicyLink` | 개인정보 처리방침 링크 | P1 | 1 |
| `F-M05-10` | `CustomerSupportLink` | 고객센터/문의하기 링크 | P2 | 2 |
| `F-M05-11` | `DataDownloadRequest` | 내 데이터 다운로드 요청 | P2 | 2 |
| `F-M05-12` | `AccountDeletion` | 계정 삭제 요청 | P1 | 2 |

---

# 섹션 3: 기능 명세 – Ask NeoPrime (Analytics) 상세

## 3.1 개요

**Ask NeoPrime**은 기존의 분산된 분석 페이지들을 하나의 AI 콘솔로 통합한 것입니다.

### 화면 구조

```
┌─────────────────────────────────────────────────────────────┐
│  Ask NeoPrime                                    [Elite]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🔍 무엇이든 물어보세요...                      [검색]   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [📊 합격 예측 현황] [📈 성장 추이] [👨‍🏫 강사 편차] [⚠️ 리스크] │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  💡 Insight Cards                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 🚨 리스크 │ │ 🎯 기회  │ │ 📚 커리  │ │ 👥 세그  │       │
│  │ 학생 8명  │ │ TOP 후보 │ │ 큘럼 제안│ │ 먼트     │       │
│  │ 주의 필요 │ │ 12명    │ │ 명암집중 │ │ 분석    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  🔬 Deep Dive                                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [Explain] [Compare] [Simulate]                          ││
│  │                                                          ││
│  │ (선택된 모드에 따른 분석 결과 영역)                      ││
│  │                                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.2 핵심 API 인터페이스

### `analyzeAcademyData` API

```typescript
// Request
interface AnalyzeAcademyDataRequest {
  academyId: string;
  query: string;  // 자연어 질의
  mode: 'explain' | 'compare' | 'simulate';
  context?: {
    studentIds?: string[];
    universityFilter?: string[];
    dateRange?: { start: ISO8601String; end: ISO8601String };
    gradeFilter?: ('고1' | '고2' | '고3' | '재수')[];
  };
  simulationParams?: SimulationParams;  // Simulate 모드용
  tenantConfig?: TenantAIConfig;  // Elite 전용
}

// Response
interface AnalyzeAcademyDataResponse {
  queryId: string;
  mode: 'explain' | 'compare' | 'simulate';
  
  // 자연어 응답
  summary: string;  // "현재 학원의 홍대 합격 예상 인원은 65명입니다..."
  
  // 구조화된 데이터
  structuredData: ExplainResult | CompareResult | SimulateResult;
  
  // 인사이트 카드
  insightCards: InsightCard[];
  
  // 시각화 데이터
  visualizations: Visualization[];
  
  // 메타데이터
  metadata: {
    tokensUsed: number;
    latencyMs: number;
    engineVersion: string;
    confidence: number;  // 0-1
  };
}

// Simulation 파라미터
interface SimulationParams {
  type: 'whatIf' | 'projection' | 'comparison';
  variables: {
    name: string;
    currentValue: number | string;
    simulatedValue: number | string;
  }[];
  targetMetric: 'admissionProbability' | 'level' | 'ranking';
}
```

---

## 3.3 모드별 상세 기능

### 3.3.1 Explain 모드

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W05-E01` | `ExplainStudentPerformance` | 특정 학생 성과 설명 | P0 | 2 | All |
| `F-W05-E02` | `ExplainUniversityPrediction` | 대학별 합격 예측 근거 설명 | P0 | 2 | All |
| `F-W05-E03` | `ExplainLevelDistribution` | 학원 레벨 분포 분석 | P0 | 2 | All |
| `F-W05-E04` | `ExplainGrowthPattern` | 학생/학원 성장 패턴 분석 | P1 | 2 | All |
| `F-W05-E05` | `ExplainTeacherBias` | 강사 평가 편차 분석 | P1 | 2 | Elite |
| `F-W05-E06` | `ExplainRiskFactors` | 리스크 요인 분석 (LOW 라인 원인) | P1 | 2 | Elite |

#### F-W05-E01: `ExplainStudentPerformance`

**예시 질의**:
- "김OO 학생이 왜 B+ 레벨인지 설명해줘"
- "홍OO의 최근 성장이 정체된 이유가 뭐야?"

**입력**:
```typescript
interface ExplainStudentRequest {
  studentId: string;
  aspects?: ('level' | 'growth' | 'weakness' | 'strength')[];
}
```

**출력**:
```typescript
interface ExplainResult {
  type: 'explain';
  subject: {
    type: 'student' | 'university' | 'academy' | 'metric';
    id: string;
    name: string;
  };
  explanation: {
    summary: string;
    factors: Array<{
      factor: string;
      impact: 'positive' | 'negative' | 'neutral';
      weight: number;  // 0-1
      detail: string;
    }>;
    recommendations: string[];
  };
  supportingData: {
    currentMetrics: Record<string, number | string>;
    historicalTrend: Array<{ date: string; value: number }>;
    comparisons: Array<{ benchmark: string; value: number; difference: number }>;
  };
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 질의 입력 후 5초 이내에 분석 결과가 표시된다.
- [ ] AC2: 설명은 최소 3개 이상의 요인(factors)을 포함한다.
- [ ] AC3: 각 요인은 긍정/부정/중립으로 명확히 분류된다.
- [ ] AC4: 추천 사항은 구체적인 액션 아이템을 포함한다 (예: "명암 연습 주 3회 추가").
- [ ] AC5: Standard 플랜에서는 요인 분석이 상위 3개로 제한된다.

---

### 3.3.2 Compare 모드

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W05-C01` | `CompareStudentSegments` | 학생 세그먼트 간 비교 | P1 | 2 | Elite |
| `F-W05-C02` | `ComparePeriods` | 기간별 성과 비교 | P1 | 2 | All |
| `F-W05-C03` | `CompareTeachers` | 강사별 평가 비교 | P1 | 2 | Elite |
| `F-W05-C04` | `CompareUniversities` | 대학별 합격 현황 비교 | P1 | 2 | All |
| `F-W05-C05` | `CompareCohorts` | 연도별 코호트 비교 | P2 | 3 | Elite |

#### F-W05-C01: `CompareStudentSegments`

**예시 질의**:
- "고3과 재수생의 평균 레벨 차이를 비교해줘"
- "디자인 전공과 회화 전공 학생들의 합격률 비교"

**출력**:
```typescript
interface CompareResult {
  type: 'compare';
  comparisonType: 'segment' | 'period' | 'teacher' | 'university' | 'cohort';
  groups: Array<{
    name: string;
    size: number;
    metrics: Record<string, number>;
  }>;
  differences: Array<{
    metric: string;
    groupA: { name: string; value: number };
    groupB: { name: string; value: number };
    difference: number;
    percentageDiff: number;
    significance: 'high' | 'medium' | 'low';
  }>;
  insights: string[];
  visualization: {
    type: 'bar' | 'radar' | 'line';
    data: ChartData;
  };
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 최대 5개 그룹까지 동시 비교가 가능하다.
- [ ] AC2: 각 차이는 통계적 유의성(significance)이 표시된다.
- [ ] AC3: 비교 결과는 자동으로 적절한 시각화(바 차트/레이더 차트)로 표시된다.
- [ ] AC4: Standard 플랜에서는 기간 비교와 대학 비교만 가능하다.

---

### 3.3.3 Simulate 모드

| 기능 ID | 기능명 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:-------|:-----|:--------:|:-----:|:----:|
| `F-W05-S01` | `SimulateWhatIf` | "만약 ~하면" 가정 시뮬레이션 | P1 | 2 | Elite |
| `F-W05-S02` | `SimulateProjection` | 미래 예측 시뮬레이션 | P1 | 2 | Elite |
| `F-W05-S03` | `SimulateCutoffChange` | 커트라인 변화 시뮬레이션 | P2 | 3 | Elite |
| `F-W05-S04` | `SimulateBatchScenario` | 다중 학생 일괄 시뮬레이션 | P2 | 3 | Elite |

#### F-W05-S01: `SimulateWhatIf`

**예시 질의**:
- "김OO 학생이 앞으로 4주 동안 구도 점수를 2점 올리면 홍대 합격 확률이 얼마나 올라가?"
- "전체 학생의 명암 점수가 평균 1점 상승하면 TOP 라인 학생이 몇 명 늘어나?"

**입력**:
```typescript
interface SimulateWhatIfRequest {
  targetType: 'student' | 'segment' | 'academy';
  targetId: string;
  hypotheticalChanges: Array<{
    variable: string;  // "compositionScore", "attendanceRate", etc.
    changeType: 'absolute' | 'relative';
    changeValue: number;
  }>;
  targetMetric: string;  // "admissionProbability", "level", etc.
}
```

**출력**:
```typescript
interface SimulateResult {
  type: 'simulate';
  simulationType: 'whatIf' | 'projection' | 'cutoff' | 'batch';
  baseline: {
    metric: string;
    value: number;
    confidence: number;
  };
  simulated: {
    metric: string;
    value: number;
    confidence: number;
    changeFromBaseline: number;
    changePercentage: number;
  };
  breakdown: Array<{
    factor: string;
    contribution: number;
    explanation: string;
  }>;
  caveats: string[];  // 시뮬레이션 제한사항
  recommendations: string[];
}
```

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: 시뮬레이션 결과는 10초 이내에 계산된다.
- [ ] AC2: 결과에는 신뢰도(confidence)가 함께 표시된다.
- [ ] AC3: 비현실적인 변화(예: 점수 +10)에 대해 경고 메시지가 표시된다.
- [ ] AC4: Standard 플랜에서는 Simulate 모드가 "Elite 플랜 전용"으로 잠금 처리된다.
- [ ] AC5: 시뮬레이션 결과는 저장하여 나중에 참조할 수 있다.

---

## 3.4 Insight Cards

### 카드 타입 정의

```typescript
interface InsightCard {
  type: 'risk' | 'opportunity' | 'curriculum' | 'segment';
  title: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  severity?: 'critical' | 'warning' | 'info';
  actionUrl?: string;
  details: {
    description: string;
    affectedStudents?: number;
    recommendations?: string[];
  };
}
```

### 카드별 기능

| 기능 ID | 카드 타입 | 설명 | 우선순위 | Phase | 플랜 |
|:--------|:---------|:-----|:--------:|:-----:|:----:|
| `F-W05-IC01` | `RiskCard` | 리스크 학생 경고 카드 | P0 | 2 | Elite |
| `F-W05-IC02` | `OpportunityCard` | TOP 라인 진입 가능 학생 카드 | P0 | 2 | Elite |
| `F-W05-IC03` | `CurriculumCard` | 커리큘럼 제안 카드 | P1 | 2 | Elite |
| `F-W05-IC04` | `SegmentCard` | 세그먼트 인사이트 카드 | P1 | 2 | Elite |

#### F-W05-IC01: `RiskCard`

**수용 기준 (Acceptance Criteria)**:
- [ ] AC1: LOW/RISK 라인 학생이 1명 이상이면 카드가 활성화된다.
- [ ] AC2: 카드에는 리스크 학생 수, 주요 원인(예: "4축 중 구도 취약"), 권장 조치가 표시된다.
- [ ] AC3: 카드 클릭 시 리스크 학생 상세 리스트로 이동한다.
- [ ] AC4: 심각도(critical/warning)에 따라 카드 색상이 다르다 (빨강/주황).

---

## 3.5 프론트엔드 컴포넌트 계약

### 질의창 컴포넌트

```typescript
interface QueryInputProps {
  placeholder: string;
  presetQuestions: Array<{
    label: string;
    query: string;
    mode: 'explain' | 'compare' | 'simulate';
  }>;
  onSubmit: (query: string, mode: string) => void;
  isLoading: boolean;
  recentQueries?: string[];  // 최근 질의 자동완성
}
```

### 인사이트 카드 컴포넌트

```typescript
interface InsightCardProps {
  card: InsightCard;
  onClick: () => void;
  isExpanded: boolean;
  planType: PlanType;  // 플랜에 따른 잠금 처리
}
```

### 결과 패널 컴포넌트

```typescript
interface ResultPanelProps {
  result: AnalyzeAcademyDataResponse | null;
  isLoading: boolean;
  error: Error | null;
  onExport: (format: 'pdf' | 'excel') => void;
  onSave: () => void;
}
```

---

# 섹션 4: 비기능 명세 – 공통

## 4.1 성능 (Performance)

| NFR ID | 항목 | 요구사항 | 측정 방법 | 우선순위 | Phase |
|:-------|:-----|:---------|:---------|:--------:|:-----:|
| `NFR-P01` | API 응답 시간 | P95 ≤ 3초 (일반 API) | k6 부하 테스트 | P0 | 1 |
| `NFR-P02` | AI 피드백 생성 | P95 ≤ 5초 | LLM 호출 시간 측정 | P0 | 1 |
| `NFR-P03` | Ask NeoPrime 쿼리 | P95 ≤ 10초 | E2E 응답 시간 측정 | P0 | 2 |
| `NFR-P04` | 페이지 초기 로딩 | LCP ≤ 2.5초 | Lighthouse | P0 | 1 |
| `NFR-P05` | 인터랙션 응답 | FID ≤ 100ms | Core Web Vitals | P1 | 1 |
| `NFR-P06` | 레이아웃 안정성 | CLS ≤ 0.1 | Core Web Vitals | P1 | 1 |
| `NFR-P07` | 대시보드 데이터 갱신 | 캐시 TTL 5분 | 캐시 히트율 모니터링 | P1 | 1 |
| `NFR-P08` | 합격 예측 계산 | 배치 처리 ≤ 30분 (전체 학생) | 배치 작업 시간 | P1 | 2 |

### NFR-P01: API 응답 시간

**상세 요구사항**:
- 일반 CRUD API: P50 ≤ 500ms, P95 ≤ 3초, P99 ≤ 5초
- 목록 조회 (100건 이하): P50 ≤ 1초, P95 ≤ 3초
- 목록 조회 (100건 초과): 페이지네이션 필수, 단일 페이지 P95 ≤ 3초

**수용 기준**:
- [ ] AC1: 100 동시 사용자 부하에서 P95 ≤ 3초 충족
- [ ] AC2: 500 동시 사용자 부하에서 P95 ≤ 5초 충족
- [ ] AC3: 응답 시간 초과 시 타임아웃 에러와 함께 재시도 안내

---

## 4.2 확장성 (Scalability)

| NFR ID | 항목 | 요구사항 | 측정 방법 | 우선순위 | Phase |
|:-------|:-----|:---------|:---------|:--------:|:-----:|
| `NFR-S01` | 동시 사용자 | 500명 동시 접속 지원 | 부하 테스트 | P0 | 1 |
| `NFR-S02` | 데이터 볼륨 | 학원당 최대 1,000명 학생 | 성능 테스트 | P0 | 1 |
| `NFR-S03` | 테넌트 수 | 100개 학원 동시 운영 | 멀티테넌시 테스트 | P1 | 2 |
| `NFR-S04` | 평가 데이터 | 연간 100만 건 평가 데이터 처리 | BigQuery 성능 | P1 | 2 |
| `NFR-S05` | Auto Scaling | CPU 70% 시 자동 스케일아웃 | GKE 오토스케일링 | P1 | 2 |
| `NFR-S06` | 수평 확장 | Stateless 서비스 설계 | 아키텍처 검토 | P0 | 1 |

---

## 4.3 가용성/신뢰성 (Availability/Reliability)

| NFR ID | 항목 | 요구사항 | 측정 방법 | 우선순위 | Phase |
|:-------|:-----|:---------|:---------|:--------:|:-----:|
| `NFR-A01` | 서비스 가용성 | 99.5% uptime (월간) | 업타임 모니터링 | P0 | 1 |
| `NFR-A02` | 계획된 다운타임 | 월 2시간 이내 | 유지보수 일정 | P1 | 1 |
| `NFR-A03` | 장애 복구 시간 | RTO ≤ 1시간 | 장애 대응 훈련 | P0 | 2 |
| `NFR-A04` | 데이터 복구 시점 | RPO ≤ 1시간 | 백업 주기 검증 | P0 | 2 |
| `NFR-A05` | 에러율 | HTTP 5xx ≤ 0.1% | APM 모니터링 | P0 | 1 |
| `NFR-A06` | 데이터베이스 | 자동 페일오버 지원 | Cloud SQL HA | P0 | 2 |
| `NFR-A07` | 백업 | 일일 자동 백업, 30일 보관 | 백업 정책 | P0 | 1 |
| `NFR-A08` | 재해 복구 | 다중 리전 백업 | DR 테스트 | P2 | 3 |

---

## 4.4 보안/개인정보 보호 (Security & Privacy)

| NFR ID | 항목 | 요구사항 | 측정 방법 | 우선순위 | Phase |
|:-------|:-----|:---------|:---------|:--------:|:-----:|
| `NFR-SEC01` | 인증 | Firebase Auth + JWT (만료 1시간) | 보안 감사 | P0 | 1 |
| `NFR-SEC02` | 권한 관리 | RBAC (원장/강사/학생/학부모) | 접근 제어 테스트 | P0 | 1 |
| `NFR-SEC03` | 데이터 암호화 | 전송 중 TLS 1.3, 저장 시 AES-256 | 암호화 검증 | P0 | 1 |
| `NFR-SEC04` | 민감정보 해싱 | 학생 이름 SHA-256 해싱 | 데이터 마스킹 검증 | P0 | 1 |
| `NFR-SEC05` | API 보안 | Rate Limiting (100 req/min/user) | 부하 테스트 | P0 | 1 |
| `NFR-SEC06` | SQL Injection | 파라미터화 쿼리 필수 | 보안 스캔 (OWASP ZAP) | P0 | 1 |
| `NFR-SEC07` | XSS 방지 | 출력 이스케이핑 필수 | 보안 스캔 | P0 | 1 |
| `NFR-SEC08` | CSRF 방지 | CSRF 토큰 적용 | 보안 테스트 | P0 | 1 |
| `NFR-SEC09` | 개인정보 동의 | 가입 시 명시적 동의 수집 | UI 검증 | P0 | 1 |
| `NFR-SEC10` | 데이터 삭제권 | 요청 시 10일 이내 처리 | 프로세스 검증 | P0 | 2 |
| `NFR-SEC11` | 접근 로그 | 모든 API 호출 로깅, 90일 보관 | 로그 검토 | P0 | 1 |
| `NFR-SEC12` | 멀티테넌시 격리 | 테넌트 간 데이터 완전 격리 | 침투 테스트 | P0 | 1 |
| `NFR-SEC13` | 보안 감사 | 분기 1회 보안 감사 | 감사 보고서 | P1 | 2 |

### NFR-SEC04: 민감정보 해싱

**상세 요구사항**:
```typescript
// 해싱 대상 필드
interface SensitiveDataPolicy {
  studentName: 'hash';      // SHA-256
  schoolName: 'generalize'; // "강남구 소재 고등학교"로 일반화
  phoneNumber: 'mask';      // "010-****-1234"
  email: 'mask';            // "k***@example.com"
  address: 'exclude';       // 수집하지 않음
}

// 해싱 함수
function hashStudentName(name: string, salt: string): string {
  return crypto.createHash('sha256')
    .update(name + salt)
    .digest('hex')
    .substring(0, 16);  // 충돌 최소화
}
```

---

## 4.5 관측 가능성 (Logging, Monitoring, Tracing)

| NFR ID | 항목 | 요구사항 | 도구 | 우선순위 | Phase |
|:-------|:-----|:---------|:----|:--------:|:-----:|
| `NFR-O01` | 구조화 로깅 | JSON 포맷, 상관관계 ID 포함 | Cloud Logging | P0 | 1 |
| `NFR-O02` | 로그 보존 | 90일 보관 (hot), 1년 (cold) | Cloud Storage | P0 | 1 |
| `NFR-O03` | 메트릭 수집 | 시스템/애플리케이션/비즈니스 메트릭 | Cloud Monitoring | P0 | 1 |
| `NFR-O04` | 분산 트레이싱 | 요청 전체 흐름 추적 | Cloud Trace | P1 | 2 |
| `NFR-O05` | 알림 설정 | 임계치 초과 시 Slack/Email 알림 | Cloud Alerting | P0 | 1 |
| `NFR-O06` | 대시보드 | 핵심 지표 실시간 대시보드 | Grafana/Looker | P1 | 2 |
| `NFR-O07` | 에러 추적 | 에러 그룹화, 스택 트레이스 | Cloud Error Reporting | P0 | 1 |
| `NFR-O08` | APM | 애플리케이션 성능 모니터링 | Cloud Profiler | P2 | 2 |

### NFR-O01: 구조화 로깅

**로그 스키마**:
```typescript
interface LogEntry {
  timestamp: ISO8601String;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
  correlationId: string;    // 요청 추적 ID
  tenantId: string;         // 학원 ID
  userId?: string;          // 사용자 ID (선택)
  service: string;          // 서비스 이름
  action: string;           // 수행 동작
  duration?: number;        // 소요 시간 (ms)
  status: 'success' | 'failure';
  error?: {
    code: string;
    message: string;
    stack?: string;
  };
  metadata?: Record<string, unknown>;
}
```

---

## 4.6 AI 품질/설명 가능성 (Explainability, Evaluation)

| NFR ID | 항목 | 요구사항 | 측정 방법 | 우선순위 | Phase |
|:-------|:-----|:---------|:---------|:--------:|:-----:|
| `NFR-AI01` | 예측 정확도 | 합격 예측 정확도 ≥ 85% | 백테스트 (전년도 데이터) | P0 | 2 |
| `NFR-AI02` | 피드백 품질 | 원장 수정률 ≤ 30% | 수정 로그 분석 | P0 | 1 |
| `NFR-AI03` | 피드백 구조 | 3단 구조 유지율 100% | 자동 검증 | P0 | 1 |
| `NFR-AI04` | 설명 가능성 | 모든 예측에 근거 제시 | UI 검증 | P0 | 2 |
| `NFR-AI05` | 모델 버전 관리 | 버전별 A/B 테스트 지원 | MLflow | P1 | 2 |
| `NFR-AI06` | 편향 감지 | 학년/전공별 편향 모니터링 | 공정성 메트릭 | P2 | 3 |
| `NFR-AI07` | 피드백 루프 | 사용자 피드백 수집 → 모델 개선 | 피드백 수집 UI | P1 | 2 |
| `NFR-AI08` | Hallucination 방지 | 허위 정보 생성률 ≤ 1% | 출력 검증 | P0 | 1 |

### NFR-AI01: 예측 정확도

**측정 방법**:
```typescript
interface PredictionAccuracyMetrics {
  // 전체 정확도
  overallAccuracy: number;  // (TP + TN) / Total
  
  // 라인별 정확도
  lineAccuracy: {
    TOP: number;
    HIGH: number;
    MID: number;
    LOW: number;
  };
  
  // 혼동 행렬
  confusionMatrix: number[][];
  
  // 추가 메트릭
  precision: number;
  recall: number;
  f1Score: number;
  auc: number;
}

// 목표 수치
const targetMetrics: PredictionAccuracyMetrics = {
  overallAccuracy: 0.85,
  lineAccuracy: {
    TOP: 0.90,
    HIGH: 0.85,
    MID: 0.80,
    LOW: 0.85
  },
  precision: 0.85,
  recall: 0.85,
  f1Score: 0.85,
  auc: 0.90
};
```

---

# 섹션 5: 릴리즈 단계별 우선순위 태깅

## 5.1 Phase 1: MVP (Week 1-6)

### 목표
- 핵심 플로우 완성: 평가 입력 → AI 피드백 생성 → 학생 앱 확인
- 네오캣 파일럿 준비

### 포함 기능

| 플랫폼 | 탭 ID | 기능 ID | 기능명 | 우선순위 |
|:------:|:-----:|:--------|:-------|:--------:|
| Web | TAB-W01 | F-W01-01~03 | 대시보드 요약 카드 | P0 |
| Web | TAB-W02 | F-W02-01~02, 04, 06~07 | 학생 리스트 기본 | P0 |
| Web | TAB-W03 | F-W03-01~02, 04~05, 07~08 | 학생 상세 기본 | P0 |
| Web | TAB-W04 | F-W04-01~10 | 평가 입력 전체 | P0 |
| Web | TAB-W06 | F-W06-01~04 | 설정 기본 | P0 |
| Mobile | TAB-M01 | F-M01-01~04, 06~07 | 홈 기본 | P0 |
| Mobile | TAB-M02 | F-M02-01~04 | 주간 리포트 기본 | P0 |
| Mobile | TAB-M03 | F-M03-01~02, 05 | 합격 확률 기본 | P0 |
| Mobile | TAB-M05 | F-M05-01~03, 07 | 내 정보 기본 | P0 |

### 포함 비기능

| NFR ID | 항목 |
|:-------|:-----|
| NFR-P01 | API 응답 시간 (기본) |
| NFR-P02 | AI 피드백 생성 시간 |
| NFR-P04 | 페이지 초기 로딩 |
| NFR-S01 | 동시 사용자 (100명) |
| NFR-A01 | 서비스 가용성 (99%) |
| NFR-A05 | 에러율 |
| NFR-A07 | 백업 |
| NFR-SEC01~08 | 기본 보안 |
| NFR-O01, O05, O07 | 기본 관측성 |
| NFR-AI02~03, 08 | 피드백 품질 |

---

## 5.2 Phase 2: 핵심 기능 (Week 7-12)

### 목표
- Ask NeoPrime (Analytics) 출시
- Theory Engine v3 통합
- Elite 플랜 차별화 기능

### 포함 기능

| 플랫폼 | 탭 ID | 기능 ID | 기능명 | 우선순위 |
|:------:|:-----:|:--------|:-------|:--------:|
| Web | TAB-W01 | F-W01-04~08 | 대시보드 고급 | P1 |
| Web | TAB-W02 | F-W02-03, 05, 08, 10 | 학생 리스트 고급 | P1 |
| Web | TAB-W03 | F-W03-03, 06, 09, 11 | 학생 상세 고급 (Elite) | P1 |
| Web | TAB-W04 | F-W04-11, 13 | 평가 입력 고급 | P1 |
| Web | TAB-W05 | F-W05-01~09 | Ask NeoPrime 전체 | P0-P1 |
| Web | TAB-W06 | F-W06-05~08 | 설정 고급 (Elite) | P1 |
| Mobile | TAB-M01 | F-M01-05, 09 | 홈 고급 | P1 |
| Mobile | TAB-M02 | F-M02-05~06 | 주간 리포트 고급 | P1 |
| Mobile | TAB-M03 | F-M03-03~04, 06 | 합격 확률 고급 | P1 |
| Mobile | TAB-M04 | F-M04-01~05 | 유사 사례 전체 | P0-P1 |
| Mobile | TAB-M05 | F-M05-04~06, 09, 12 | 내 정보 고급 | P1 |

### 포함 비기능

| NFR ID | 항목 |
|:-------|:-----|
| NFR-P03 | Ask NeoPrime 쿼리 응답 시간 |
| NFR-P08 | 합격 예측 배치 처리 |
| NFR-S02~05 | 확장성 전체 |
| NFR-A02~04, 06 | 가용성 고급 |
| NFR-SEC10~12 | 보안 고급 |
| NFR-O02~04, 06 | 관측성 고급 |
| NFR-AI01, 04~05, 07 | AI 품질 고급 |

---

## 5.3 Phase 3: 고도화 (Week 13+)

### 목표
- 전체 기능 완성
- 성능/보안 고도화
- 확장 준비 (체대/음대 모듈)

### 포함 기능

| 플랫폼 | 탭 ID | 기능 ID | 기능명 | 우선순위 |
|:------:|:-----:|:--------|:-------|:--------:|
| Web | TAB-W02 | F-W02-09 | 엑셀 내보내기 | P2 |
| Web | TAB-W03 | F-W03-10 | 개별 리포트 | P2 |
| Web | TAB-W04 | F-W04-12, 14 | 일괄 평가, 자동저장 | P2 |
| Web | TAB-W05 | F-W05-10~12, S03~04, C05 | Analytics 고급 | P2 |
| Web | TAB-W06 | F-W06-09~10 | 설정 고급 | P2 |
| Mobile | TAB-M01 | F-M01-08 | 당겨서 새로고침 | P2 |
| Mobile | TAB-M02 | F-M02-07~08 | 공유, 반응 | P2 |
| Mobile | TAB-M03 | F-M03-07 | 합격선 비교 | P2 |
| Mobile | TAB-M04 | F-M04-06 | 사례 상세 모달 | P2 |
| Mobile | TAB-M05 | F-M05-08, 10~11 | 버전, 지원, 다운로드 | P2 |

### 포함 비기능

| NFR ID | 항목 |
|:-------|:-----|
| NFR-A08 | 재해 복구 |
| NFR-SEC13 | 보안 감사 |
| NFR-O08 | APM |
| NFR-AI06 | 편향 감지 |

---

## 5.4 우선순위 요약 매트릭스

### 기능별 Phase 분포

| Phase | P0 기능 | P1 기능 | P2 기능 | 합계 |
|:-----:|:-------:|:-------:|:-------:|:----:|
| Phase 1 | 35 | 5 | 0 | 40 |
| Phase 2 | 10 | 30 | 5 | 45 |
| Phase 3 | 0 | 5 | 20 | 25 |
| **합계** | **45** | **40** | **25** | **110** |

### 플랜별 기능 분포

| 플랜 | Phase 1 | Phase 2 | Phase 3 | 합계 |
|:-----|:-------:|:-------:|:-------:|:----:|
| All (공통) | 38 | 25 | 15 | 78 |
| Elite 전용 | 2 | 20 | 10 | 32 |

---

## 부록: 인터페이스 타입 정의 전체

```typescript
// ===== 공통 타입 =====
type ISO8601String = string;
type PlanType = 'elite' | 'standard' | 'public';
type UserRole = 'director' | 'teacher' | 'student' | 'parent';
type AdmissionLine = 'TOP' | 'HIGH' | 'MID' | 'LOW' | 'DISQUALIFIED';

interface FourAxisScore {
  composition: number;
  tone: number;
  concept: number;
  completion: number;
}

// ===== API 응답 공통 =====
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  metadata?: {
    requestId: string;
    timestamp: ISO8601String;
    latencyMs: number;
  };
}

// ===== Pagination =====
interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// ===== 학생 관련 =====
interface Student {
  id: string;
  academyId: string;
  name: string;  // 내부 저장 시 해싱
  nameDisplay: string;  // 표시용 "김OO"
  grade: '고1' | '고2' | '고3' | '재수';
  major: string;
  school?: string;
  targetUniversities: string[];
  currentLevel?: string;
  assignedTeacherId?: string;
  createdAt: ISO8601String;
  updatedAt: ISO8601String;
}

// ===== 평가 관련 =====
interface Evaluation {
  id: string;
  studentId: string;
  academyId: string;
  teacherId: string;
  weekNumber: number;
  seasonId: string;
  scores: FourAxisScore;
  overallLevel: string;
  workDescription: string;
  feedback: {
    positive: string;
    coreIssue: string;
    nextAction: string;
    isAIGenerated: boolean;
    isModified: boolean;
  };
  createdAt: ISO8601String;
}

// ===== 합격 예측 관련 =====
interface AdmissionPrediction {
  studentId: string;
  university: string;
  major: string;
  admissionType: string;
  probability: number;
  line: AdmissionLine;
  confidence: number;
  reasoning: string;
  similarCaseCount: number;
  similarCaseSuccessRate: number;
  computedAt: ISO8601String;
  engineVersion: string;
}

// ===== Meta-AI 설정 =====
interface TenantAIConfig {
  academyId: string;
  feedbackStyle: {
    tone: 'strict' | 'balanced' | 'encouraging';
    verbosity: 'concise' | 'standard' | 'detailed';
    emphasisAreas: ('composition' | 'tone' | 'concept' | 'completion')[];
  };
  predictionWeights: {
    recentEvaluationWeight: number;
    growthMomentumWeight: number;
    historicalDataWeight: number;
  };
  customPromptPrefix?: string;
  customPromptSuffix?: string;
  cutoffAdjustments?: Record<string, number>;
  updatedAt: ISO8601String;
  version: number;
}
```

---

**문서 끝**

| 항목 | 내용 |
|:-----|:-----|
| **문서 ID** | FRS-NEOPRIME-001 |
| **버전** | 1.0 |
| **최종 수정** | 2026-01-21 |
| **다음 리뷰** | 2026-01-28 |
| **승인자** | TBD |
