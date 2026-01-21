# Excel Formula Extraction & Python Conversion Agent - Phase 1

## 문서 정보

| 항목 | 내용 |
|------|------|
| **Phase** | 1 - 구조 파악 및 18개 대학 PoC |
| **후속 문서** | `AGENT_PROMPT_Phase2_전체대학추출.md` |
| **작성일** | 2026-01-21 |

---

## 에이전트 역할
당신은 **Excel Formula Mining & Python Conversion Specialist (Phase 1)**입니다.
입시 예측 엑셀 워크북의 모든 수식, 가중치, 휴리스틱을 **추출**하여 
동등한 Python 코드로 **변환**하는 것이 유일한 목표입니다.

---

## 핵심 원칙 (절대 위반 금지)

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
기존 분석 결과 (참고용):
  - C:\Neoprime\outputs\formula_catalog.csv
  - C:\Neoprime\outputs\sheet_flow_graph.json
  - C:\Neoprime\outputs\probe_report.json
```

---

## 수행할 작업 (순서대로)

### Phase 1: 구조 파악 (Read-Only)

#### 1.1 시트 목록 및 역할 식별
```python
import openpyxl
wb = openpyxl.load_workbook(excel_path, data_only=False)
for sheet_name in wb.sheetnames:
    print(f"Sheet: {sheet_name}, Rows: {ws.max_row}, Cols: {ws.max_column}")
```

**확인할 시트:**
- `RAWSCORE`: 원점수 입력
- `INDEX`: 과목별 지수 계산
- `PERCENTAGE`: 백분위/커트라인
- `COMPUTE`: 최종 점수 계산 (가중치 적용)
- `RESTRICT`: 결격 조건
- `SUBJECT*`: 과목 관련 참조 테이블

#### 1.2 헤더 구조 분석
- 행 헤더: 대학명, 학과명이 어느 행/열에 있는지
- 열 헤더: 과목명, 연도가 어디에 있는지
- Named Range 목록

---

### Phase 2: 가중치 셀 위치 식별 (검증 기반 - 추정 금지)

#### 2.1 상수 참조 셀 후보 추출 (catalog 기반)
**절대 특정 좌표를 가정하지 마라.** 대신 `formula_catalog.csv`에서 자동 식별:

```python
import pandas as pd
import ast  # 보안: eval() 대신 ast.literal_eval() 사용
from collections import Counter

# 수식에서 참조되는 셀 주소 빈도 분석
df = pd.read_csv("outputs/formula_catalog.csv")
all_refs = []
for refs in df["cell_refs"].dropna():
    # 보안: eval()은 임의 코드 실행 위험 → ast.literal_eval() 사용
    try:
        parsed = ast.literal_eval(refs)
        if isinstance(parsed, list):
            all_refs.extend(parsed)
    except (ValueError, SyntaxError):
        continue  # 파싱 불가능한 경우 스킵

# 가장 많이 참조되는 셀 Top-50 (상수/파라미터 후보)
ref_counts = Counter(all_refs).most_common(50)
print("=== 가중치 후보 셀 (참조 빈도 Top-50) ===")
for ref, count in ref_counts:
    print(f"  {ref}: {count}회 참조")
```

#### 2.2 후보 셀의 컨텍스트 검증 (행/열 헤더 확인)
```python
# 후보 셀의 행 라벨, 열 헤더를 읽어 "이게 진짜 가중치인지" 확인
candidate_cells = [ref for ref, _ in ref_counts[:20]]

for cell_ref in candidate_cells:
    sheet_name, col, row = parse_cell_ref(cell_ref)  # 예: "COMPUTE!$C$2"
    ws = wb[sheet_name]
    
    # 해당 셀의 값
    value = ws.cell(row=row, column=col).value
    
    # 행 라벨 (A열 또는 첫 열)
    row_label = ws.cell(row=row, column=1).value
    
    # 열 헤더 (1행 또는 헤더 행)
    col_header = ws.cell(row=1, column=col).value
    
    print(f"{cell_ref}: value={value}, row_label={row_label}, col_header={col_header}")
```

#### 2.3 Parity Test로 가중치 확정 (abs+rel 엄격 기준)

**⚠️ 중요**: `openpyxl(data_only=True)`는 "저장된 캐시 값"이라 부정확할 수 있음!
**expected value는 반드시 xlwings(Excel COM)로 실시간 계산 결과를 사용**

```python
import xlwings as xw

# ❌ openpyxl(data_only=True) 사용 금지 - 캐시값이라 오래되거나 비어있을 수 있음
# ✅ xlwings로 Excel에서 실시간 계산된 값 읽기
app = xw.App(visible=False)
wb = app.books.open(excel_path)
wb.app.calculate()  # 강제 재계산
expected_value = wb.sheets["COMPUTE"].range("J3").value  # 예시 출력 셀
wb.close()
app.quit()

# 후보 가중치로 Python 계산
calculated_value = compute_with_weights(candidate_weights, input_scores)

# abs + rel 동시 기준 (엄격한 100% Parity)
# 0.01% 상대오차는 600점대에서 0.06점 차이도 통과 → 너무 느슨!
def is_strict_parity(expected: float, calculated: float) -> tuple[bool, dict]:
    """
    엄격한 Parity 검증: abs + rel 동시 만족 필요
    
    기준:
    - 절대 오차: 1e-6 이하 (0.000001)
    - 상대 오차: 1e-9 이하 (0.0000001%)
    
    예외: ROUND/표시용 셀은 abs 1e-3까지 허용 (별도 표시)
    """
    abs_err = abs(expected - calculated)
    rel_err = abs_err / max(abs(expected), abs(calculated), 1e-15)
    
    # 엄격 기준
    ABS_TOLERANCE = 1e-6
    REL_TOLERANCE = 1e-9
    
    passed = (abs_err < ABS_TOLERANCE) and (rel_err < REL_TOLERANCE)
    
    return passed, {
        "abs_error": abs_err,
        "rel_error": rel_err,
        "abs_threshold": ABS_TOLERANCE,
        "rel_threshold": REL_TOLERANCE,
        "passed": passed
    }

# 일치 여부로 "진짜 가중치" 확정
passed, metrics = is_strict_parity(expected_value, calculated_value)
if passed:
    print(f"✅ 100% Parity 달성!")
    print(f"   abs_err={metrics['abs_error']:.2e}, rel_err={metrics['rel_error']:.2e}")
    save_weights_to_json(candidate_weights)
