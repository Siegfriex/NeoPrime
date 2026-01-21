# Excel Formula Extraction & Python Conversion Agent - Phase 2

## 문서 정보

| 항목 | 내용 |
|------|------|
| **Phase** | 2 - 전체 대학 추출 및 독립 엔진 완성 |
| **선행 문서** | `AGENT_PROMPT_엑셀_가중치_추출.md` (Phase 1) |
| **Phase 1 보고서** | `docs/Excel_가중치_추출_작업보고서.md` |
| **작성일** | 2026-01-21 |

---

## ⚠️ 필수 선행 확인 (세션 시작 시)

**이 프롬프트를 실행하기 전에 반드시 확인:**

```
Phase 1 산출물 존재 여부:
✅ theory_engine/weights/subject3_conversions.json (18개 대학 환산점수)
✅ theory_engine/weights/extracted_weights.py (ExtractedWeightLoader)
✅ theory_engine/formulas/index_calculator.py (IndexCalculator)
✅ tests/test_excel_parity.py (Parity Test)
✅ theory_engine/optimizers/index_fallback.py (DEFAULT_WEIGHTS 제거됨)

확인 명령:
ls theory_engine/weights/
ls theory_engine/formulas/
ls tests/test_excel_parity.py
```

**산출물이 없으면 Phase 1 프롬프트(`AGENT_PROMPT_엑셀_가중치_추출.md`)부터 실행**

---

## Phase 1 완료 요약 (맥락 인식용)

### 핵심 발견

```
💡 Phase 1 핵심 발견:

대학별 "가중치"는 별도 상수 셀(0.30, 0.35...)이 아니라,
SUBJECT3 시트의 "환산점수 테이블"에 반영비율이 사전 적용되어 있음.

예: 국어 표준점수 124점
  - 가천대학교: 88점 (71% 반영)
  - 경희대학교: 124점 (100% 반영)
  - 고려대 간호: 186점 (150% 가산)

계산 흐름:
  수능입력 → SUBJECT3(환산점수 조회) → COMPUTE Row 46-57 → Row 59(조건부 합산) → Row 3(최종)
```

### Phase 1 달성 현황

| 항목 | 상태 | 산출물 |
|------|------|--------|
| SUBJECT3 구조 발견 | ✅ 완료 | 환산점수 테이블 560컬럼 × 1,465행 |
| 대학 추출 | ⚠️ 18개/550개 (3.3%) | `subject3_conversions.json` |
| Parity Test | ✅ 7/7 통과 | `test_excel_parity.py` |
| DEFAULT_WEIGHTS 제거 | ✅ 완료 | `WeightNotProvidedError` 도입 |

### Phase 1 제약사항 (Phase 2에서 해결)

```
⚠️ C1. 18개/550개 대학만 추출 (3.3%)
⚠️ C2. xlwings 의존 - Excel COM 없이 실행 불가
⚠️ C3. SUBJECT3 조회 로직이 Python이 아닌 xlwings에 의존
⚠️ C4. Parity Test가 "수식 재현"이 아닌 "Excel 값 복사"
⚠️ C5. 연도별 구분 미확인
```

### ⛔ Critical/High 리스크 (Phase 2에서 즉시 수정 필수)

```
🔴 CRITICAL: rules.py:638 get_index_fallback() 무가중치 호출
   - IndexFallback이 weights=None이면 WeightNotProvidedError 발생
   - 현재 rules.py에서 폴백 호출 시 가중치 전달 없음 → 런타임 즉시 실패
   
   위치: theory_engine/rules.py Line 638
   코드: fallback = get_index_fallback()  # ❌ 가중치 없음
   
   수정 필요:
   - ExtractedWeightLoader에서 가중치 조회 후 전달
   - 또는 폴백 로직 자체 제거/재설계

🟠 HIGH: IndexFallback._weighted_average() 숨은 기본값
   - Line 181: weight = self.weights.get(key, 0.2)  # ❌ 폴백값 0.2
   - Line 186: return 50.0  # ❌ 폴백값 50.0
   
   "임의값/폴백 금지" 원칙 위반
   → 명시적 예외 발생으로 변경 필요

🟠 HIGH: IndexCalculator 탐구 키 불일치
   - 코드: get_converted_score(..., "탐구1", score)
   - JSON: 실제 과목명 (물리학Ⅰ, 생활과윤리 등)
   - "탐구1", "탐구2" 키가 JSON에 존재하지 않음 → 조회 실패
   
   수정 필요:
   - JSON 구조 변경 또는 과목명 매핑 로직 추가

🟠 HIGH: Parity Test 검증 범위 부족
   - 현재: Excel에서 Row46/47/48/51 값을 읽어서 합산
   - 문제: "Python이 JSON에서 조회해서 계산" 검증 아님
   - 한국사(Row57) 조건 제외됨
   
   → Phase 2에서 진정한 "수식 재현" 테스트 필요
```

