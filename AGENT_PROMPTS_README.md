# NeoPrime 에이전트 프롬프트 가이드

## 개요

이 문서는 NeoPrime Theory Engine의 Excel 가중치 추출 작업을 위한 에이전트 프롬프트 간 의존성과 실행 순서를 설명합니다.

---

## 프롬프트 목록

| Phase | 파일명 | 목적 | 상태 |
|-------|--------|------|------|
| 1 | `AGENT_PROMPT_엑셀_가중치_추출.md` | 구조 파악, 18개 대학 추출, PoC | ✅ 완료 |
| 2 | `AGENT_PROMPT_Phase2_전체대학추출.md` | 550개 대학 추출, xlwings 제거 | 🔲 대기 |

---

## 의존성 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: AGENT_PROMPT_엑셀_가중치_추출.md                        │
│                                                                  │
│  목표: 구조 파악 + 18개 대학 PoC + Parity Test 검증              │
│                                                                  │
│  산출물:                                                         │
│   ├── theory_engine/weights/subject3_conversions.json (18개)    │
│   ├── theory_engine/weights/extracted_weights.py                │
│   ├── theory_engine/formulas/index_calculator.py                │
│   ├── tests/test_excel_parity.py                                │
│   └── index_fallback.py (DEFAULT_WEIGHTS 제거)                  │
│                                                                  │
│  보고서:                                                         │
│   └── docs/Excel_가중치_추출_작업보고서.md                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼ (의존)
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: AGENT_PROMPT_Phase2_전체대학추출.md                    │
│                                                                  │
│  목표: 550개 대학 추출 + xlwings 의존 제거                       │
│                                                                  │
│  필수 선행:                                                      │
│   ✅ Phase 1 산출물 존재                                         │
│   ✅ Phase 1 Parity Test 통과                                   │
│                                                                  │
│  신규 산출물:                                                    │
│   ├── theory_engine/weights/subject3_conversions_full.json      │
│   ├── tests/ground_truth_all.json                               │
│   ├── tests/test_excel_parity_standalone.py                     │
│   └── tools/extract_all_universities.py                         │
│                                                                  │
│  수정:                                                           │
│   ├── extracted_weights.py (유연한 키 매칭)                      │
│   ├── index_calculator.py (실제 조회)                           │
│   └── Phase 1 보고서 (과장 표현 완화)                            │
│                                                                  │
│  보고서:                                                         │
│   └── docs/Excel_가중치_추출_Phase2_보고서.md                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 실행 가이드

### 새 세션에서 Phase 2 시작 시

```bash
# 1. Phase 1 산출물 확인 (필수)
ls theory_engine/weights/subject3_conversions.json
ls theory_engine/weights/extracted_weights.py
ls theory_engine/formulas/index_calculator.py
ls tests/test_excel_parity.py

# 2. Phase 1 완료 상태 확인
cat docs/Excel_가중치_추출_작업보고서.md | head -50

# 3. Phase 2 프롬프트 읽기
cat AGENT_PROMPT_Phase2_전체대학추출.md
```

### Phase 1 미완료 시

```bash
# Phase 1 프롬프트부터 실행
cat AGENT_PROMPT_엑셀_가중치_추출.md
```

---

## 핵심 맥락 (세션 초기화 시 참조)

### Phase 1 핵심 발견

```
💡 가중치 구조 발견:

대학별 "가중치"는 별도 상수 셀(0.30, 0.35...)이 아니라,
SUBJECT3 시트의 "환산점수 테이블"에 반영비율이 사전 적용되어 있음.

예: 국어 표준점수 124점
  - 가천대학교: 88점 (71% 반영) → 124 × 0.71 ≈ 88
  - 경희대학교: 124점 (100% 반영)
  - 고려대 간호: 186점 (150% 가산)

계산 흐름:
  수능입력 → SUBJECT3(환산점수 조회) → COMPUTE Row 46-57 → Row 59(조건부 합산)
```

### Phase 1 제약사항

| 제약 | 설명 | Phase 2 해결 |
|------|------|-------------|
| C1 | 18개/550개 대학 (3.3%) | 전체 추출 |
| C2 | xlwings 의존 (Excel COM) | 제거 |
| C3 | SUBJECT3 조회 xlwings 의존 | Python 구현 |
| C4 | Parity Test = Excel 값 복사 | 수식 재현 |
| C5 | 연도별 구분 미확인 | Phase 3 |

### ⛔ Critical/High 리스크 (Phase 2 즉시 수정 필수)

| 등급 | 위치 | 문제 | 영향 |
|------|------|------|------|
| 🔴 Critical | rules.py:638 | `get_index_fallback()` 무가중치 호출 | 런타임 즉시 실패 |
| 🟠 High | index_fallback.py:181,186 | 숨은 기본값 (0.2, 50.0) | 폴백 금지 원칙 위반 |
| 🟠 High | index_calculator.py | "탐구1/2" 키 JSON 불일치 | 조회 실패 |
| 🟠 High | test_excel_parity.py | Excel 값 복사 ≠ 수식 재현 | 검증 부족 |