else:
    print(f"❌ Parity 실패: expected={expected_value}, calculated={calculated_value}")
    print(f"   abs_err={metrics['abs_error']:.2e} (허용: {metrics['abs_threshold']:.0e})")
    print(f"   rel_err={metrics['rel_error']:.2e} (허용: {metrics['rel_threshold']:.0e})")
    print("→ 수식 파싱 오류 또는 가중치 오류 확인 필요")
```

#### 2.4 출력 형식 (검증 후 생성)
```json
// weights_by_program.json - 검증된 가중치만 저장
{
  "metadata": {
    "source_excel": "202511고속성장분석기(가채점)20251114.xlsx",
    "extraction_date": "2026-01-21",
    "parity_test_passed": true,
    "verified_cells": ["COMPUTE!C2", "COMPUTE!D2", ...]
  },
  "programs": {
    "서울대_의예_2025": {
      "weights": {
        "korean": 0.30,
        "math": 0.35,
        "english": 0.10,
        "inquiry1": 0.125,
        "inquiry2": 0.125
      },
      "source_cells": {
        "korean": "COMPUTE!C5",
        "math": "COMPUTE!D5"
      },
      "parity_verified": true
    }
  }
}
```

**중요**: 위 예시의 숫자는 실제 추출 전까지 플레이스홀더임. 실제 값은 엑셀에서 읽어야 함.

---

### Phase 3: 수식 변환 (Critical)

#### 3.1 수식 파싱 규칙

| Excel 함수 | Python 변환 |
|------------|-------------|
| `=A1+B1` | `a1 + b1` |
| `=SUMPRODUCT(A1:A5, B1:B5)` | `np.dot(a, b)` |
| `=IF(A1>B1, C1, D1)` | `c1 if a1 > b1 else d1` |
| `=IFS(cond1, val1, cond2, val2)` | `if cond1: val1 elif cond2: val2` |
| `=IFERROR(expr, fallback)` | `try: expr except: fallback` |
| `=VLOOKUP(key, range, col, 0)` | `lookup_dict.get(key)` |
| `=INDEX(range, MATCH(...))` | `df.loc[...]` 또는 `dict[key]` |
| `=FIND("국", A1)` | `"국" in a1` |

#### 3.2 조건부 로직 추출
`RESTRICT` 시트에서 결격 조건:
```python
# Excel: =IF(AND(FIND("의",B2)>0, C5<2), "결격", "통과")
# Python:
def check_medical_restriction(major: str, inquiry_count: int) -> bool:
    if "의" in major and inquiry_count < 2:
        return True  # 결격
    return False
```

---

### Phase 4: Python 모듈 생성

#### 4.1 가중치 로더 (Fallback 제거, 명시적 오류)
```python
# theory_engine/weights/extracted_weights.py

import json
from pathlib import Path
from typing import Dict, Optional

class WeightNotFoundError(Exception):
    """가중치 미등록 오류 - Fallback 사용 금지, 명시적 오류 발생"""
    pass