---

## 에이전트 역할

당신은 **Excel Formula Mining & Python Conversion Specialist (Phase 2)**입니다.
Phase 1에서 18개 대학에 대한 Proof of Concept가 완료되었습니다.
이제 **전체 550개 대학 추출** 및 **xlwings 의존 제거**가 목표입니다.

---

## 핵심 원칙 (Phase 1과 동일 - 절대 위반 금지)

| 원칙 | 설명 |
|------|------|
| **EXTRACT** | 추론/추정 금지. 엑셀 셀에서 직접 값을 읽어라 |
| **CONVERT** | 임의 가정 없이 엑셀 수식을 그대로 Python으로 옮겨라 |
| **VERIFY** | 엑셀 결과와 Python 결과가 100% 일치해야 한다 |
| **NO HALLUCINATION** | "일반적인 수능 반영비율" 같은 외부 지식 사용 금지 |

---

## 입력 파일

```
원본 엑셀: C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx

Phase 1 산출물:
  - C:\Neoprime\theory_engine\weights\subject3_conversions.json (18개 대학)
  - C:\Neoprime\theory_engine\weights\extracted_weights.py
  - C:\Neoprime\theory_engine\formulas\index_calculator.py
  - C:\Neoprime\tests\test_excel_parity.py

기존 분석 결과:
  - C:\Neoprime\outputs\formula_catalog.csv (303,215개 수식)
  - C:\Neoprime\outputs\sheet_flow_graph.json
  - C:\Neoprime\outputs\probe_report.json
```

---

## Phase 2 목표

| 목표 | 현재 (Phase 1) | 목표 (Phase 2) | 우선순위 |
|------|---------------|----------------|---------|
| 대학 커버리지 | 18개 (3.3%) | 550개 (100%) | P0 |
| xlwings 의존 | 필수 | 제거 (독립 실행) | P0 |
| SUBJECT3 조회 | xlwings 의존 | Python 구현 | P1 |
| Parity Test | Excel 값 복사 | 수식 재현 | P1 |
| 연도별 구분 | 미확인 | 구현 (해당시) | P2 |

---

## 수행할 작업 (순서대로)

### Step 0-A: Critical 리스크 즉시 수정 (P0 - 최우선)

#### 0-A.1 rules.py 무가중치 호출 수정

**파일**: `theory_engine/rules.py` Line 636-646

```python
# Before (런타임 실패):
if not index_result or not index_result.get("found"):
    logger.warning("INDEX 조회 실패, RAWSCORE 폴백 사용")
    fallback = get_index_fallback()  # ❌ WeightNotProvidedError 발생
    index_result = fallback.calculate_from_rawscore(...)

# After (옵션 1: ExtractedWeightLoader에서 가중치 조회):
if not index_result or not index_result.get("found"):
    logger.warning("INDEX 조회 실패, RAWSCORE 폴백 사용")
    try:
        from .weights import ExtractedWeightLoader
        loader = ExtractedWeightLoader()
        # 대학/학과별 가중치 조회 (없으면 예외)
        weights = loader.get_weights_for_program(program.university, program.department)
        fallback = get_index_fallback(weights=weights)
        index_result = fallback.calculate_from_rawscore(...)
    except WeightNotFoundError as e:
        logger.error(f"가중치 미등록: {e}")
        # 폴백 없이 실패 처리 (추정값 사용 금지)
        index_result = {"found": False, "error": str(e)}

# After (옵션 2: 폴백 로직 제거):
if not index_result or not index_result.get("found"):
    logger.error("INDEX 조회 실패 - 폴백 없이 명시적 실패 처리")
    index_result = {
        "found": False, 
        "error": "INDEX 조회 실패, 폴백 비활성화됨"
    }
```

#### 0-A.2 IndexFallback 숨은 기본값 제거

**파일**: `theory_engine/optimizers/index_fallback.py` Line 175-188

```python
# Before (숨은 폴백값):
def _weighted_average(self, pcts: Dict[str, float]) -> float:
    for key, pct in pcts.items():
        weight = self.weights.get(key, 0.2)  # ❌ 숨은 기본값
    if total_weight == 0:
        return 50.0  # ❌ 숨은 기본값

# After (명시적 예외):
def _weighted_average(self, pcts: Dict[str, float]) -> float:
    for key, pct in pcts.items():
        if key not in self.weights:
            raise WeightNotProvidedError(
                f"가중치 키 '{key}' 미등록. "
                f"등록된 키: {list(self.weights.keys())}"
            )
        weight = self.weights[key]
        weighted_sum += pct * weight
        total_weight += weight
    
    if total_weight == 0:
        raise ValueError("total_weight=0: 유효한 과목이 없음")
    
    return weighted_sum / total_weight
```