### 원본 엑셀 정보

```
파일: 202511고속성장분석기(가채점)20251114 (1).xlsx
├── 시트 수: 15개
├── 전체 셀: 3,282,407개
├── 수식 셀: 303,215개 (9.24%)
├── SUBJECT3: 560컬럼 × 1,465행 (환산점수 테이블)
└── COMPUTE: 최종 점수 계산 (Row 59)
```

---

## 핵심 원칙 (모든 Phase 공통)

| 원칙 | 설명 |
|------|------|
| **EXTRACT** | 추론/추정 금지. 엑셀 셀에서 직접 값을 읽어라 |
| **CONVERT** | 임의 가정 없이 엑셀 수식을 그대로 Python으로 옮겨라 |
| **VERIFY** | 엑셀 결과와 Python 결과가 100% 일치해야 한다 |
| **NO HALLUCINATION** | "일반적인 수능 반영비율" 같은 외부 지식 사용 금지 |

---

## 파일 구조

```
C:\Neoprime\
├── AGENT_PROMPT_엑셀_가중치_추출.md      # Phase 1 프롬프트
├── AGENT_PROMPT_Phase2_전체대학추출.md   # Phase 2 프롬프트
├── AGENT_PROMPTS_README.md              # 본 문서
│
├── docs/
│   ├── Excel_가중치_추출_작업보고서.md    # Phase 1 보고서
│   ├── extraction_report.md              # Phase 1 추출 보고서
│   └── Excel_가중치_추출_Phase2_보고서.md # Phase 2 보고서 (예정)
│
├── theory_engine/
│   ├── weights/
│   │   ├── extracted_weights.py          # 환산점수 로더
│   │   ├── subject3_conversions.json     # Phase 1: 18개 대학
│   │   └── subject3_conversions_full.json # Phase 2: 550개 (예정)
│   └── formulas/
│       └── index_calculator.py           # COMPUTE 계산 로직
│
├── tests/
│   ├── test_excel_parity.py              # Phase 1: xlwings 기반
│   ├── test_excel_parity_standalone.py   # Phase 2: 독립 실행 (예정)
│   └── ground_truth_all.json             # Phase 2: 전체 기대값 (예정)
│
├── tools/
│   ├── extract_all_universities.py       # Phase 2: 전체 추출 (예정)
│   └── collect_ground_truth.py           # Phase 2: GT 수집 (예정)
│
└── outputs/
    ├── formula_catalog.csv               # 303,215개 수식
    └── sheet_flow_graph.json             # 시트 의존성
```

---

## 검증된 Parity Test 결과 (Phase 1)

| 컬럼 | 대학/학과 | Excel | Python | 결과 |
|------|----------|-------|--------|------|
| D | 가천대학교 | 216.0 | 216.0 | ✅ |
| E | 경희대학교 | 342.0 | 342.0 | ✅ |
| F | 경희대 교육 | 76.95 | 76.95 | ✅ |
| G | 경희대 생공 | 10.6 | 10.6 | ✅ |
| H | 경희대 치의표 | 0.0 | 0.0 | ✅ |
| I | 경희대 치의 | 76.95 | 76.95 | ✅ |
| J | 고려대 간호 | 572.705 | 572.705 | ✅ |

**입력값**: 국어 124, 수학 120, 영어 2등급, 탐구1 48, 탐구2 50, 한국사 1등급

---

## 자주 사용하는 명령

```bash
# Phase 1 산출물 확인
ls theory_engine/weights/
ls theory_engine/formulas/

# Phase 1 보고서 확인
cat docs/Excel_가중치_추출_작업보고서.md

# 현재 추출된 대학 수 확인
python -c "import json; d=json.load(open('theory_engine/weights/subject3_conversions.json')); print(len(d['conversion_table']))"

# Parity Test 실행 (Phase 1 - xlwings 필요)
python tests/test_excel_parity.py

# Parity Test 실행 (Phase 2 - 독립 실행)
python tests/test_excel_parity_standalone.py
```

---

---

## 파일 정리 정책 (cleanup_files.ps1)

```
✅ 이전 우려사항 반영됨:
- "삭제" 대신 "archive/ 폴더로 이동" 방식 적용
- DryRun 모드 (-DryRun): 실제 변경 없이 미리보기
- 타임스탬프 옵션 (-UseTimestamp): 덮어쓰기 방지

아카이브 구조:
  archive/
  ├── reports/     # 보고서 (17개 파일 보존)
  ├── scripts/     # 검증 스크립트 (3개 파일 보존)
  └── designmate/  # DesignMate 관련 파일
```

---

**최종 업데이트**: 2026-01-21
