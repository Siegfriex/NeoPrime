# NeoPrime IA 서비스정보구조 문서 업데이트 내역

**버전**: 1.0 → 1.1  
**업데이트 일시**: 2026-01-21  
**기준**: 실제 구현 코드 분석 완료

---

## 📋 업데이트 요약

### 변경 사항
- ✅ 실제 라우팅 구조 반영 (`App.tsx` 기준)
- ✅ 실제 구현된 화면 및 기능 상태 업데이트
- ✅ URL 구조 상세 테이블 실제 구현 기준으로 수정

---

## 🔄 주요 변경 내용

### 1. 사이트맵 업데이트

#### 변경 전
```
/students/list              → 전체 학생 리스트
/evaluations/history        → 평가 이력 조회
/analytics/admission        → 합격 예측 분석
/analytics/growth           → 성장 분석
/analytics/teacher-bias     → 강사 편차 분석
/analytics/reports          → 리포트 다운로드
```

#### 변경 후 (실제 구현)
```
/students                   → StudentList (학생 목록 & 분석)
/evaluations/new            → EvaluationEntry (평가 입력)
/analytics                  → Analytics (고급 분석 Lab, 3-Tab)
/simulation                 → AdmissionSimulator (입시 시뮬레이터) [신규]
```

**주요 차이점**:
1. `/students/list` → `/students`로 단순화
2. `/evaluations/history`는 StudentDetail 페이지로 통합됨
3. `/analytics`는 단일 페이지에서 3-Tab으로 통합 (Explain/Compare/Simulate)
4. `/simulation` 페이지 추가 (IA에는 없었음)

### 2. URL 구조 상세 테이블 업데이트

**추가된 컬럼**:
- 컴포넌트명 (실제 파일명)
- 상태 (✅ 완료 / 🔲 미구현)

**수정된 URL**:
- `/students/list` → `/students`
- `/analytics/*` → `/analytics` (단일 페이지)
- `/simulation` 추가

### 3. 기능명세 업데이트

#### Dashboard (TAB-W01)
**추가된 기능**:
- 시즌 컨텍스트 바 (F-W01-01)
- 전략적 갭 분석 (F-W01-05)
- 리스크 진단 테이블 (F-W01-06)
- 실행 큐 (F-W01-07)
- 코호트 성과 추이 (F-W01-08)
- 집중 관리 대상 (F-W01-09)
- 데이터 건전성 (F-W01-10)

**제거된 기능**:
- 평균 레벨 카드 (실제 구현 없음)
- 레벨 분포 차트 (실제 구현 없음)

#### StudentList (TAB-W02)
**완전히 재작성**:
- 대학별 그룹 아코디언 (F-W02-01)
- 상대적 위치 분석 (F-W02-03) [신규 기능]
- 뷰 모드 전환 (F-W02-04) [신규 기능]
- 인터랙티브 사이드 패널 (F-W02-05) [신규 기능]
- AI Insight 오버레이 (F-W02-06) [신규 기능]

**제거된 기능**:
- 학년 필터 (실제 구현 없음)
- 반/담당강사 필터 (실제 구현 없음)
- 정렬 기능 (실제 구현 없음)

---

## 📊 구현 상태 요약

### 완료된 화면 (11개)
1. ✅ Dashboard (`/`)
2. ✅ StudentList (`/students`)
3. ✅ StudentDetail (`/students/:id`)
4. ✅ StudentAdd (`/students/new`)
5. ✅ EvaluationEntry (`/evaluations/new`)
6. ✅ Analytics (`/analytics`)
7. ✅ AdmissionSimulator (`/simulation`)
8. ✅ Login (`/auth/login`)
9. ✅ Signup (`/auth/signup`)
10. ✅ Settings (`/settings`)
11. ✅ Profile (`/profile`)

### 미구현 기능
- ⏳ 평가 이력 조회 페이지 (StudentDetail로 통합됨)
- ⏳ 리포트 다운로드 기능 (버튼만 존재)
- ⏳ 강사 관리 기능 (Settings 탭에 "준비 중" 표시)
- ⏳ 학원 정보 수정 기능 (Settings 탭에 "준비 중" 표시)

---

## 🎯 다음 단계

1. ✅ IA 문서 업데이트 완료
2. ✅ FRD 문서 작성 완료 (`NeoPrime_FRD_프론트엔드명세서_v1.md`)
3. ⏳ 기존 PRD 문서 참조 업데이트 (필요 시)

---

**작성자**: AI Assistant  
**검증 상태**: ✅ 실제 코드베이스 검증 완료