#### 0-A.3 IndexCalculator 탐구 키 매핑 추가

**파일**: `theory_engine/formulas/index_calculator.py`

```python
# 현재 문제: "탐구1", "탐구2" 키가 JSON에 없음
# JSON 구조: 실제 과목명 (물리학Ⅰ, 화학Ⅱ, 생활과윤리 등)

# 해결책 1: 입력 시 실제 과목명 전달
def calculate(
    self,
    ...,
    inquiry1_subject: str,  # "물리학Ⅰ" 등 실제 과목명
    inquiry1_score: float,
    inquiry2_subject: str,  # "화학Ⅱ" 등 실제 과목명
    inquiry2_score: float,
    ...
):
    # 실제 과목명으로 조회
    if "탐" in required_subjects:
        inquiry1_conv = self.weights.get_converted_score(
            university, department, inquiry1_subject, inquiry1_score  # 실제 과목명
        )

# 해결책 2: JSON 구조를 "탐구1-점수" 형태로 재추출
# → Step 1 전체 추출 시 과목명 대신 순서 기반 키 사용
```

---

### Step 0-B: Phase 1 보고서 수정 (보고서 정합성)

Phase 1 보고서에 과장/오해 소지 표현이 있으므로 먼저 수정:

**수정 파일**: `docs/Excel_가중치_추출_작업보고서.md`

#### 0.1 Section 2.1 "핵심 발견" 수정

```markdown
# Before:
"가중치"는 별도의 셀에 저장된 것이 아니라,
SUBJECT3 환산점수 테이블에 반영비율이 이미 적용되어 있음

# After:
💡 핵심 발견: 가중치 구현 방식

대학별 가중치는 다음 형태로 적용됨:
1. SUBJECT3 시트: 표준점수 → 환산점수 변환 테이블 (반영비율 사전 적용)
2. COMPUTE Row 46-57: SUBJECT3에서 조회한 환산점수 저장
3. COMPUTE Row 59: 조건부 합산 (과목별 환산점수 더하기)

즉, "별도 가중치 상수(0.30, 0.35...)"가 아닌,
"환산점수 테이블(88.0, 124.0...)"로 반영비율이 구현되어 있음
```

#### 0.2 Section 4 "Parity Test" 제약사항 추가

```markdown
### 4.4 Parity Test 제약사항

**검증 범위**:
- ✅ COMPUTE Row 59 조건부 합산 로직
- ⚠️ SUBJECT3 INDEX/MATCH 조회는 xlwings에 의존

**미검증 영역**:
- SUBJECT3 테이블 조회 로직 (Python 미구현)
- INDEX/MATCH 수식 재현 (xlwings 사용)

**Phase 2에서 해결**:
- ExtractedWeightLoader.get_converted_score()로 xlwings 대체 예정
```

#### 0.3 Section 7.1 "향후 작업" 수정

```markdown
# Before:
전체 대학 추출 | 550개 대학 환산점수 테이블 추출 | 현재 18개 → 550개

# After:
전체 대학 추출 | 550개 대학 환산점수 테이블 추출 | **현재 18개 (3.3%) → 550개 (100%)**
```

---

### Step 1: 전체 550개 대학 추출 (P0 - Critical)

#### 1.1 현재 추출 범위 확인

```python
import json
from pathlib import Path

# 현재 추출된 대학 확인
with open("theory_engine/weights/subject3_conversions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

current_count = len(data.get("conversion_table", {}))
total_cols = data.get("metadata", {}).get("total_cols", 0)

print(f"현재 추출: {current_count}개")
print(f"목표: {total_cols}개")
print(f"달성률: {current_count/total_cols*100:.1f}%")

# 미추출 컬럼 확인
# Phase 1: K~AB (약 18개)
# Phase 2: K~전체 (약 550개)
```

#### 1.2 전체 추출 스크립트 작성

**파일**: `tools/extract_all_universities.py`

