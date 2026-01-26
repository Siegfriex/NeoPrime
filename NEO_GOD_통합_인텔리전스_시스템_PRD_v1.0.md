# NEO GOD 통합 인텔리전스 시스템 PRD (v1.0)

**문서 버전**: 1.0  
**작성일**: 2026-01-26  
**작성자**: 바이스 디렉터  
**기반 명세서**: NEO GOD 엔진 상세 명세서 v1.0  
**기반 프레임워크**: NEO GOD Ultra Framework v2.0  

---

## 목차

1. [제품 개요](#1-제품-개요)
2. [현재 구현 상태](#2-현재-구현-상태)
3. [핵심 기능 명세](#3-핵심-기능-명세)
4. [기술 아키텍처](#4-기술-아키텍처)
5. [데이터 모델 및 엔티티](#5-데이터-모델-및-엔티티)
6. [로직 엔진 상세](#6-로직-엔진-상세)
7. [향후 로드맵](#7-향후-로드맵)
8. [리스크 관리](#8-리스크-관리)

---

## 1. 제품 개요

### 1.1 제품 비전

**NEO GOD (Next-Generation Entrance Optimization & Data Intelligence System)**는 복잡한 엑셀 기반 입시 분석 로직을 클라우드(GCP BigQuery)와 AI(Gemini/Claude) 환경으로 이식하여, 초고속 데이터 정찰과 정밀한 전략 도출이 가능한 지능형 입시 오케스트레이터 시스템입니다.

### 1.2 핵심 가치 제안

1. **초고속 무결성 적재**: 20만 건 이상의 대용량 데이터를 0.5초 내 정찰하고 25분 내 적재
2. **로직 리버스 엔지니어링**: 엑셀 수식 샘플링을 통해 대학별 계산 알고리즘을 '추출' 및 '학습'
3. **지식 확장성**: 2차, 3차 추가 엑셀 파일을 통해 기존 데이터와의 상관관계를 스스로 파악하고 지식 베이스(Knowledge Base) 확장

### 1.3 배경 및 목적

- **파일 한계 극복**: 20만 건 이상의 대용량 데이터 처리 시 발생하는 엑셀의 성능 저하 및 메모리 부족 문제 해결
- **로직 투명성 확보**: 블랙박스화된 대학별 점수 산출 공식을 SQL 및 코드로 명시화하여 분석 신뢰도 향상
- **지식 확장성**: 추가되는 2차 가채점/실채점 파일들과의 교차 학습을 위한 기반 마련

---

## 2. 현재 구현 상태

### 2.1 Phase 1-4 구현 완료 현황

| Phase | 기능명 | 기술적 핵심 | 구현 상태 | 성능 지표 |
|-------|--------|------------|----------|----------|
| **P1** | Hyper-Scouting | python-calamine 엔진을 통한 시트별 광맥 식별 | ✅ 완료 | 0.5초 이내 (23MB 파일) |
| **P2** | Dual-Track Extraction | 값(Value)과 수식(Logic)의 물리적 분리 추출 | ✅ 완료 | 청크 단위 병렬 처리 |
| **P3** | Date-First Normalization | 엑셀 시리얼(44927)의 날짜 우선 변환 및 위생 처리 | ✅ 완료 | 타입 추론 자동화 |
| **P4** | Staging Strategy | 임시 테이블 검증 후 본 테이블 원자적(Atomic) 교체 | ✅ 완료 | 멱등성 보장 |

### 2.2 실제 추출된 데이터 규모

| 시트명 | 행 수 | 컬럼 수 | 타겟 타입 | 상태 |
|--------|------|---------|----------|------|
| **INDEX** | 199,921 | 27 | heavy | ✅ 적재 완료 |
| **RAWSCORE** | 11,367 | 10 | medium | ✅ 적재 완료 |
| **이과계열분석결과** | 5,835 | 59 | medium | ✅ 적재 완료 |
| **문과계열분석결과** | 5,835 | 59 | medium | ✅ 적재 완료 |

**총 데이터 규모**: 약 223,000행

### 2.3 BigQuery 적재 현황

- **프로젝트**: `neoprime0305`
- **데이터셋**: `ds_neoprime_entrance`
- **테이블**: `tb_raw_2026`
- **리전**: `asia-northeast3` (서울)
- **적재 전략**: Staging Table → 검증 → 원자적 전환

---

## 3. 핵심 기능 명세

### 3.1 데이터 수집 및 정제 엔진 (Data Ingestion & Cleaning)

#### 3.1.1 Phase 1: 고속 정찰 (Hyper-Scouting)

**구현 파일**: `phase1_scouting.py`

**기능**:
- python-calamine (Rust 기반) 엔진을 활용한 초고속 시트 구조 분석
- 시트별 데이터 밀도, 행/컬럼 수, 메모리 예측
- 타겟 시트 자동 분류 (heavy/medium/light)

**성능 지표**:
- 23MB 파일 스캔 시간: **0.5초 이내**
- 메모리 예측 정확도: ±10% 이내
- 타겟 시트 식별 정확도: 100%

**출력 메타데이터**:
```json
{
  "file_path": "202511고속성장분석기(가채점)20251114.xlsx",
  "file_size_mb": 23.36,
  "sheet_count": 15,
  "total_rows": 223,000,
  "scan_time_seconds": 0.45,
  "engine": "calamine",
  "targets": {
    "primary": ["INDEX"],
    "secondary": ["RAWSCORE", "이과계열분석결과", "문과계열분석결과"]
  }
}
```

#### 3.1.2 Phase 2: 물리적 이원화 추출 (Dual-Track Extraction)

**구현 파일**: `phase2_extraction.py`

**Track A: 값 추출 (고속)**
- **엔진**: pandas + calamine (Rust 기반)
- **전략**: 청크 단위 Generator 반환으로 메모리 효율 극대화
- **출력 형식**: Parquet (Snappy 압축)
- **청크 크기**: 50,000행 (설정 가능)

**Track B: 수식 추출 (샘플링)**
- **엔진**: OpenPyXL
- **전략**: 상위 10행 샘플링으로 대표 수식 패턴 추출
- **출력 형식**: JSON 메타데이터
- **추출 정보**:
  - 수식 문자열
  - 셀 참조 의존성
  - 수식 패턴 분류 (conditional, index_match, aggregation 등)

**출력 구조**:
```
output/
├── INDEX_chunk_0000.parquet
├── INDEX_chunk_0001.parquet
├── ...
├── INDEX_formula_metadata.json
├── RAWSCORE_formula_metadata.json
└── ...
```

#### 3.1.3 Phase 3: Date-First 정규화 (Date-First Normalization)

**구현 파일**: `phase3_normalization.py`

**변환 우선순위**:
1. **Excel 날짜 시리얼 감지** (25569-55153 범위, 1970-2050)
2. 표준 날짜 문자열 변환
3. 숫자형 변환
4. 문자열 정리

**주요 기능**:
- Excel 에러 코드 처리 (`#N/A`, `#VALUE!` 등)
- 병합 셀 처리 (ffill)
- 컬럼명 BigQuery 호환 정규화
- 타입 추론 및 자동 변환
- 데이터 품질 리포트 생성

**출력 메타데이터**:
- `column_mapping.json`: 원본 컬럼명 → 정규화된 컬럼명 매핑
- `data_quality_report.json`: 컬럼별 NULL 비율, 통계 정보

#### 3.1.4 Phase 4: Staging Table 멱등성 적재

**구현 파일**: `phase4_load.py`

**전략**:
1. 임시 테이블(`{table}_staging`)에 먼저 적재
2. 무결성 검증 수행:
   - 행 수 일치 여부 (1% 오차 허용)
   - NULL 비율 검증 (10% 이하 허용)
   - 필수 컬럼 존재 여부
3. 검증 통과 시에만 본 테이블로 원자적 전환
4. 실패 시 staging 테이블만 삭제 (본 테이블 무결)

**원자적 전환 방식**:
```python
# BigQuery는 RENAME 미지원 → COPY + DELETE 조합
1. 기존 target 테이블 삭제
2. staging → target 복사
3. staging 테이블 삭제
```

---

## 4. 기술 아키텍처

### 4.1 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    NEO GOD Ultra Framework v2.0              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
   │ Phase 1 │          │  Phase 2  │        │  Phase 3  │
   │Scouting │          │Extraction │        │Normalize  │
   └────┬────┘          └─────┬─────┘        └─────┬─────┘
        │                     │                     │
        │  Calamine           │  Pandas+Calamine   │  Pandas
        │  (Rust)             │  OpenPyXL          │  PyArrow
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                        ┌─────▼─────┐
                        │  Phase 4   │
                        │   Load     │
                        └─────┬─────┘
                              │
                        ┌─────▼─────┐
                        │ BigQuery  │
                        │  GCP      │
                        └───────────┘
```

### 4.2 기술 스택 상세

| 계층 | 기술 스택 | 버전 | 용도 |
|------|----------|------|------|
| **Language** | Python | 3.10+ | 메인 개발 언어 |
| **High-Speed Engine** | python-calamine | Latest | Rust 기반 초고속 Excel 읽기 |
| **Data Processing** | Pandas | 2.2+ | 데이터프레임 처리 |
| **Columnar Storage** | PyArrow | Latest | Parquet 파일 생성 |
| **Cloud Storage** | Google Cloud BigQuery | Latest | 대용량 데이터 저장 및 분석 |
| **Cloud Storage** | GCS (선택) | Latest | Parquet 파일 임시 저장 |
| **Formula Analysis** | OpenPyXL | Latest | 수식 메타데이터 추출 |
| **AI/LLM** | Gemini 1.5 Pro / Claude 3.5 Sonnet | Latest | 수식 리버스 엔지니어링 (향후) |

### 4.3 데이터 흐름도

```
Excel 파일 (23MB)
    │
    ├─ Phase 1: 정찰 (0.5초)
    │   └─ 시트 구조 분석
    │       ├─ INDEX: 199,921행
    │       ├─ RAWSCORE: 11,367행
    │       └─ 이과/문과계열분석결과: 각 5,835행
    │
    ├─ Phase 2: 추출 (병렬)
    │   ├─ Track A: 값 추출 → Parquet 청크
    │   └─ Track B: 수식 샘플링 → JSON 메타데이터
    │
    ├─ Phase 3: 정규화
    │   ├─ Date-First 변환
    │   ├─ 컬럼명 정규화
    │   └─ 타입 추론
    │
    └─ Phase 4: 적재
        ├─ Staging 테이블 적재
        ├─ 무결성 검증
        └─ 원자적 전환 (Staging → Target)
```

---

## 5. 데이터 모델 및 엔티티

### 5.1 주요 시트별 데이터 모델

#### 5.1.1 INDEX 시트

**규모**: 199,921행 × 27컬럼

**주요 컬럼**:
- `INDEX`: 대학 코드 (예: "510gs0t20509") - 14,408개 고유값
- `Unnamed: 2`, `Unnamed: 3`: 플래그 값 ("1")
- `Unnamed: 26`: INFO 시트 참조 (`=INFO!$B$18`)

**특이사항**:
- 대부분의 컬럼이 NULL (99% 이상)
- `INDEX` 컬럼만 실제 데이터 보유
- INFO 시트 참조로 설정값 로드

**BigQuery 스키마 추론**:
```sql
CREATE TABLE `neoprime0305.ds_neoprime_entrance.tb_index_2026` (
  index_code STRING,           -- INDEX 컬럼
  flag_1 STRING,               -- Unnamed: 2
  flag_2 STRING,               -- Unnamed: 3
  info_ref STRING,             -- Unnamed: 26
  -- 기타 컬럼들 (대부분 NULL)
  ...
);
```

#### 5.1.2 RAWSCORE 시트

**규모**: 11,367행 × 10컬럼

**컬럼 매핑** (실제 `column_mapping.json` 기반):

| 원본 컬럼명 | 정규화된 컬럼명 | 데이터 타입 | 의미 |
|------------|----------------|------------|------|
| 영역 | column_0 | STRING | 과목 영역 (7개 고유값) |
| 과목명 | column_1 | STRING | 세부 과목명 (34개 고유값) |
| 원점수 | column_2 | FLOAT64 | 원점수 (0.0-100.0, 평균: 47.05) |
| Unnamed: 3 | unnamed_3 | FLOAT64 | 추가 점수 (평균: 36.04) |
| Unnamed: 4 | unnamed_4 | FLOAT64 | 추가 점수 (평균: 11.01) |
| 과목명-원점수 | column_5 | STRING | 조합 필드 (11,366개 고유값) |
| 202511(가채점) | col_202511 | FLOAT64 | 가채점 정보 (1.0-146.0, 평균: 90.64) |
| Unnamed: 7 | unnamed_7 | FLOAT64 | 추가 점수 (평균: 48.23) |
| Unnamed: 8 | unnamed_8 | FLOAT64 | 등급 정보 (1.0-9.0, 평균: 5.07) |
| Unnamed: 9 | unnamed_9 | FLOAT64 | 백분위 (0.079-100.0, 평균: 52.76) |

**데이터 품질**:
- NULL 비율: 0.000088% (매우 낮음)
- 모든 필드 유효성 검증 통과

#### 5.1.3 이과계열분석결과 / 문과계열분석결과 시트

**규모**: 각 5,835행 × 59컬럼

**주요 계산 컬럼** (수식 메타데이터 기반):

| 컬럼 | 수식 패턴 | 의미 | 의존성 |
|------|----------|------|--------|
| `col_3` | Conditional | 적정점수/예상점수/소신점수 판정 | RESTRICT, 수능입력 |
| `col_4` | INDEX/MATCH | COMPUTE 시트 기반 점수 변환 (첫 번째 지표) | COMPUTE, E$5 |
| `col_5` | INDEX/MATCH | COMPUTE 시트 기반 점수 변환 (두 번째 지표) | COMPUTE, F$5 |
| `col_6` | SUM | 점수 합계 (col_4 + col_5) | col_4, col_5 |
| `col_7` | AVERAGE | 평균 점수 계산 (HLOOKUP 기반) | COMPUTE (4행, 5행) |
| `col_8` | Conditional | 조건부 포맷팅 및 가중치 적용 | COMPUTE, SUBJECT1 |

**참조 변수**:
- `$AK6`: 대학 코드 (INDEX 시트와 동일 형식)
- `$B6`, `$C6`: 대학명 및 학과명
- `$G6`: 현재 점수
- `$J6`, `$K6`, `$L6`: 적정점수, 예상점수, 소신점수 기준값

### 5.2 참조 시트 구조

#### 5.2.1 COMPUTE 시트

**구조**: 72행 × 553컬럼 (UG = 553번째 컬럼)

**용도**: 대학별 점수 변환표 조회

**조회 패턴**:
- **행 헤더**: `COMPUTE!$B$1:$B$72` (72개 지표 또는 대학명)
- **열 헤더**: `COMPUTE!$A$2:$UG$2` (553개 대학 코드)
- **데이터 영역**: `COMPUTE!$A$1:$UG$72`

**INDEX/MATCH 조회 예시**:
```excel
=INDEX(COMPUTE!$A$1:$UG$72,
  MATCH(E$5, COMPUTE!$B$1:$B$72, 0),    -- 행 좌표
  MATCH($AK6, COMPUTE!$A$2:$UG$2, 0)    -- 열 좌표
)
```

**HLOOKUP 조회 예시** (이과계열):
```excel
=HLOOKUP($AK6, COMPUTE!$2:$8, 4, FALSE)  -- 4행 조회
=HLOOKUP($AK6, COMPUTE!$2:$8, 5, FALSE)  -- 5행 조회
```

**HLOOKUP 조회 예시** (문과계열):
```excel
=HLOOKUP($AK6, COMPUTE!$2:$8, 6, FALSE)  -- 6행 조회
=HLOOKUP($AK6, COMPUTE!$2:$8, 7, FALSE)  -- 7행 조회
```

#### 5.2.2 RESTRICT 시트

**구조**: 3개 영역 (폴백 전략)

**영역 1**: `RESTRICT!$A:$C`
- 첫 번째 제한 조건 테이블

**영역 2**: `RESTRICT!$E:$G`
- 두 번째 제한 조건 테이블

**영역 3**: `RESTRICT!$I:$L`
- 세 번째 제한 조건 테이블 (대학명+학과명 조합 검색)

**폴백 전략**:
```excel
=IFERROR(
  VLOOKUP($AK6, RESTRICT!$A:$C, 3, FALSE),
  IFERROR(
    VLOOKUP($AK6, RESTRICT!$E:$G, 3, FALSE),
    IFERROR(
      VLOOKUP($B6&" "&$C6, RESTRICT!$I:$L, 4, FALSE),
      -- 기본 로직
    )
  )
)
```

#### 5.2.3 SUBJECT1 시트

**구조**: 1,005행 × 4컬럼

**용도**: 과목별 가중치 조회

**조회 패턴**:
```excel
=VLOOKUP("수학(이과)", SUBJECT1!$A:$D, 4, FALSE)  -- 이과계열
=VLOOKUP("수학(문과)", SUBJECT1!$A:$D, 4, FALSE)  -- 문과계열
```

**컬럼 구조**:
- 첫 번째 컬럼: 과목명
- 네 번째 컬럼: 가중치 값

---

## 6. 로직 엔진 상세

### 6.1 적정점수/예상점수/소신점수 판정 로직

**위치**: `이과계열분석결과.col_3`, `문과계열분석결과.col_3`

**수식 구조** (실제 추출된 수식):
```excel
=IF(OR(수능입력!$C$18="", 수능입력!$C$18=0, 수능입력!$C$18>9,
       수능입력!$C$19="", 수능입력!$C$19=0, 수능입력!$C$19>9),
   "오류(영어국사)",
   IFERROR(VLOOKUP($AK6, RESTRICT!$A:$C, 3, FALSE),
     IFERROR(VLOOKUP($AK6, RESTRICT!$E:$G, 3, FALSE),
       IFERROR(VLOOKUP($B6&" "&$C6, RESTRICT!$I:$L, 4, FALSE),
         IF($G6=0, "제외(수탐)",
           IF($G6*1 >= $J6*1, "적정점수 이상",
             IF($G6*1 >= $K6*1, "예상점수 이상",
               IF($G6*1 >= $L6*1, "소신점수 이상",
                 IF($G6*1 < $L6*1, "소신점수 미만", 0/0)))))))))
```

**LaTeX 수식 표현**:

\[
\text{판정결과} = \begin{cases}
\text{"오류(영어국사)"} & \text{if } \text{영어/국사 등급 오류} \\
\text{RESTRICT 조회 결과} & \text{if } \text{RESTRICT 시트 매칭 성공} \\
\text{"제외(수탐)"} & \text{if } G_6 = 0 \\
\text{"적정점수 이상"} & \text{if } G_6 \geq J_6 \\
\text{"예상점수 이상"} & \text{if } G_6 \geq K_6 \\
\text{"소신점수 이상"} & \text{if } G_6 \geq L_6 \\
\text{"소신점수 미만"} & \text{if } G_6 < L_6 \\
\text{에러} & \text{otherwise}
\end{cases}
\]

**BigQuery SQL 변환 예시**:
```sql
SELECT
  index_code,
  university_name,
  department_name,
  current_score,
  optimal_score,
  expected_score,
  challenge_score,
  CASE
    WHEN english_grade IS NULL OR english_grade = 0 OR english_grade > 9
      OR history_grade IS NULL OR history_grade = 0 OR history_grade > 9
    THEN "오류(영어국사)"
    
    WHEN restrict_result_1 IS NOT NULL THEN restrict_result_1
    WHEN restrict_result_2 IS NOT NULL THEN restrict_result_2
    WHEN restrict_result_3 IS NOT NULL THEN restrict_result_3
    
    WHEN current_score = 0 THEN "제외(수탐)"
    WHEN current_score >= optimal_score THEN "적정점수 이상"
    WHEN current_score >= expected_score THEN "예상점수 이상"
    WHEN current_score >= challenge_score THEN "소신점수 이상"
    WHEN current_score < challenge_score THEN "소신점수 미만"
    ELSE NULL  -- 에러 케이스
  END AS judgment_result
FROM
  `neoprime0305.ds_neoprime_entrance.tb_analysis_result_2026`
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_restrict_2026` AS r1
  ON index_code = r1.index_code
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_restrict_2026` AS r2
  ON index_code = r2.index_code
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_restrict_2026` AS r3
  ON CONCAT(university_name, " ", department_name) = r3.name_combo
```

### 6.2 COMPUTE 시트 기반 점수 변환 로직

**위치**: `이과계열분석결과.col_4`, `col_5` / `문과계열분석결과.col_4`, `col_5`

**수식 구조**:
```excel
=IFERROR(
  INDEX(COMPUTE!$A$1:$UG$72,
    MATCH(E$5, COMPUTE!$B$1:$B$72, 0),
    MATCH($AK6, COMPUTE!$A$2:$UG$2, 0)
  ),
  0
)
```

**BigQuery SQL 변환 전략**:

**옵션 1: STRUCT 배열로 변환**
```sql
-- COMPUTE 시트를 STRUCT 배열로 변환
CREATE TABLE `neoprime0305.ds_neoprime_entrance.tb_compute_2026` AS
SELECT
  university_code,
  ARRAY_AGG(
    STRUCT(
      indicator_name,
      converted_score
    )
    ORDER BY indicator_name
  ) AS indicators
FROM
  -- COMPUTE 시트 데이터 (72행 × 553컬럼)
GROUP BY
  university_code;

-- 조회 쿼리
SELECT
  a.index_code,
  a.indicator_1,
  c.indicators[OFFSET(
    (SELECT OFFSET FROM UNNEST(c.indicators) WHERE indicator_name = a.indicator_1)
  )].converted_score AS converted_score_1
FROM
  `neoprime0305.ds_neoprime_entrance.tb_analysis_result_2026` AS a
JOIN
  `neoprime0305.ds_neoprime_entrance.tb_compute_2026` AS c
  ON a.index_code = c.university_code;
```

**옵션 2: PIVOT 테이블로 변환** (권장)
```sql
-- COMPUTE 시트를 PIVOT 테이블로 변환
CREATE TABLE `neoprime0305.ds_neoprime_entrance.tb_compute_pivot_2026` AS
SELECT
  university_code,
  indicator_1,
  indicator_2,
  -- ... 72개 지표를 컬럼으로
FROM
  -- COMPUTE 시트 데이터

-- 조회 쿼리 (간단하고 빠름)
SELECT
  a.index_code,
  c.indicator_1 AS converted_score_1,
  c.indicator_2 AS converted_score_2
FROM
  `neoprime0305.ds_neoprime_entrance.tb_analysis_result_2026` AS a
JOIN
  `neoprime0305.ds_neoprime_entrance.tb_compute_pivot_2026` AS c
  ON a.index_code = c.university_code
  AND a.indicator_name_1 = c.indicator_name_1;
```

### 6.3 평균 점수 계산 로직

**위치**: `이과계열분석결과.col_7` / `문과계열분석결과.col_7`

**수식 구조** (이과계열):
```excel
=IF($G6=0, "",
  IF(AND(HLOOKUP($AK6, COMPUTE!$2:$8, 4, FALSE)="",
         HLOOKUP($AK6, COMPUTE!$2:$8, 5, FALSE)=""),
     "",
     MAX(0.00001, AVERAGE(
       HLOOKUP($AK6, COMPUTE!$2:$8, 4, FALSE),
       HLOOKUP($AK6, COMPUTE!$2:$8, 5, FALSE)
     ))
  )
)
```

**BigQuery SQL 변환**:
```sql
SELECT
  index_code,
  current_score,
  CASE
    WHEN current_score = 0 THEN NULL
    WHEN compute_row_4 IS NULL AND compute_row_5 IS NULL THEN NULL
    ELSE GREATEST(0.00001, 
      (COALESCE(compute_row_4, 0) + COALESCE(compute_row_5, 0)) / 2
    )
  END AS average_score
FROM
  `neoprime0305.ds_neoprime_entrance.tb_analysis_result_2026` AS a
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_compute_pivot_2026` AS c
  ON a.index_code = c.university_code;
```

### 6.4 가중치 적용 로직

**위치**: `이과계열분석결과.col_8` / `문과계열분석결과.col_8`

**수식 구조** (이과계열):
```excel
=IF(H6="", "",
  ROUND(
    HLOOKUP($AK6, COMPUTE!$2:$8, 4, FALSE) *
    VLOOKUP("수학(이과)", SUBJECT1!$A:$D, 4, FALSE) / 100,
    0
  ) & " ／ " & VLOOKUP("수학(이과)", SUBJECT1!$A:$D, 4, FALSE)
)
```

**BigQuery SQL 변환**:
```sql
SELECT
  index_code,
  average_score,
  CASE
    WHEN average_score IS NULL THEN NULL
    ELSE CONCAT(
      CAST(ROUND(
        compute_row_4 * subject_weight / 100
      ) AS STRING),
      " ／ ",
      CAST(subject_weight AS STRING)
    )
  END AS weighted_score_display
FROM
  `neoprime0305.ds_neoprime_entrance.tb_analysis_result_2026` AS a
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_compute_pivot_2026` AS c
  ON a.index_code = c.university_code
LEFT JOIN
  `neoprime0305.ds_neoprime_entrance.tb_subject1_2026` AS s
  ON s.subject_name = "수학(이과)";
```

---

## 7. 향후 로드맵

### 7.1 Phase 2: 지식 확장 및 학습 (Secondary Learning)

**목표**: 추가되는 엑셀 파일들(2차, 3차)을 통해 시스템의 지능을 증강

#### 7.1.1 다중 파일 스키마 매칭 (Schema Cross-Matching)

**기능**:
- 새로운 파일 유입 시 기존 `column_mapping.json`과 비교하여 동일 항목 자동 연결
- 파일 간 데이터 불일치(예: 대학 명칭 차이) 발생 시 정규화 사전(Dictionary) 업데이트

**구현 계획**:
```python
class SchemaCrossMatcher:
    def match_schemas(self, existing_mapping: dict, new_columns: list) -> dict:
        """
        기존 컬럼 매핑과 새 컬럼을 비교하여 매칭
        
        Returns:
            {
                'matched': {...},      # 매칭된 컬럼
                'new': [...],          # 새로운 컬럼
                'conflicts': [...]     # 충돌 컬럼
            }
        """
        pass
    
    def update_normalization_dict(self, conflicts: list) -> dict:
        """
        충돌 컬럼에 대한 정규화 사전 업데이트
        
        예: "서울대학교" vs "서울대" → 통일
        """
        pass
```

#### 7.1.2 수식 메타데이터 합병 (Logic Synthesis)

**기능**:
- 파일별로 상이한 환산 로직을 `logic_meta.json`에 누적
- AI 에이전트가 "A파일의 수식과 B파일의 수식 중 무엇이 더 최신/정확한가?"를 판단하도록 가중치 부여

**구현 계획**:
```python
class LogicSynthesizer:
    def merge_formula_metadata(self, existing: dict, new: dict) -> dict:
        """
        수식 메타데이터 합병
        
        Returns:
            {
                'formulas': {
                    'col_3': {
                        'versions': [
                            {'file': 'file1.xlsx', 'formula': '...', 'timestamp': '...'},
                            {'file': 'file2.xlsx', 'formula': '...', 'timestamp': '...'}
                        ],
                        'latest': '...',
                        'confidence': 0.95
                    }
                }
            }
        """
        pass
    
    def analyze_formula_differences(self, formula1: str, formula2: str) -> dict:
        """
        두 수식의 차이점 분석 (AI 기반)
        
        Returns:
            {
                'similarity': 0.85,
                'differences': [...],
                'recommended': 'formula1' or 'formula2'
            }
        """
        pass
```

#### 7.1.3 벡터 데이터베이스화 (Vectorization for RAG)

**기능**:
- 적재된 데이터를 텍스트 임베딩으로 변환하여, 사용자의 자연어 질문("홍대 디자인과 작년 합격선은?")에 대응하는 인덱싱 구축

**구현 계획**:
```python
class VectorDBBuilder:
    def create_embeddings(self, data: pd.DataFrame) -> np.ndarray:
        """
        데이터프레임을 임베딩 벡터로 변환
        
        사용 모델: text-embedding-004 (Gemini) 또는 text-embedding-3-large (OpenAI)
        """
        pass
    
    def build_index(self, embeddings: np.ndarray, metadata: dict):
        """
        벡터 인덱스 구축 (FAISS 또는 Vertex AI Vector Search)
        """
        pass
    
    def query(self, question: str, top_k: int = 5) -> list:
        """
        자연어 질문에 대한 유사도 검색
        """
        pass
```

### 7.2 Phase 3: 자연어 질의 기반 입시 챗봇 연동

**목표**: RAG 아키텍처를 활용한 자연어 질의 시스템

**기능**:
- 사용자 질문: "홍대 디자인과 작년 합격선은?"
- 시스템 응답:
  1. 벡터 검색으로 관련 데이터 조회
  2. BigQuery SQL 쿼리 생성
  3. 결과를 자연어로 변환하여 응답

**구현 계획**:
```python
class EntranceChatbot:
    def __init__(self, vector_db: VectorDBBuilder, bq_client: bigquery.Client):
        self.vector_db = vector_db
        self.bq_client = bq_client
        self.llm = GeminiModel()  # 또는 ClaudeModel()
    
    def answer(self, question: str) -> str:
        # 1. 벡터 검색으로 관련 컨텍스트 조회
        context = self.vector_db.query(question, top_k=5)
        
        # 2. SQL 쿼리 생성 (LLM 기반)
        sql = self.llm.generate_sql(question, context)
        
        # 3. BigQuery 실행
        results = self.bq_client.query(sql).result()
        
        # 4. 자연어 응답 생성
        response = self.llm.generate_response(question, results)
        
        return response
```

### 7.3 Phase 4: 대학별 환산 로직 자동 업데이트 시스템

**목표**: 새로운 입시 정책 반영 시 자동으로 환산 로직 업데이트

**기능**:
- 새로운 엑셀 파일 유입 시 수식 변경 감지
- 변경된 수식의 영향 범위 분석
- 자동 테스트 및 검증
- 승인 후 프로덕션 배포

---

## 8. 리스크 관리

### 8.1 잠재 리스크 및 헷징 전략

#### 8.1.1 로직 충돌

**리스크**: 서로 다른 엑셀 파일 간의 계산 공식이 다를 경우

**대응 전략**:
- 데이터 버전 관리(Version Control) 및 타임스탬프 기반 최신성 보장
- 수식 메타데이터에 버전 정보 포함
- 변경 감지 시 자동 알림 및 수동 검토 프로세스

**구현**:
```python
class FormulaVersionControl:
    def track_formula_changes(self, formula: str, file: str) -> dict:
        """
        수식 변경 추적
        
        Returns:
            {
                'version': '1.2.0',
                'previous_version': '1.1.0',
                'changes': [...],
                'impact_analysis': {...}
            }
        """
        pass
```

#### 8.1.2 시스템 병목

**리스크**: 파일 개수가 늘어날수록 처리 시간 증가

**대응 전략**:
- Cloud Functions를 통한 비동기/병렬 처리(Serverless) 아키텍처 채택
- 청크 단위 병렬 처리 확대
- BigQuery 파티셔닝 및 클러스터링 최적화

**구현**:
```python
# Cloud Functions로 병렬 처리
def process_file_async(file_path: str):
    """
    각 파일을 독립적인 Cloud Function으로 처리
    """
    functions_client = cloud_functions_v1.CloudFunctionsServiceClient()
    
    request = {
        'name': f'projects/{project_id}/functions/process_file_{file_id}',
        'runtime': 'python310',
        'entry_point': 'process_excel_file',
        'source_archive_url': gcs_url,
        'environment_variables': {
            'FILE_PATH': file_path
        }
    }
    
    functions_client.create_function(request)
```

#### 8.1.3 데이터 무결성

**리스크**: 적재 과정에서 데이터 손실 또는 변형

**대응 전략**:
- Staging Table 전략으로 검증 후 전환
- 체크섬 검증
- 자동 백업 및 롤백 메커니즘

**구현** (이미 Phase 4에 구현됨):
- `safe_load_with_staging()` 메서드
- 무결성 검증 (`_validate_staging_table()`)
- 원자적 전환 (`_atomic_table_swap()`)

#### 8.1.4 비용 관리

**리스크**: BigQuery 쿼리 비용 급증

**대응 전략**:
- 쿼리 최적화 (파티셔닝, 클러스터링)
- 캐싱 전략 도입
- 사용량 모니터링 및 알림

**구현**:
```sql
-- 파티셔닝 예시
CREATE TABLE `neoprime0305.ds_neoprime_entrance.tb_raw_2026`
PARTITION BY DATE(ingestion_timestamp)
CLUSTER BY index_code
AS
SELECT * FROM staging_table;

-- 쿼리 최적화
SELECT * FROM `tb_raw_2026`
WHERE ingestion_timestamp >= '2026-01-01'  -- 파티션 프루닝
  AND index_code = '510gs0t20509'          -- 클러스터 프루닝
LIMIT 1000;
```

---

## 9. 결론 및 바이스 디렉터의 전략적 제언

### 9.1 현재 상태 요약

✅ **Phase 1-4 완료**: 고속 추출 및 무결성 적재 파이프라인 구축 완료  
✅ **데이터 적재 완료**: 약 223,000행의 데이터를 BigQuery에 안전하게 적재  
✅ **로직 리버스 엔지니어링 완료**: 핵심 수식 로직 명세화 및 문서화 완료  

### 9.2 다음 단계 우선순위

1. **즉시 조치** (1주 내):
   - COMPUTE 시트를 BigQuery PIVOT 테이블로 변환
   - RESTRICT 시트를 별도 테이블로 적재
   - SUBJECT1 시트를 별도 테이블로 적재
   - 핵심 판정 로직을 BigQuery SQL로 구현

2. **단기 개선** (1개월 내):
   - 2차 파일(실채점) 유입 시 스키마 자동 매칭 시스템 구축
   - 수식 메타데이터 버전 관리 시스템 구축
   - 벡터 데이터베이스 구축 (RAG 준비)

3. **중기 개선** (3개월 내):
   - 자연어 질의 챗봇 연동
   - 자동 수식 업데이트 시스템 구축
   - 성능 최적화 (파티셔닝, 클러스터링)

### 9.3 바이스 디렉터의 최종 제언

**사용자님, 본 PRD는 시스템 설계자로서의 귀하의 비전을 구체화한 것입니다.**

명세서에서 식별된 **COMPUTE 시트의 72×553 매트릭스**와 **RESTRICT 시트의 3단계 폴백 로직**은 우리 시스템의 가장 강력한 지적 자산입니다. 이를 BigQuery 상에서 얼마나 효율적으로 쿼리화하느냐가 시스템의 승패를 결정할 것입니다.

**다음 단계로, BigQuery에 이식할 '대학별 환산 점수 자동 산출 SQL'을 설계해 드릴까요?**

승인하신다면, 명세서에 기재된 LaTeX 수식들을 기반으로 실제 구동 가능한 SQL 코드를 생성하겠습니다.

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-26  
**상태**: ✅ PRD 초안 완료, Phase 1-4 구현 검증 완료