class ExtractedWeightLoader:
    """엑셀에서 추출한 실제 가중치 로더
    
    중요: DEFAULT_WEIGHTS 같은 임의 폴백 사용 금지!
    가중치가 없으면 명시적으로 WeightNotFoundError 발생
    """
    
    def __init__(self):
        weight_file = Path(__file__).parent / "weights_by_program.json"
        with open(weight_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._weights = data.get("programs", {})
            self._metadata = data.get("metadata", {})
    
    def get_weights(self, university: str, major: str, year: int) -> dict:
        """대학/학과/연도별 실제 가중치 반환
        
        Args:
            university: 대학명 (예: "서울대")
            major: 학과명 (예: "의예")
            year: 연도 (예: 2025)
        
        Returns:
            가중치 딕셔너리 {"korean": 0.3, "math": 0.35, ...}
        
        Raises:
            WeightNotFoundError: 가중치가 등록되지 않은 경우
                                 (절대 임의 값 반환 금지!)
        """
        key = f"{university}_{major}_{year}"
        
        if key in self._weights:
            return self._weights[key]["weights"]
        
        # 연도 없이 검색
        key_no_year = f"{university}_{major}"
        for k, v in self._weights.items():
            if k.startswith(key_no_year):
                return v["weights"]
        
        # ❌ 절대 DEFAULT_WEIGHTS 사용 금지!
        # ❌ weights.get(key, DEFAULT) 금지!
        raise WeightNotFoundError(
            f"가중치 미등록: {key}\n"
            f"해결 방법:\n"
            f"  1. 엑셀에서 해당 대학/학과 가중치 추출 필요\n"
            f"  2. weights_by_program.json에 추가 필요\n"
            f"  3. 임의 가정/추정 절대 금지"
        )
    
    def list_available_programs(self) -> list:
        """등록된 프로그램 목록 반환"""
        return list(self._weights.keys())
    
    def get_metadata(self) -> dict:
        """추출 메타데이터 반환 (출처, 날짜, 검증 결과)"""
        return self._metadata
```

#### 4.2 수식 실행기
```python
# theory_engine/formulas/index_calculator.py

class IndexCalculator:
    """INDEX 시트 계산 로직 (엑셀에서 추출)"""
    
    def __init__(self, weight_loader: ExtractedWeightLoader):
        self.weights = weight_loader
    
    def calculate(self, university: str, major: str, year: int,
                  korean: float, math: float, english: float,
                  inquiry1: float, inquiry2: float) -> float:
        """
        엑셀 수식 패턴: =BF46*("국" 토큰) + BF47*("수" 토큰) + ...
        ⚠️ 과목 매핑은 컨텍스트(헤더/라벨)로 최종 확정 필요
        """
        w = self.weights.get_weights(university, major, year)
        
        result = (
            w["korean"] * korean +
            w["math"] * math +
            w["english"] * english +
            w["inquiry1"] * inquiry1 +
            w["inquiry2"] * inquiry2
        )
        return result
```

---

### Phase 5: 검증

#### 5.1 단위 검증
```python
# tests/test_excel_parity.py

def test_single_cell_parity():
    """특정 셀 계산 결과가 엑셀과 일치하는지 검증"""
    # 엑셀에서 직접 읽은 기대값
    excel_result = 87.35  # 예: INDEX!BF59의 실제 값
    
    # Python 계산
    calc = IndexCalculator(ExtractedWeightLoader())
    python_result = calc.calculate(
        university="서울대", major="의예", year=2025,
        korean=95, math=98, english=1, inquiry1=90, inquiry2=92
    )
    
    assert abs(excel_result - python_result) < 0.001, \
        f"불일치: Excel={excel_result}, Python={python_result}"
```

#### 5.2 배치 검증
```python
def test_batch_parity():
    """샘플 20건에 대해 엑셀 결과와 Python 결과 비교"""
    test_cases = load_test_cases("test_data/sample_students.csv")
    
    mismatches = []
    for case in test_cases:
        excel_val = case["excel_result"]
        python_val = engine.compute(case["input"])
        
        if abs(excel_val - python_val) > 0.001:
            mismatches.append({
                "input": case["input"],
                "excel": excel_val,
                "python": python_val,
                "diff": abs(excel_val - python_val)
            })
    
    assert len(mismatches) == 0, f"불일치 {len(mismatches)}건: {mismatches}"
```

---

## 출력물 체크리스트

| 파일 | 설명 | 필수 |
|------|------|------|
| `theory_engine/weights/weights_by_university.json` | 대학별 가중치 | ✅ |
| `theory_engine/weights/extracted_weights.py` | 가중치 로더 | ✅ |
| `theory_engine/formulas/index_calculator.py` | INDEX 계산 | ✅ |
| `theory_engine/formulas/percentage_calculator.py` | PERCENTAGE 계산 | ✅ |
| `theory_engine/formulas/compute_calculator.py` | COMPUTE 계산 | ✅ |
| `theory_engine/rules/extracted_restrictions.py` | 결격 조건 | ✅ |
| `tests/test_excel_parity.py` | 일치 검증 | ✅ |
| `docs/extraction_report.md` | 추출 보고서 | ✅ |

---

## 금지 사항 (위반 시 실패)

```
❌ DEFAULT_WEIGHTS = {"korean": 0.28, ...}  # 하드코딩 금지
❌ "일반적으로 국어는 30% 반영"  # 외부 지식 금지
❌ weights.get(key, DEFAULT)  # 폴백 상수 금지
❌ 가중치를 "추정"하거나 "가정"  # 추론 금지
```

---

## 가중치 정의 (Critical - 오해 방지)

```
⚠️ "가중치"란 무엇인가?

정의: Parity Test를 통과한 파라미터 집합
     (Excel 최종 출력과 100% 일치하는 Python 계산에 사용되는 값)

주의사항:
1. 합=1 강제 금지
   - 추출된 값이 0.3, 0.35, 0.1, 0.125, 0.125 라면 그대로 사용
   - "합이 1이 되어야 한다"는 가정으로 정규화하지 마라
   - Excel이 실제로 정규화하는지는 수식 분석으로 확인

2. 원시 계수 vs 정규화된 가중치
   - BF46 등이 "원시 계수"이고 다른 셀에서 정규화될 수 있음
   - 예: 실제 가중치 = BF46 / (BF46+BF47+BF48+BF51+BF57)
   - → Parity Test로 "어느 값이 최종 기여도인지" 검증

3. 조건부 가중치
   - 동일 대학/학과라도 조건(전형/계열)에 따라 가중치가 다를 수 있음
   - 예: 수시 vs 정시, 자연계열 vs 인문계열
   - → 조건별로 별도 파라미터 세트 추출

검증 기준:
  가중치 W가 올바르면:
  Excel_result == Python_compute(inputs, W)  # Parity 만족
  (abs_err < 1e-6 AND rel_err < 1e-9)
```

---

## 위험 완화 체크리스트 (필수 수행)

### 사전 검증 (Step 0에서 반드시 확인)

| 체크 | 위험 요인 | 완화 전략 | 검증 방법 |
|------|----------|----------|----------|
| ☐ | **OFFSET 동적 참조 (2,200회)** | xlwings Excel COM 필수 사용 | probe_report.txt에서 OFFSET 사용 셀 목록 확인 |
| ☐ | **순환 참조** | 위상정렬 + max_depth=100 제한 | dependency_closure에서 사이클 감지 로직 |
| ☐ | **부동소수점 오차** | abs+rel 동시 기준 (엄격) | `abs(a-b) < 1e-6 AND rel_err < 1e-9` |
| ☐ | **숨겨진 시트/셀** | openpyxl hidden 속성 확인 | `ws.sheet_state`, `ws.column_dimensions[col].hidden` |
| ☐ | **VBA 매크로** | 배열수식/VBA 존재 시 경고 | probe_report: 현재 0개 (안전) |

### OFFSET 동적 참조 처리 (Critical)

OFFSET 함수는 참조 범위가 런타임에 결정되므로 정적 분석 불가:

```python
# OFFSET 사용 셀 식별
import pandas as pd
df = pd.read_csv("outputs/formula_catalog.csv")
offset_cells = df[df["effective_formula"].str.contains("OFFSET", na=False)]
print(f"OFFSET 사용 셀: {len(offset_cells)}개")

# OFFSET 셀이 가중치에 영향을 주는지 확인
# 영향 있으면 → xlwings 필수
# 영향 없으면 → openpyxl로 진행 가능
```

### 숨겨진 시트/셀 확인

```python
from openpyxl import load_workbook

wb = load_workbook(excel_path, data_only=False)
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    if ws.sheet_state == 'hidden':
        print(f"⚠️ 숨겨진 시트 발견: {sheet_name}")
    
    # 숨겨진 열 확인
    for col_letter, col_dim in ws.column_dimensions.items():
        if col_dim.hidden:
            print(f"⚠️ 숨겨진 열: {sheet_name}!{col_letter}")
```

### 순환 참조 감지

```python
def detect_cycles(dependency_graph: dict) -> list:
    """순환 참조 감지"""
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        if node in rec_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in dependency_graph.get(node, []):
            dfs(neighbor, path.copy())
        
        rec_stack.remove(node)
    
    for node in dependency_graph:
        dfs(node, [])
    
    return cycles
```

---

## 시작 명령 (검증 기반 순서)

```
Step 0: 사전 검증 및 가중치 후보 자동 식별 (Critical)

  [0-1] 위험 요인 확인 (위험 완화 체크리스트 참조)
    - probe_report.txt 재확인: OFFSET 2,200회, VBA 0개
    - 숨겨진 시트/셀 존재 여부 확인
    - OFFSET 사용 셀이 가중치에 영향 주는지 판단
    
  [0-2] 기존 산출물에서 가중치 패턴 자동 추출 (★ 핵심)
    
    ⚠️ 중요: 58-62행은 "합산 구조"이지 가중치 저장소가 아님!
    실제 가중치는 곱셈 계수로 등장하는 셀 (예: BF46, BF47, BF48, BF51, BF57)
    
    # 실제 가중치 수식 예시 (formula_catalog.csv에서 확인됨):
    # =BF46*IFERROR(FIND("국",BF65)/FIND("국",BF65),0)
    #  +BF47*IFERROR(FIND("수",BF65)/FIND("수",BF65),0)
    #  +BF48*IFERROR(FIND("영",BF65)/FIND("영",BF65),0)
    #  +BF51*IFERROR(FIND("탐",BF65)/FIND("탐",BF65),0)+...
    # → BF46("국" 토큰), BF47("수" 토큰), BF48("영" 토큰), BF51("탐" 토큰), BF57("한" 토큰)
    # ⚠️ 주의: 위 매핑은 FIND() 패턴 기반 추정임. 컨텍스트(헤더/라벨)로 최종 확정 필요!
    #    예: "한"이 한국사/한문/대체영역 중 무엇인지는 행 라벨 확인 필수
    
    import pandas as pd
    import ast
    import re
    from collections import Counter
    
    df = pd.read_csv("outputs/formula_catalog.csv")
    
    # ⚠️ INDEX 시트로 스코프 제한 (노이즈 방지)
    index_df = df[df["sheet_name"] == "INDEX"]
    
    # 방법 1: 곱셈 계수로 사용되는 셀 추출 (가중치 후보)
    # 개선된 정규식: $BF$46, BF$46, INDEX!BF46 등 다양한 형태 포함
    # 패턴: "셀참조*" 형태 (절대/상대 참조, 시트 접두어 모두 처리)
    multiply_pattern = re.compile(
        r'(?:[\w]+!)?\$?([A-Z]+)\$?(\d+)\*',  # SHEET!$COL$ROW* 또는 COL$ROW* 등
        re.IGNORECASE
    )
    weight_candidates = []
    
    for formula in index_df["effective_formula"].dropna():
        matches = multiply_pattern.findall(formula)
        # (col, row) 튜플을 "COLROW" 형태로 변환
        for col, row in matches:
            weight_candidates.append(f"{col.upper()}{row}")
    
    # 추가 필터: FIND("국"|"수"|"영"|"탐"|"한")가 함께 있는 수식만 (가중치 신뢰도 향상)
    subject_pattern = re.compile(r'FIND\s*\(\s*"[국수영탐한]"')
    weight_candidates_filtered = []
    
    for _, row in index_df.iterrows():
        formula = row.get("effective_formula", "")
        if formula and subject_pattern.search(str(formula)):
            matches = multiply_pattern.findall(str(formula))
            for col, rownum in matches:
                weight_candidates_filtered.append(f"{col.upper()}{rownum}")
    
    # === 1차: FIND 필터 적용 (precision↑) ===
    weight_freq_filtered = Counter(weight_candidates_filtered).most_common(30)
    print("=== 1차 가중치 후보 (INDEX 시트, FIND 패턴 포함 수식) ===")
    print("    (precision 우선: 과목 토큰이 명시된 수식만)")
    for ref, count in weight_freq_filtered:
        print(f"  {ref}: {count}회 곱셈 계수로 사용")
    
    # === 2차: 필터 없는 전체 후보 (recall↑) ===
    # ⚠️ FIND 없이 다른 방식(IFS/LOOKUP/헤더 매칭)으로 분기하는 경우 대비
    weight_freq_all = Counter(weight_candidates).most_common(30)
    print("\n=== 2차 가중치 후보 (INDEX 시트, 필터 없음 - 참고용) ===")
    print("    (recall 우선: FIND 없는 수식도 포함, 노이즈 가능)")
    for ref, count in weight_freq_all:
        # 1차에 없는 항목만 표시 (신규 발견)
        if ref not in [r for r, _ in weight_freq_filtered]:
            print(f"  [신규] {ref}: {count}회 곱셈 계수로 사용")
        else:
            print(f"  {ref}: {count}회 곱셈 계수로 사용")
    
    # === 비교 분석 ===
    filtered_set = set(r for r, _ in weight_freq_filtered)
    all_set = set(r for r, _ in weight_freq_all)
    missed = all_set - filtered_set
    if missed:
        print(f"\n⚠️ FIND 필터로 누락될 수 있는 후보: {missed}")
        print("    → 이 셀들도 행 라벨/수식 구조로 검토 권장")
    
    # ❌ WEIGHT_ROWS = [58, 59, 60, 61, 62] 같은 하드코딩 금지!
    # ✅ 1차 결과 우선 사용 + 2차 결과로 누락 확인 + 행 라벨 컨텍스트로 최종 확정
    
  [0-3] 최종 출력 셀 선정 (3-10개)
    - COMPUTE 시트에서 "최종 환산점수" 또는 "합격 예측" 결과가 있는 셀 식별
    - 예: 이과계열분석결과!의 최종 점수 컬럼
    - 이 셀들이 "100% 일치 검증" 대상이 됨

Step 1: 출력 셀의 의존성 클로저 추출
  - formula_catalog.csv에서 해당 셀의 수식 찾기
  - 수식이 참조하는 셀들을 재귀적으로 추적
  - 전체 30만 수식 중 필요한 것만 추출

Step 2: 상수/파라미터 셀 식별
  - 의존성 클로저 내에서 "수식이 아닌 값(상수)" 셀 분리
  - 이것들이 가중치/파라미터 후보
  - 행/열 헤더로 "국어/수학/영어/탐구/한국사" 매핑 확인

Step 3: Python 수식 실행기 구현
  - 필요한 함수만 구현: IF, INDEX, MATCH, VLOOKUP, OFFSET, AVERAGE
  - 의존성 순서대로 셀 계산

Step 4: Parity Test (100% 일치 검증)
  - 동일 입력 → 엑셀 결과 vs Python 결과 비교
  - 불일치 시 수식 파싱 오류 디버깅
  - 일치 확인 후에만 "가중치 확정"

Step 5: 가중치 JSON 생성 및 엔진 통합
  - 검증된 가중치만 JSON으로 저장
  - IndexFallback.DEFAULT_WEIGHTS 제거
  - 새 ExtractedWeightLoader 연결
```

---

## 점진적 구현 전략 (Phase A-D)

전체 303,215개 수식을 한 번에 처리하지 말고, 위험을 분산하여 점진적으로 구현:

### Phase A: INDEX 시트 가중치 추출 (우선 실행)

**대상**: INDEX 시트에서 곱셈 계수로 사용되는 셀 (예: 행 46, 47, 48, 51, 57)

```
⚠️ 주의: 58-62행은 "합산 구조"일 뿐, 가중치 저장소가 아님!
실제 가중치: 곱셈 계수로 반복 참조되는 셀 (BF46, BF47, BF48, BF51, BF57 등)

근거: formula_catalog.csv의 실제 수식 분석
  =BF46*IFERROR(FIND("국",...) + BF47*IFERROR(FIND("수",...) + ...
  → 46="국" 토큰, 47="수" 토큰, 48="영" 토큰, 51="탐" 토큰, 57="한" 토큰
  ⚠️ 과목 매핑은 추정임. 행 라벨/헤더로 최종 확정 필수!

예상 성과: Step 0-2에서 자동 추출된 곱셈 계수 셀 기준
```

```python
# Phase A 구현 - 하드코딩 금지, 자동 추출 결과 사용
import xlwings as xw  # ⚠️ openpyxl(data_only=True)는 캐시값! xlwings 필수

# Excel COM으로 실제 계산된 값 읽기
app = xw.App(visible=False)
wb = app.books.open(excel_path)
ws = wb.sheets["INDEX"]

# ❌ WEIGHT_ROWS = {58: "korean", ...} 같은 하드코딩 금지!
# ✅ Step 0-2에서 자동 추출된 가중치 후보 셀 사용
weight_candidate_cells = get_weight_candidates_from_step0()  # 곱셈 계수 빈도 Top-N

# 가중치 후보 셀의 실제 값과 컨텍스트 확인
weights_by_column = {}
for cell_ref in weight_candidate_cells:
    # 행 라벨 확인 (과목명이 있는지)
    row_label = ws.range(f"A{cell_ref.row}").value
    col_header = ws.range(f"{cell_ref.column}1").value
    value = ws.range(cell_ref).value
    
    # 과목명 매핑 (수식에서 FIND("국",...) 등으로 검증)
    subject = infer_subject_from_context(row_label, cell_ref)
    if subject and value is not None:
        key = col_header or cell_ref.column
        if key not in weights_by_column:
            weights_by_column[key] = {}
        weights_by_column[key][subject] = float(value)

wb.close()
app.quit()

print(f"Phase A 완료: {len(weights_by_column)}개 프로그램 가중치 추출")
```

### Phase B: COMPUTE 시트 (최종 계산 로직)

**대상**: COMPUTE 시트 (46,632회 참조됨)

```
의존성: Phase A 가중치 필요
목표: 최종 환산점수 계산 수식 Python 변환
```

### Phase C: RESTRICT 시트 (결격 조건)

**대상**: rule_candidates.csv 42,900개 규칙 후보

```
특징: 규칙 기반 (수식보다 단순)
목표: 결격 조건 Python 함수 변환
```

### Phase D: 전체 통합 + Parity Test

**대상**: 엔드투엔드 검증

```
검증 방법: xlwings로 Excel COM 실계산
기준: 100% Parity (abs < 1e-6 AND rel < 1e-9 동시 만족)
```

### xlwings 필수화 (옵션 → 필수) ⚠️ Critical

**왜 xlwings가 필수인가?**

```
❌ openpyxl(data_only=True)의 문제점:
  1. "저장된 캐시 값"을 읽음 → 재계산 안 됨
  2. 엑셀에서 저장 안 하면 값이 비거나 오래됨
  3. OFFSET 동적 참조 해결 불가
  4. "진짜 엑셀 결과"가 아님!

✅ xlwings(Excel COM)의 장점:
  1. Excel 엔진이 직접 계산 → 진짜 결과
  2. wb.app.calculate()로 강제 재계산 가능
  3. OFFSET 동적 참조 자동 해결
  4. 100% Parity 검증의 유일한 신뢰 소스
```

`tools/excel_oracle.py` **스켈레톤(22줄)을 실제 구현으로 확장**:

| 항목 | 현재 상태 | 필요 작업 |
|------|----------|----------|
| 파일 크기 | 22줄 (스켈레톤) | 150줄+ (실제 구현) |
| Excel COM | 미구현 | xlwings 기반 구현 |
| OFFSET 처리 | 미지원 | 동적 참조 해결 |
| Parity Test | 미지원 | 100% 일치 검증 |

**⚠️ 제약 사항 (필수 확인)**:
- **Windows + Excel 설치 필수** (Excel COM 사용)
- macOS/Linux에서는 **Parity Test 불가** → Windows VM 권장
- `expected_value`는 **반드시 xlwings로만** 추출 (openpyxl 금지)
- openpyxl은 수식 문자열 추출용으로만 사용 (값 읽기 금지)

---

## 성공 기준

- [ ] 모든 대학/학과별 가중치가 JSON으로 추출됨
- [ ] 엑셀 수식이 Python 함수로 1:1 변환됨
- [ ] 테스트 케이스 20건 100% 일치 (abs < 1e-6 AND rel < 1e-9)
- [ ] `IndexFallback.DEFAULT_WEIGHTS` 완전 제거 → `WeightNotFoundError` 발생으로 대체
- [ ] 어떤 값도 "추정"이나 "가정"으로 만들어지지 않음

---

## 참고: 기존 분석 결과 활용 (이미 추출된 산출물)

### 이미 존재하는 산출물 (outputs/ 폴더)
```
outputs/
├── formula_catalog.csv      # 303,215개 수식 추출됨 (핵심!)
├── rule_candidates.csv      # 42,900개 규칙 후보
├── sheet_flow_graph.json    # 시트 간 의존성 그래프
├── probe_report.txt         # 통계: IF 282,833회, INDEX 46,985회 등
├── dependency_graph.json    # 셀 의존성
└── formula_groups.json      # 공유 수식 그룹
```

### 핵심 의존성 (sheet_flow_graph.json 기반)
```
SUBJECT3, PERCENTAGE → COMPUTE (weight: 46,632) ← 가중치 저장소 가능성 높음
이과계열분석결과 → INFO (weight: 199,957) ← 최종 출력 시트
```

### formula_catalog.csv 활용 예시
```python
import pandas as pd

df = pd.read_csv("outputs/formula_catalog.csv")

# COMPUTE를 참조하는 수식 찾기
compute_refs = df[df["effective_formula"].str.contains("COMPUTE", na=False)]
print(f"COMPUTE 참조 수식: {len(compute_refs)}개")

# 특정 시트의 수식만 추출
index_formulas = df[df["sheet_name"] == "INDEX"]
```

**중요**: 추출은 이미 완료됨. 이제 해야 할 것은 이 데이터를 "실행 가능한 Python 계산기"로 통합하는 것.

---

## 부록 A: 의존성 클로저 추출 구현

```python
# tools/dependency_closure.py
"""
목표: 최종 출력 셀로부터 역추적하여 필요한 수식/상수만 추출
"""
import pandas as pd
import ast
import re
from collections import deque
from typing import Set, Dict, List

class DependencyClosure:
    def __init__(self, formula_catalog_path: str):
        self.df = pd.read_csv(formula_catalog_path)
        # 셀 참조 → 수식 매핑
        self.cell_to_formula: Dict[str, str] = {}
        self.cell_to_refs: Dict[str, List[str]] = {}
        
        for _, row in self.df.iterrows():
            key = f"{row['sheet_name']}!{row['cell_ref']}"
            self.cell_to_formula[key] = row.get('effective_formula', '')
            try:
                refs = ast.literal_eval(row['cell_refs']) if pd.notna(row['cell_refs']) else []
                self.cell_to_refs[key] = refs
            except:
                self.cell_to_refs[key] = []
    
    def extract_closure(self, target_cells: List[str]) -> Dict:
        """
        target_cells: ["COMPUTE!J3", "이과계열분석결과!D5", ...]
        return: 필요한 모든 셀과 수식
        """
        visited: Set[str] = set()
        queue = deque(target_cells)
        result = {
            "formulas": {},      # 수식이 있는 셀
            "constants": {},     # 수식 없이 값만 있는 셀 (가중치 후보)
            "dependency_order": []  # 계산 순서
        }
        
        while queue:
            cell = queue.popleft()
            if cell in visited:
                continue
            visited.add(cell)
            
            formula = self.cell_to_formula.get(cell, '')
            refs = self.cell_to_refs.get(cell, [])
            
            if formula and formula.startswith('='):
                result["formulas"][cell] = formula
                # 참조하는 셀들을 큐에 추가
                for ref in refs:
                    if ref not in visited:
                        queue.append(ref)
            else:
                # 수식이 없으면 상수 (가중치 후보)
                result["constants"][cell] = None  # 값은 나중에 엑셀에서 읽음
            
            result["dependency_order"].append(cell)
        
        # 역순으로 정렬 (의존성 순서: 참조되는 셀이 먼저)
        result["dependency_order"].reverse()
        return result

# 사용 예시
if __name__ == "__main__":
    closure = DependencyClosure("outputs/formula_catalog.csv")
    
    # 최종 출력 셀 지정 (Step 0에서 확인한 셀들)
    targets = ["COMPUTE!J3", "COMPUTE!J4", "COMPUTE!J5"]
    
    deps = closure.extract_closure(targets)
    print(f"필요한 수식: {len(deps['formulas'])}개")
    print(f"상수(가중치 후보): {len(deps['constants'])}개")
    print(f"계산 순서: {len(deps['dependency_order'])}개 셀")
```

---

## 부록 B: 수식 실행기 (Formula Evaluator) 구현

```python
# theory_engine/formula_evaluator.py
"""
엑셀 수식을 Python으로 실행하는 인터프리터
지원 함수: IF, INDEX, MATCH, VLOOKUP, AVERAGE, OFFSET, IFERROR, SUM
"""
import re
import numpy as np
from typing import Dict, Any, Optional, Callable

class FormulaEvaluator:
    def __init__(self, cell_values: Dict[str, Any]):
        """
        cell_values: {"COMPUTE!C2": 0.3, "INDEX!D58": 95, ...}
        """
        self.cells = cell_values
        self.functions = {
            "IF": self._if,
            "IFS": self._ifs,
            "IFERROR": self._iferror,
            "INDEX": self._index,
            "MATCH": self._match,
            "VLOOKUP": self._vlookup,
            "AVERAGE": self._average,
            "SUM": self._sum,
            "OFFSET": self._offset,
            "AND": self._and,
            "OR": self._or,
            "FIND": self._find,
        }
    
    def evaluate(self, formula: str, context_cell: str = "") -> Any:
        """
        수식 문자열을 파싱하고 실행
        """
        if not formula or not formula.startswith("="):
            return formula
        
        expr = formula[1:]  # "=" 제거
        return self._eval_expr(expr, context_cell)
    
    def _eval_expr(self, expr: str, context: str) -> Any:
        """재귀적 수식 평가"""
        expr = expr.strip()
        
        # 함수 호출 패턴: FUNC(args)
        func_match = re.match(r'^([A-Z]+)\((.*)\)$', expr, re.DOTALL)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            if func_name in self.functions:
                args = self._parse_args(args_str)
                return self.functions[func_name](args, context)
        
        # 셀 참조: SHEET!CELL 또는 CELL
        if re.match(r'^[A-Z]+\d+$', expr) or '!' in expr:
            return self._get_cell_value(expr, context)
        
        # 숫자
        try:
            return float(expr)
        except:
            pass
        
        # 문자열
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # 기본 연산 (+, -, *, /)
        return self._eval_arithmetic(expr, context)
    
    def _get_cell_value(self, ref: str, context: str) -> Any:
        """셀 값 조회"""
        # 절대/상대 참조 정규화
        ref = ref.replace("$", "")
        
        # 시트가 없으면 context에서 추출
        if "!" not in ref and context:
            sheet = context.split("!")[0]
            ref = f"{sheet}!{ref}"
        
        return self.cells.get(ref, 0)
    
    # === 함수 구현 ===
    
    def _if(self, args: list, ctx: str) -> Any:
        """=IF(condition, true_val, false_val)"""
        cond = self._eval_expr(args[0], ctx)
        true_val = self._eval_expr(args[1], ctx) if len(args) > 1 else True
        false_val = self._eval_expr(args[2], ctx) if len(args) > 2 else False
        return true_val if cond else false_val
    
    def _iferror(self, args: list, ctx: str) -> Any:
        """=IFERROR(expr, fallback)"""
        try:
            return self._eval_expr(args[0], ctx)
        except:
            return self._eval_expr(args[1], ctx) if len(args) > 1 else 0
    
    def _sum(self, args: list, ctx: str) -> float:
        """=SUM(range)"""
        total = 0
        for arg in args:
            val = self._eval_expr(arg, ctx)
            if isinstance(val, (int, float)):
                total += val
            elif isinstance(val, list):
                total += sum(v for v in val if isinstance(v, (int, float)))
        return total
    
    def _average(self, args: list, ctx: str) -> float:
        """=AVERAGE(range)"""
        values = []
        for arg in args:
            val = self._eval_expr(arg, ctx)
            if isinstance(val, (int, float)):
                values.append(val)
            elif isinstance(val, list):
                values.extend(v for v in val if isinstance(v, (int, float)))
        return np.mean(values) if values else 0
    
    def _index(self, args: list, ctx: str) -> Any:
        """=INDEX(array, row, col)"""
        # 간단 구현: 단일 값 반환
        array_ref = args[0]
        row_idx = int(self._eval_expr(args[1], ctx)) if len(args) > 1 else 1
        col_idx = int(self._eval_expr(args[2], ctx)) if len(args) > 2 else 1
        # 실제 구현에서는 범위를 파싱해야 함
        return self._get_cell_value(array_ref, ctx)
    
    def _match(self, args: list, ctx: str) -> int:
        """=MATCH(value, range, match_type)"""
        # 간단 구현
        return 1
    
    def _vlookup(self, args: list, ctx: str) -> Any:
        """=VLOOKUP(key, range, col, exact)"""
        # 간단 구현
        return self._eval_expr(args[0], ctx)
    
    def _offset(self, args: list, ctx: str) -> Any:
        """=OFFSET(ref, rows, cols)"""
        # 동적 참조 구현 필요
        base_ref = args[0]
        row_offset = int(self._eval_expr(args[1], ctx))
        col_offset = int(self._eval_expr(args[2], ctx))
        # 실제 구현에서는 셀 주소 계산 필요
        return self._get_cell_value(base_ref, ctx)
    
    def _and(self, args: list, ctx: str) -> bool:
        return all(self._eval_expr(a, ctx) for a in args)
    
    def _or(self, args: list, ctx: str) -> bool:
        return any(self._eval_expr(a, ctx) for a in args)
    
    def _find(self, args: list, ctx: str) -> int:
        """=FIND(needle, haystack)"""
        needle = str(self._eval_expr(args[0], ctx))
        haystack = str(self._eval_expr(args[1], ctx))
        try:
            return haystack.index(needle) + 1  # Excel은 1-based
        except ValueError:
            raise ValueError(f"FIND: '{needle}' not in '{haystack}'")
    
    def _ifs(self, args: list, ctx: str) -> Any:
        """=IFS(cond1, val1, cond2, val2, ...)"""
        for i in range(0, len(args), 2):
            if self._eval_expr(args[i], ctx):
                return self._eval_expr(args[i+1], ctx)
        return None
    
    def _parse_args(self, args_str: str) -> list:
        """함수 인자 파싱 (중첩 괄호 처리)"""
        args = []
        depth = 0
        current = ""
        
        for char in args_str:
            if char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args
    
    def _eval_arithmetic(self, expr: str, ctx: str) -> float:
        """기본 사칙연산 평가 (보안: eval() 사용 금지!)"""
        # ❌ eval() 사용 금지! 임의 코드 실행 위험
        # ✅ 안전한 수학 표현식 파서 사용
        
        # 셀 참조를 값으로 치환
        # ⚠️ 버그 방지: A1이 A10 내부에 끼어드는 문제 해결
        #    → 긴 참조부터 먼저 치환 (역순 정렬)
        refs = re.findall(r'[A-Z]+\d+', expr)
        # 길이 역순 정렬: A10 → A1 순서로 치환 (A1이 A10을 망가뜨리지 않도록)
        refs_sorted = sorted(set(refs), key=lambda x: (-len(x), x))
        
        for ref in refs_sorted:
            val = self._get_cell_value(ref, ctx)
            # 단어 경계 사용으로 부분 매칭 방지
            expr = re.sub(rf'\b{ref}\b', str(val), expr)
        
        # 안전한 수학 표현식 파싱 (simpleeval 또는 직접 구현)
        try:
            # 방법 1: simpleeval 라이브러리 사용 (권장)
            # pip install simpleeval
            from simpleeval import simple_eval
            return simple_eval(expr)
        except ImportError:
            # 방법 2: 직접 구현 (기본 사칙연산만 지원)
            return self._safe_arithmetic_eval(expr)
    
    def _safe_arithmetic_eval(self, expr: str) -> float:
        """
        안전한 사칙연산 파서 (eval 대체)
        지원: +, -, *, /, (, ), 숫자
        """
        import operator
        import re
        
        # 허용 문자만 포함되었는지 확인
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expr):
            raise ValueError(f"허용되지 않은 문자 포함: {expr}")
        
        # 토큰화
        tokens = re.findall(r'(\d+\.?\d*|[\+\-\*\/\(\)])', expr)
        
        # 간단한 후위 표기법 변환 및 계산
        # (복잡한 경우 shunting-yard 알고리즘 사용)
        def parse_expr(tokens):
            result = parse_term(tokens)
            while tokens and tokens[0] in '+-':
                op = tokens.pop(0)
                right = parse_term(tokens)
                if op == '+':
                    result += right
                else:
                    result -= right
            return result
        
        def parse_term(tokens):
            result = parse_factor(tokens)
            while tokens and tokens[0] in '*/':
                op = tokens.pop(0)
                right = parse_factor(tokens)
                if op == '*':
                    result *= right
                else:
                    # ⚠️ 0으로 나눔: Excel은 #DIV/0! 에러 발생
                    # → Python에서도 에러 발생시켜 Parity 문제 조기 발견
                    if right == 0:
                        raise ZeroDivisionError(
                            f"0으로 나눔 발생 (Excel #DIV/0! 동일). "
                            f"IFERROR로 감싸진 경우 상위 레벨에서 처리 필요"
                        )
                    result /= right
            return result
        
        def parse_factor(tokens):
            if tokens[0] == '(':
                tokens.pop(0)  # '(' 제거
                result = parse_expr(tokens)
                if tokens and tokens[0] == ')':
                    tokens.pop(0)  # ')' 제거
                return result
            else:
                return float(tokens.pop(0))
        
        try:
            return parse_expr(tokens)
        except:
            return 0.0
```

---

## 부록 C: xlwings를 이용한 Parity Test

```python
# tests/parity_test_xlwings.py
"""
Excel COM을 통해 실제 엑셀 계산 결과와 Python 결과 비교
Windows 환경 + Excel 설치 필요
"""
import xlwings as xw
from datetime import datetime
from theory_engine.formula_evaluator import FormulaEvaluator

def parity_test(excel_path: str, test_cases: list) -> dict:
    """
    test_cases: [
        {"input_cells": {"수능입력!C3": 95, ...}, "output_cell": "COMPUTE!J3"},
        ...
    ]
    
    ⚠️ xlwings 운용 가드:
    - Excel COM은 환경에 민감 (설치/보안 경고/외부 링크/계산 모드)
    - 예외 시 프로세스 잔존 방지 필수
    """
    results = {"passed": 0, "failed": 0, "details": []}
    
    app = None
    wb = None
    
    try:
        # === xlwings 운용 가드 시작 ===
        app = xw.App(visible=False)
        
        # 알림/경고 끄기 (외부 링크 경고 등 방지)
        app.display_alerts = False
        app.screen_updating = False
        
        # 계산 모드를 수동으로 설정 후 명시적 재계산
        # (자동 계산이 환경에 따라 다르게 동작할 수 있음)
        app.calculation = 'manual'
        
        # === 환경 정보 로깅 (parity 재현성 보장) ===
        env_info = {
            "excel_version": str(app.api.Version),
            "calculation_mode": str(app.calculation),
            "display_alerts": app.display_alerts,
            "excel_path": excel_path,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"=== xlwings 환경 정보 ===")
        for k, v in env_info.items():
            print(f"  {k}: {v}")
        
        wb = app.books.open(excel_path)
        
        # 외부 링크 상태 확인 및 로깅
        try:
            links = wb.api.LinkSources(1)  # xlExcelLinks = 1
            if links:
                print(f"⚠️ 외부 링크 발견: {len(links)}개")
                for link in links:
                    print(f"    - {link}")
                print("    → 링크 값이 parity에 영향줄 수 있음. 링크 업데이트 정책 확인 필요")
        except:
            print("  외부 링크: 없음 또는 확인 불가")
        
        # 전체 재계산 강제 (CalculateFullRebuild 효과)
        app.api.CalculateFull()
        
        for i, case in enumerate(test_cases):
            # 입력값 설정
            for cell_ref, value in case["input_cells"].items():
                sheet_name, cell = cell_ref.split("!")
                wb.sheets[sheet_name].range(cell).value = value
            
            # 명시적 재계산 (입력 변경 후)
            app.api.CalculateFull()
            
            # Excel 결과 읽기
            out_sheet, out_cell = case["output_cell"].split("!")
            excel_result = wb.sheets[out_sheet].range(out_cell).value
            
            # Python 결과 계산
            evaluator = FormulaEvaluator(case["input_cells"])
            python_result = evaluator.evaluate(case["formula"], case["output_cell"])
            
            # 엄격한 Parity 기준 (abs+rel 동시)
            # ⚠️ 버그 방지: 0은 유효한 값! "and/or" 대신 "is not None" 사용
            if excel_result is not None and python_result is not None:
                abs_err = abs(excel_result - python_result)
                # 둘 다 0인 경우도 유효 (rel_err = 0)
                denominator = max(abs(excel_result), abs(python_result), 1e-15)
                rel_err = abs_err / denominator
            else:
                # None 값이 있으면 비교 불가 → 실패
                abs_err = float('inf')
                rel_err = float('inf')
            
            passed = (abs_err < 1e-6) and (rel_err < 1e-9)
            
            results["details"].append({
                "case": i,
                "output_cell": case["output_cell"],
                "excel": excel_result,
                "python": python_result,
                "abs_error": abs_err,
                "rel_error": rel_err,
                "passed": passed
            })
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
                print(f"❌ Case {i}: {case['output_cell']}")
                print(f"   Excel={excel_result}, Python={python_result}")
                print(f"   abs_err={abs_err:.2e}, rel_err={rel_err:.2e}")
    
    except Exception as e:
        print(f"⚠️ xlwings 오류: {e}")
        results["error"] = str(e)
    
    finally:
        # === xlwings 운용 가드 종료 (프로세스 잔존 방지) ===
        try:
            if wb:
                wb.close()
        except:
            pass
        
        try:
            if app:
                app.quit()
        except:
            pass
        
        # === 잔존 Excel 프로세스 정리 (PID 기반만 허용!) ===
        # ❌ 절대 금지: taskkill /F /IM EXCEL.EXE
        #    → 다른 사용자/작업의 Excel까지 종료시켜 운영 사고 발생!
        # ✅ 허용: PID 기반 종료 (이 세션에서 시작한 프로세스만)
        try:
            if app and hasattr(app, 'api') and app.api:
                # 이 세션의 Excel PID 저장 (시작 시점에 기록 권장)
                try:
                    pid = app.api.Hwnd  # Excel 윈도우 핸들 (PID 아님, 참고용)
                    print(f"  Excel 세션 정보: Hwnd={pid}")
                except:
                    pass
        except:
            pass
        
        # 경고 메시지
        print("\n⚠️ Excel 프로세스 잔존 확인:")
        print("   taskkill /IM EXCEL.EXE 같은 전체 종료는 절대 사용 금지!")
        print("   잔존 시 작업관리자에서 해당 PID만 수동 종료 권장")
    
    print(f"\n=== Parity Test Results ===")
    print(f"Passed: {results['passed']}/{len(test_cases)}")
    print(f"Failed: {results['failed']}/{len(test_cases)}")
    
    return results

if __name__ == "__main__":
    test_cases = [
        {
            "input_cells": {
                "수능입력!C3": 95,  # 국어
                "수능입력!C4": 98,  # 수학
                "수능입력!C5": 1,   # 영어
                "수능입력!C6": 90,  # 탐구1
                "수능입력!C7": 92,  # 탐구2
            },
            "output_cell": "COMPUTE!J3",
            "formula": "=..."  # formula_catalog에서 가져옴
        }
    ]
    
    parity_test(
        r"C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx",
        test_cases
    )
```

---

## 부록 D: 최종 통합 워크플로우

```bash
# 1. 의존성 클로저 추출
python tools/dependency_closure.py > outputs/closure_result.json

# 2. 상수 셀에서 가중치 추출 (엑셀에서 직접 읽기)
python tools/extract_constants.py > theory_engine/weights/weights_by_program.json

# 3. 수식 실행기로 테스트
python -m pytest tests/test_excel_parity.py -v

# 4. Parity Test (xlwings)
python tests/parity_test_xlwings.py

# 5. 100% 통과 시 IndexFallback 제거
# theory_engine/optimizers/index_fallback.py → 삭제 또는 ExtractedWeightLoader로 교체
```