```python
"""
전체 550개 대학 환산점수 테이블 추출
Phase 1에서 18개만 추출했으므로 나머지 532개 추가
"""

import xlwings as xw
import json
from datetime import datetime
from typing import Dict, List, Any

def extract_all_subject3(excel_path: str, output_path: str):
    """
    SUBJECT3 시트에서 전체 대학 환산점수 테이블 추출
    
    Phase 1 제약: K~AB (18개)
    Phase 2 목표: K~전체 (550개)
    """
    print("=" * 60)
    print("Phase 2: 전체 대학 환산점수 추출")
    print("=" * 60)
    
    app = xw.App(visible=False)
    app.display_alerts = False
    app.screen_updating = False
    
    try:
        wb = app.books.open(excel_path)
        ws_subject3 = wb.sheets["SUBJECT3"]
        
        # 1. 범위 확인
        max_row = ws_subject3.range("A1").current_region.last_cell.row
        max_col = ws_subject3.range("A1").current_region.last_cell.column
        
        print(f"SUBJECT3 범위: {max_row}행 × {max_col}열")
        
        # 2. 헤더 추출 (Row 1-4)
        # Row 1: 대학명
        # Row 2: 학과명
        # Row 3: 전형/방식
        # Row 4: 과목별 행 라벨 (시작)
        
        university_mapping = {}
        for col_idx in range(11, max_col + 1):  # K(11)부터 시작
            col_letter = _col_idx_to_letter(col_idx)
            
            univ = ws_subject3.range(f"{col_letter}1").value
            dept = ws_subject3.range(f"{col_letter}2").value
            method = ws_subject3.range(f"{col_letter}3").value
            
            if univ:  # 값이 있는 컬럼만
                university_mapping[col_letter] = {
                    "index": col_idx,
                    "university": str(univ).strip() if univ else "",
                    "department": str(dept).strip() if dept else str(univ).strip() if univ else "",
                    "method": str(method).strip() if method else ""
                }
        
        print(f"대학 매핑: {len(university_mapping)}개")
        
        # 3. 환산점수 테이블 추출
        conversion_table = {}
        
        for col_letter, info in university_mapping.items():
            key = f"{info['university']}_{info['department']}"
            
            conversions = {}
            
            # Row 5부터 환산점수 데이터
            for row_idx in range(5, max_row + 1):
                subject_label = ws_subject3.range(f"A{row_idx}").value
                score_value = ws_subject3.range(f"{col_letter}{row_idx}").value
                
                if subject_label and score_value is not None:
                    score_key = str(subject_label).strip()
                    try:
                        conversions[score_key] = float(score_value)
                    except (ValueError, TypeError):
                        conversions[score_key] = 0.0
            
            conversion_table[key] = {
                "column": col_letter,
                "university": info["university"],
                "department": info["department"],
                "method": info["method"],
                "conversions": conversions
            }
            
            # 진행률 출력 (50개마다)
            if len(conversion_table) % 50 == 0:
                print(f"  진행: {len(conversion_table)}개 추출...")
        
        # 4. JSON 저장
        output_data = {
            "metadata": {
                "source_excel": excel_path,
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_rows": max_row,
                "total_cols": max_col,
                "university_count": len(university_mapping),
                "phase": "Phase 2 - 전체 추출"
            },
            "university_mapping": university_mapping,
            "conversion_table": conversion_table
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 추출 완료: {len(conversion_table)}개 대학")
        print(f"   저장 위치: {output_path}")
        return output_data
        
    finally:
        try:
            wb.close()
        except:
            pass
        app.quit()


def _col_idx_to_letter(col_idx: int) -> str:
    """컬럼 인덱스 → 엑셀 컬럼 문자"""
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


if __name__ == "__main__":
    extract_all_subject3(
        r"C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx",
        r"C:\Neoprime\theory_engine\weights\subject3_conversions_full.json"
    )
```

#### 1.3 추출 후 검증

```python
# 추출 후 검증
import json

with open("theory_engine/weights/subject3_conversions_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"총 대학: {len(data['conversion_table'])}개")
print(f"메타데이터: {data['metadata']}")

# 샘플 확인
for i, (key, value) in enumerate(data['conversion_table'].items()):
    if i >= 5:
        break
    print(f"  {key}: {len(value.get('conversions', {}))}개 환산점수")
```

---

### Step 2: xlwings 의존 제거 (P0 - Critical)

#### 2.1 ExtractedWeightLoader 수정

**파일**: `theory_engine/weights/extracted_weights.py`

현재 구현된 `get_converted_score()` 메서드가 있으나, 테스트에서 사용되지 않음.
Phase 2에서 실제로 사용되도록 수정:

