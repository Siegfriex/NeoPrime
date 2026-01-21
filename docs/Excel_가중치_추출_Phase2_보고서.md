# Excel 가중치 추출 Phase 2 보고서

**Version**: 1.0
**Date**: 2026-01-21
**Status**: In Progress
**Phase 1 참조**: `docs/Excel_가중치_추출_작업보고서.md`

---

## 목차

1. [Phase 2 개요](#1-phase-2-개요)
2. [Critical/High 리스크 수정](#2-criticalhigh-리스크-수정)
3. [구현 내용](#3-구현-내용)
4. [산출물](#4-산출물)
5. [검증 방법](#5-검증-방법)
6. [남은 작업](#6-남은-작업)

---

## 1. Phase 2 개요

### 1.1 목표

| 항목 | Phase 1 | Phase 2 |
|:-----|:--------|:--------|
| **대학 수** | 18개 (3.3%) | **550개 (100%)** |
| **xlwings 의존** | 런타임 필수 | **추출 시에만 사용** |
| **Parity Test** | Excel 값 복사 | **JSON 기반 독립 실행** |
| **탐구 과목명** | "탐구1", "탐구2" | **실제 과목명 지원** |

### 1.2 핵심 원칙

```
EXTRACT (추론 금지) | CONVERT (가정 금지) | VERIFY (100% 일치) | NO HALLUCINATION
```

---

## 2. Critical/High 리스크 수정

### 2.1 Critical: `rules.py:638` 무가중치 호출

**문제**: INDEX 조회 실패 시 `get_index_fallback()`을 가중치 없이 호출

**수정 전**:
```python
fallback = get_index_fallback()  # WeightNotProvidedError 발생
```

**수정 후**:
```python
logger.error("INDEX 조회 실패 - 폴백 비활성화 (가중치 미제공)")
index_result = {
    "found": False,
    "error": "INDEX 조회 실패, 폴백 비활성화됨",
    "match_type": "fallback_disabled",
    ...
}
```

**파일**: `theory_engine/rules.py:635-647`

### 2.2 High: `index_fallback.py:181,186` 숨은 기본값

**문제**: `.get(key, 0.2)` 및 `return 50.0`으로 숨겨진 폴백값 사용

**수정 전**:
```python
weight = self.weights.get(key, 0.2)  # 숨은 기본값
if total_weight == 0:
    return 50.0  # 숨은 폴백값
```

**수정 후**:
```python
if key not in self.weights:
    raise KeyError(f"가중치 키 '{key}' 미등록...")
weight = self.weights[key]

if total_weight == 0:
    raise ValueError("total_weight=0: 유효한 과목 가중치가 없습니다")
```

**파일**: `theory_engine/optimizers/index_fallback.py:175-199`

### 2.3 High: `index_calculator.py:127-128` 탐구 키 매핑

**문제**: `f"탐구{i+1}"` 키가 JSON에 없어서 조회 실패

**수정 전**:
```python
inquiry_conv = self.weights.get_converted_score(
    university, department, f"탐구{i+1}", score  # JSON에 없는 키
)
```

**수정 후**:
```python
# 실제 과목명으로 조회 (정규화 자동 적용)
inquiry_conv = self.weights.get_converted_score(
    university, department, subject_name, score  # "물리학 Ⅰ" 등
)
```

**파일**: `theory_engine/formulas/index_calculator.py:141-159`

---

## 3. 구현 내용

### 3.1 전체 대학 추출 스크립트

**파일**: `tools/extract_all_universities.py`

```python
class UniversityExtractor:
    """전체 대학 환산점수 추출기

    SUBJECT3 시트에서 모든 대학의 환산점수 테이블을 추출합니다.
    """

    def extract_all(self, use_xlwings=True) -> Dict:
        """xlwings COM으로 550개 대학 추출"""
        ...
```

**사용법**:
```bash
python tools/extract_all_universities.py
# 출력: theory_engine/weights/subject3_conversions_full.json
```

### 3.2 Ground Truth 수집 스크립트

**파일**: `tools/collect_ground_truth.py`

```python
class GroundTruthCollector:
    """Excel 실계산 기반 Ground Truth 수집기

    다양한 입력 조합에 대해 Excel이 계산한 결과를 수집합니다.
    """

    TEST_CASES = [
        {"name": "high_score_case1", "korean": 135, ...},
        {"name": "mid_score_case1", "korean": 120, ...},
        ...
    ]
```

**사용법**:
```bash
python tools/collect_ground_truth.py
# 출력: tests/fixtures/ground_truth.json
```

### 3.3 탐구 과목명 정규화

**파일**: `theory_engine/weights/extracted_weights.py`

```python
INQUIRY_SUBJECT_ALIASES = {
    "물리학 Ⅰ": ["물리학1", "물리1", "물리 I", ...],
    "화학 Ⅰ": ["화학1", "화학 I", ...],
    "생명과학 Ⅰ": ["생명과학1", "생명1", ...],
    ...
}

def normalize_inquiry_subject(subject: str) -> str:
    """탐구 과목명 정규화

    "물리학1" → "물리학 Ⅰ"
    """
    ...
```

### 3.4 IndexCalculator 실제 과목명 지원

**파일**: `theory_engine/formulas/index_calculator.py`

```python
def calculate(
    self,
    ...
    inquiry1_subject: str = "",  # Phase 2 추가
    inquiry2_subject: str = "",  # Phase 2 추가
) -> CalculationResult:
    """실제 과목명으로 환산점수 조회 (정규화 자동 적용)"""
    ...
```

### 3.5 독립 Parity Test

**파일**: `tests/test_excel_parity_standalone.py`

- xlwings 없이 실행 가능
- `ground_truth.json` 기반 검증
- 성공 기준: 90% 이상 통과

```bash
pytest tests/test_excel_parity_standalone.py -v
```

---

## 4. 산출물

### 4.1 신규 파일

| 파일 | 설명 |
|:-----|:-----|
| `tools/extract_all_universities.py` | 550개 대학 추출 스크립트 |
| `tools/collect_ground_truth.py` | Ground Truth 수집 스크립트 |
| `tests/test_excel_parity_standalone.py` | 독립 Parity Test |

### 4.2 예상 산출물 (스크립트 실행 후)

| 파일 | 설명 |
|:-----|:-----|
| `theory_engine/weights/subject3_conversions_full.json` | 550개 대학 환산점수 |
| `tests/fixtures/ground_truth.json` | Golden cases |

### 4.3 수정된 파일

| 파일 | 수정 내용 |
|:-----|:----------|
| `theory_engine/rules.py` | Line 635-647 폴백 비활성화 |
| `theory_engine/optimizers/index_fallback.py` | Line 175-199 숨은 기본값 제거 |
| `theory_engine/weights/extracted_weights.py` | 탐구 과목명 정규화 추가 |
| `theory_engine/formulas/index_calculator.py` | 실제 과목명 파라미터 추가 |
| `tests/test_excel_parity.py` | Phase 2 주석 추가 |
| `docs/Excel_가중치_추출_작업보고서.md` | Phase 2 참조 추가 |

---

## 5. 검증 방법

### 5.1 단계별 검증

```bash
# Step 0-A: Critical 수정 확인
python -c "from theory_engine.rules import compute_theory_result; print('OK')"

# Step 1: 대학 추출 확인 (스크립트 실행 후)
python -c "import json; d=json.load(open('theory_engine/weights/subject3_conversions_full.json',encoding='utf-8')); print(len(d['conversion_table']))"
# 예상: 500+

# Step 2: Ground Truth 확인 (스크립트 실행 후)
python -c "import json; d=json.load(open('tests/fixtures/ground_truth.json',encoding='utf-8')); print(len(d['ground_truth']))"

# Step 3-4: 환산점수 조회 확인
python -c "from theory_engine.weights.extracted_weights import normalize_inquiry_subject; print('Normalization OK')"

# Step 5: Parity Test 실행
pytest tests/test_excel_parity_standalone.py -v
# 예상: 90%+ PASSED
```

### 5.2 성공 기준

| 기준 | 목표 |
|:-----|:-----|
| Critical 리스크 수정 | 100% |
| 대학 환산점수 추출 | 500개 이상 |
| Ground Truth 생성 | 50개 이상 |
| Parity Test 통과율 | 90% 이상 |
| xlwings 런타임 의존 | 제거됨 |

---

## 6. 남은 작업

### 6.1 필수 (스크립트 실행 필요)

| 작업 | 명령어 | 상태 |
|:-----|:-------|:-----|
| 전체 대학 추출 | `python tools/extract_all_universities.py` | 대기 중 |
| Ground Truth 수집 | `python tools/collect_ground_truth.py` | 대기 중 |
| Parity Test 실행 | `pytest tests/test_excel_parity_standalone.py -v` | 대기 중 |

> **주의**: 위 스크립트는 Windows + Excel 설치 환경에서 1회 실행 필요

### 6.2 권장

- [ ] 추가 테스트 케이스 확장
- [ ] 에러 핸들링 강화
- [ ] 성능 최적화 (대량 추출 시)

---

## 부록: 금지 사항

```
 xlwings 런타임 사용 (추출/GT수집 시에만 허용)
 DEFAULT_WEIGHTS 부활
 추정/가정 기반 환산점수
 조용한 실패 (에러 시 명시적 예외)
 .get(key, default) 패턴으로 폴백값 숨기기
```

---

**작성자**: Claude Opus 4.5
**최종 업데이트**: 2026-01-21