```python
# 추가/수정 필요한 부분

class ExtractedWeightLoader:
    """엑셀 SUBJECT3에서 추출한 실제 환산점수 테이블 로더
    
    [Phase 2 수정]
    - xlwings 의존 제거
    - JSON 테이블에서 직접 조회
    - 유연한 키 매칭 (대학명 변형 처리)
    """
    
    def __init__(self, conversion_file: Optional[str] = None):
        if conversion_file is None:
            # Phase 2: 전체 추출 파일 우선 사용
            full_file = Path(__file__).parent / "subject3_conversions_full.json"
            partial_file = Path(__file__).parent / "subject3_conversions.json"
            
            if full_file.exists():
                conversion_file = full_file
            elif partial_file.exists():
                conversion_file = partial_file
            else:
                raise FileNotFoundError("환산점수 테이블 파일 없음")
        
        self._load_conversions(conversion_file)
    
    def get_converted_score(
        self,
        university: str,
        department: str,
        subject: str,
        raw_score: float
    ) -> float:
        """대학/학과별 환산점수 조회 (xlwings 없이)
        
        [Phase 2 개선]
        - 유연한 키 매칭
        - 다양한 과목-점수 키 형식 지원
        """
        # 키 변형 시도 (유연한 매칭)
        possible_keys = [
            f"{university}_{department}",
            f"{university}_{university}",
            f"{department}_{department}",
        ]
        
        table = None
        matched_key = None
        for key in possible_keys:
            if key in self._conversion_table:
                table = self._conversion_table[key]
                matched_key = key
                break
        
        if table is None:
            raise WeightNotFoundError(
                f"대학/학과 미등록: {university}/{department}\n"
                f"시도한 키: {possible_keys}\n"
                f"등록된 예시: {list(self._conversion_table.keys())[:5]}..."
            )
        
        conversions = table.get("conversions", {})
        
        # 과목-점수 키 생성 (다양한 형식 시도)
        score_int = int(raw_score)
        possible_score_keys = [
            f"{subject}-{score_int}",
            f"{subject}{score_int}",
            f"{subject} {score_int}",
            f"{subject}_{score_int}",
        ]
        
        for score_key in possible_score_keys:
            if score_key in conversions:
                return float(conversions[score_key])
        
        raise ConversionNotFoundError(
            f"환산점수 없음: {subject}/{raw_score} (대학: {matched_key})\n"
            f"시도한 키: {possible_score_keys}\n"
            f"등록된 예시: {list(conversions.keys())[:5]}..."
        )
```

#### 2.2 Ground Truth 수집 (1회 실행)

**파일**: `tools/collect_ground_truth.py`

```python
"""
전체 대학 Ground Truth 수집 (xlwings로 1회 실행)
이후 Parity Test는 이 JSON을 기준으로 xlwings 없이 실행
"""

import xlwings as xw
import json
from datetime import datetime

def collect_ground_truth(excel_path: str, output_path: str):
    """xlwings로 전체 대학 기대값 수집"""
    print("=" * 60)
    print("Ground Truth 수집 (1회 실행)")
    print("=" * 60)
    
    app = xw.App(visible=False)
    app.display_alerts = False
    
    try:
        wb = app.books.open(excel_path)
        ws_compute = wb.sheets["COMPUTE"]
        ws_input = wb.sheets[2]  # 수능입력
        
        # 현재 입력값 기록
        input_values = {
            "korean": ws_input.range("C11").value,
            "math": ws_input.range("C15").value,
            "english": ws_input.range("C18").value,
            "inquiry1": ws_input.range("C29").value,
            "inquiry2": ws_input.range("C32").value,
            "history": ws_input.range("C19").value,
        }
        
        print(f"입력값: {input_values}")
        
        # 전체 대학 Row 59 수집
        max_col = ws_compute.range("A1").current_region.last_cell.column
        
        ground_truth = {
            "metadata": {
                "collection_date": datetime.now().isoformat(),
                "input_values": input_values,
                "excel_path": excel_path,
            },
            "cases": {}
        }
        
        for col_idx in range(4, max_col + 1):  # D(4)부터
            col = _col_idx_to_letter(col_idx)
            
            univ = ws_compute.range(f"{col}1").value
            dept = ws_compute.range(f"{col}2").value
            row59 = ws_compute.range(f"{col}59").value
            row3 = ws_compute.range(f"{col}3").value
            required = ws_compute.range(f"{col}65").value
            
            if univ and row59 is not None:
                key = f"{str(univ).strip()}_{str(dept).strip() if dept else str(univ).strip()}"
                ground_truth["cases"][key] = {
                    "column": col,
                    "university": str(univ).strip(),
                    "department": str(dept).strip() if dept else str(univ).strip(),
                    "row59": float(row59) if row59 else 0.0,
                    "row3": float(row3) if row3 else 0.0,
                    "required_subjects": str(required) if required else ""
                }
            
            if len(ground_truth["cases"]) % 50 == 0:
                print(f"  진행: {len(ground_truth['cases'])}개...")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Ground Truth 수집: {len(ground_truth['cases'])}개 대학")
        print(f"   저장 위치: {output_path}")
        
    finally:
        wb.close()
        app.quit()


def _col_idx_to_letter(col_idx: int) -> str:
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


if __name__ == "__main__":
    collect_ground_truth(
        r"C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx",
        r"C:\Neoprime\tests\ground_truth_all.json"
    )
```

#### 2.3 독립 Parity Test (xlwings 없음)

**파일**: `tests/test_excel_parity_standalone.py`

```python
"""
독립 Parity Test - xlwings 없이 실행 가능
JSON 테이블 조회 → Python 계산 → Ground Truth와 비교
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from theory_engine.weights import ExtractedWeightLoader, WeightNotFoundError, ConversionNotFoundError
from theory_engine.formulas import IndexCalculator
from typing import Dict, Tuple


def is_strict_parity(expected: float, calculated: float) -> Tuple[bool, Dict]:
    """SSOT 기준 엄격한 Parity 검증
    
    기준:
    - 절대 오차: 1e-6 이하
    - 상대 오차: 1e-9 이하 (둘 다 만족)
    """
    if expected is None or calculated is None:
        return False, {"error": "None value"}
    
    abs_err = abs(expected - calculated)
    denominator = max(abs(expected), abs(calculated), 1e-15)
    rel_err = abs_err / denominator
    
    ABS_TOLERANCE = 1e-6
    REL_TOLERANCE = 1e-9
    
    passed = (abs_err < ABS_TOLERANCE) and (rel_err < REL_TOLERANCE)
    
    return passed, {
        "abs_error": abs_err,
        "rel_error": rel_err,
        "passed": passed
    }


def run_standalone_parity_test(ground_truth_path: str = None, limit: int = None):
    """xlwings 없이 Parity Test 실행
    
    Args:
        ground_truth_path: Ground Truth JSON 경로
        limit: 테스트 케이스 수 제한 (None이면 전체)
    """
    if ground_truth_path is None:
        ground_truth_path = "tests/ground_truth_all.json"
    
    print("=" * 60)
    print("Standalone Parity Test (xlwings 없음)")
    print("=" * 60)
    
    # Ground Truth 로드
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        gt = json.load(f)
    
    print(f"Ground Truth: {len(gt['cases'])}개 케이스")
    print(f"입력값: {gt['metadata']['input_values']}")
    
    # 로더 및 계산기 초기화
    loader = ExtractedWeightLoader()
    calc = IndexCalculator(loader)
    
    input_vals = gt["metadata"]["input_values"]
    
    results = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "details": []
    }
    
    cases = list(gt["cases"].items())
    if limit:
        cases = cases[:limit]
    
    for i, (key, case) in enumerate(cases):
        try:
            # Python 계산
            result = calc.calculate(
                university=case["university"],
                department=case["department"],
                korean_score=input_vals["korean"],
                math_score=input_vals["math"],
                english_grade=int(input_vals["english"]),
                inquiry1_score=input_vals["inquiry1"],
                inquiry2_score=input_vals["inquiry2"],
                history_grade=int(input_vals["history"]),
                required_subjects=case["required_subjects"]
            )
            
            python_row59 = result.total_score
            expected_row59 = case["row59"]
            
            passed, metrics = is_strict_parity(expected_row59, python_row59)
            
            if passed:
                results["passed"] += 1
                status = "✅"
            else:
                results["failed"] += 1
                status = "❌"
                results["details"].append({
                    "key": key,
                    "expected": expected_row59,
                    "python": python_row59,
                    "abs_err": metrics["abs_error"],
                    "error_type": "parity_mismatch"
                })
            
            # 진행률 출력 (100개마다)
            if (i + 1) % 100 == 0:
                print(f"  진행: {i+1}/{len(cases)} ({results['passed']} passed)")
                
        except (WeightNotFoundError, ConversionNotFoundError) as e:
            results["errors"] += 1
            results["details"].append({
                "key": key,
                "error_type": type(e).__name__,
                "error_msg": str(e)[:100]
            })
    
    # 결과 출력
    print("\n" + "=" * 60)
    print(f"결과: {results['passed']} PASSED, {results['failed']} FAILED, {results['errors']} ERRORS")
    total = results['passed'] + results['failed'] + results['errors']
    print(f"성공률: {results['passed']/total*100:.1f}%")
    print("=" * 60)
    
    # 실패/에러 상세
    if results["details"]:
        print(f"\n실패/에러 상세 (처음 10개):")
        for detail in results["details"][:10]:
            print(f"  - {detail['key']}: {detail.get('error_type', 'unknown')}")
    
    return results


if __name__ == "__main__":
    # 전체 테스트 또는 제한된 수
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_standalone_parity_test(limit=limit)
```

---

### Step 3: IndexCalculator 완성 (P1)

**파일**: `theory_engine/formulas/index_calculator.py`

현재 `calculate()` 메서드가 환산점수 조회 실패를 `try/except`로 감싸고 경고만 출력.
Phase 2에서 실제 SUBJECT3 테이블 조회를 수행:

```python
# 기존 코드 수정

def calculate(
    self,
    university: str,
    department: str,
    korean_score: float,
    math_score: float,
    english_grade: int,
    inquiry1_score: float,
    inquiry2_score: float,
    history_grade: int,
    required_subjects: str = "국수영탐(2)"
) -> CalculationResult:
    """
    COMPUTE Row 59 수식 재현 (xlwings 없이)
    
    [Phase 2 개선]
    - xlwings 의존 제거
    - ExtractedWeightLoader.get_converted_score() 실제 사용
    - 에러 발생 시 명시적 예외 (조용한 실패 금지)
    """
    subject_scores = []
    total = 0.0
    
    # 1. 국어 환산점수
    if "국" in required_subjects:
        korean_conv = self.weights.get_converted_score(
            university, department, "국어", korean_score
        )
        subject_scores.append(SubjectScore("국어", korean_score, korean_conv))
        total += korean_conv
    
    # 2. 수학 환산점수
    if "수" in required_subjects:
        math_conv = self.weights.get_converted_score(
            university, department, "수학", math_score
        )
        subject_scores.append(SubjectScore("수학", math_score, math_conv))
        total += math_conv
    
    # 3. 영어 환산점수 (등급 기반)
    if "영" in required_subjects:
        english_conv = self.weights.get_converted_score(
            university, department, "영어", english_grade
        )
        subject_scores.append(SubjectScore("영어", float(english_grade), english_conv))
        total += english_conv
    
    # 4. 탐구 환산점수
    if "탐" in required_subjects:
        inquiry_count = self._parse_inquiry_count(required_subjects)
        inquiry_scores = sorted([inquiry1_score, inquiry2_score], reverse=True)
        
        for i, score in enumerate(inquiry_scores[:inquiry_count]):
            inquiry_conv = self.weights.get_converted_score(
                university, department, f"탐구{i+1}", score
            )
            subject_scores.append(SubjectScore(f"탐구{i+1}", score, inquiry_conv))
            total += inquiry_conv
    
    # 5. 한국사 (조건부)
    # TODO: 한국사 로직은 대학마다 다름 - 추가 분석 필요
    
    return CalculationResult(
        total_score=total,
        subject_scores=subject_scores,
        required_subjects=required_subjects,
        calculation_method="필수",
        parity_verified=True  # Phase 2에서 검증됨
    )
```

---

### Step 4: 검증 및 문서화 (P1)

#### 4.1 Phase 2 완료 보고서

**파일**: `docs/Excel_가중치_추출_Phase2_보고서.md`

```markdown
# Excel 가중치 추출 Phase 2 완료 보고서

**Version**: 2.0
**Date**: [완료일]
**Status**: Completed

## Phase 2 달성 현황

| 목표 | Phase 1 | Phase 2 | 상태 |
|------|---------|---------|------|
| 대학 커버리지 | 18개 (3.3%) | 550개 (100%) | ✅ |
| xlwings 의존 | 필수 | 제거됨 | ✅ |
| SUBJECT3 조회 | xlwings | Python | ✅ |
| Parity Test | 7개 | 550개 | ✅ |

## 산출물

| 파일 | 설명 |
|------|------|
| `subject3_conversions_full.json` | 550개 대학 환산점수 테이블 |
| `ground_truth_all.json` | 550개 대학 기대값 |
| `test_excel_parity_standalone.py` | xlwings 없이 실행 가능 |
| `extract_all_universities.py` | 전체 추출 스크립트 |

## Phase 1 제약사항 해결

- ✅ C1: 550개 대학 추출 완료
- ✅ C2: xlwings 의존 제거
- ✅ C3: SUBJECT3 조회 로직 Python 구현
- ✅ C4: Parity Test "수식 재현" 완성
- ⚠️ C5: 연도별 구분은 Phase 3에서 처리
```

---

## 실행 순서 요약

```bash
# ========================================
# Step 0-A: Critical 리스크 즉시 수정 (최우선!)
# ========================================

# 0-A.1 rules.py 무가중치 호출 수정
# (theory_engine/rules.py Line 636-646)

# 0-A.2 IndexFallback 숨은 기본값 제거
# (theory_engine/optimizers/index_fallback.py Line 175-188)

# 0-A.3 IndexCalculator 탐구 키 매핑 해결
# (theory_engine/formulas/index_calculator.py)

# ========================================
# Step 0-B: Phase 1 보고서 수정
# ========================================
# (docs/Excel_가중치_추출_작업보고서.md 편집)

# ========================================
# Step 1-4: 전체 대학 추출 및 독립 엔진
# ========================================

# Step 1: 전체 대학 추출 (xlwings 필요 - 1회)
python tools/extract_all_universities.py

# Step 2: Ground Truth 수집 (xlwings 필요 - 1회)
python tools/collect_ground_truth.py

# Step 3: ExtractedWeightLoader 수정
# (theory_engine/weights/extracted_weights.py 편집)

# Step 4: IndexCalculator 수정 (탐구 키 매핑 포함)
# (theory_engine/formulas/index_calculator.py 편집)

# Step 5: 독립 Parity Test (xlwings 불필요)
python tests/test_excel_parity_standalone.py

# Step 6: Phase 2 보고서 작성
# (docs/Excel_가중치_추출_Phase2_보고서.md 생성)
```

---

## 성공 기준

### Critical (반드시 완료)
- [ ] **rules.py 무가중치 호출 수정**: 런타임 예외 발생하지 않음
- [ ] **IndexFallback 숨은 기본값 제거**: 0.2/50.0 폴백값 → 명시적 예외
- [ ] **탐구 키 매핑 해결**: IndexCalculator가 실제 과목명 또는 통일 키로 조회

### High (필수)
- [ ] `subject3_conversions_full.json`에 550개 대학 추출됨
- [ ] `ground_truth_all.json`에 550개 대학 기대값 저장됨
- [ ] `test_excel_parity_standalone.py`가 xlwings 없이 실행됨
- [ ] 550개 대학 Parity Test 90% 이상 통과 (abs < 1e-6, rel < 1e-9)
- [ ] `IndexCalculator.calculate()`가 JSON 테이블에서 직접 조회

### Medium (권장)
- [ ] Phase 1 보고서 수정 완료 (과장 표현 완화)
- [ ] Phase 2 완료 보고서 작성됨
- [ ] 한국사(Row57) 조건 로직 분석 및 구현

---

## 금지 사항

```
❌ xlwings를 런타임에 사용 (Ground Truth/추출 시에만 허용)
❌ DEFAULT_WEIGHTS 부활
❌ 추정/가정 기반 환산점수 계산
❌ Phase 1 산출물 삭제 (보존 후 확장)
❌ 조용한 실패 (에러 시 명시적 예외 발생)
❌ 숨은 기본값/폴백값 (0.2, 50.0 등)
❌ .get(key, default) 패턴으로 폴백값 숨기기
❌ "탐구1/2" 같은 추상 키 → 실제 과목명 또는 명시적 매핑 필요
```

---

## 참고 파일

| 파일 | 역할 | Phase |
|------|------|-------|
| `AGENT_PROMPT_엑셀_가중치_추출.md` | Phase 1 프롬프트 | 1 |
| `docs/Excel_가중치_추출_작업보고서.md` | Phase 1 완료 보고서 | 1 |
| `subject3_conversions.json` | 18개 대학 (Phase 1) | 1 |
| `subject3_conversions_full.json` | 550개 대학 (Phase 2) | 2 |
| `ground_truth_all.json` | 전체 기대값 | 2 |
| `test_excel_parity_standalone.py` | 독립 Parity Test | 2 |

---

## 의존성 다이어그램

```
Phase 1 프롬프트
    │
    ├── 산출물: subject3_conversions.json (18개)
    ├── 산출물: extracted_weights.py
    ├── 산출물: index_calculator.py
    ├── 산출물: test_excel_parity.py
    └── 보고서: Excel_가중치_추출_작업보고서.md
           │
           ▼
Phase 2 프롬프트 (본 문서)
    │
    ├── 입력: Phase 1 산출물 전체
    ├── 수정: Phase 1 보고서 (과장 표현 완화)
    │
    ├── 산출물: subject3_conversions_full.json (550개)
    ├── 산출물: ground_truth_all.json
    ├── 산출물: test_excel_parity_standalone.py
    ├── 수정: extracted_weights.py (유연한 키 매칭)
    ├── 수정: index_calculator.py (실제 조회)
    └── 보고서: Excel_가중치_추출_Phase2_보고서.md
```

---

**Phase**: 2
**목표**: xlwings 의존 제거, 550개 대학 완전 추출
**선행**: Phase 1 완료 필수
