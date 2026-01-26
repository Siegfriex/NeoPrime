# ============================================================
# Logic Transpiler v2: 복잡한 수식 지원
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
확장된 Excel 수식 → Python 변환 지원:
- 복잡한 IF/OR/AND 중첩
- INDEX/MATCH 2D 조회
- HLOOKUP 지원
- 다중 시트 참조
- 문자열 결합 (&)
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TranspiledFormula:
    """변환된 수식"""
    original: str
    python_code: str
    dependencies: List[str]
    sheet_refs: List[str]
    complexity: str  # 'simple', 'medium', 'complex'


class AdvancedLogicTranspiler:
    """고급 수식 트랜스파일러"""

    def __init__(self, metadata_dir: str = './output'):
        self.metadata_dir = Path(metadata_dir)
        self.sheets_data: Dict[str, Any] = {}

    def transpile(self, formula: str, context: Dict[str, Any] = None) -> TranspiledFormula:
        """
        Excel 수식을 Python 코드로 변환

        Args:
            formula: Excel 수식 (=로 시작)
            context: 컨텍스트 정보 (현재 시트, 행/열 등)

        Returns:
            TranspiledFormula 객체
        """
        if not formula or not formula.startswith('='):
            return TranspiledFormula(
                original=formula,
                python_code=f"'{formula}'",
                dependencies=[],
                sheet_refs=[],
                complexity='simple'
            )

        expr = formula[1:]  # '=' 제거

        # 시트 참조 추출
        sheet_refs = self._extract_sheet_refs(expr)

        # 복잡도 판정
        complexity = self._assess_complexity(expr)

        # 변환
        python_code = self._transpile_expression(expr, context or {})

        # 의존성 추출
        dependencies = self._extract_dependencies(expr)

        return TranspiledFormula(
            original=formula,
            python_code=python_code,
            dependencies=dependencies,
            sheet_refs=sheet_refs,
            complexity=complexity
        )

    def _assess_complexity(self, expr: str) -> str:
        """수식 복잡도 평가"""
        expr_upper = expr.upper()

        # 중첩 함수 수 계산
        func_count = len(re.findall(r'[A-Z]+\s*\(', expr_upper))

        # 조건문 중첩 확인
        if_count = expr_upper.count('IF(')

        if func_count > 5 or if_count > 2:
            return 'complex'
        elif func_count > 2 or if_count > 0:
            return 'medium'
        return 'simple'

    def _extract_sheet_refs(self, expr: str) -> List[str]:
        """시트 참조 추출"""
        # 패턴: SheetName!A1 또는 'Sheet Name'!A1
        pattern = r"'?([^'!]+)'?!"
        matches = re.findall(pattern, expr)
        return list(set(matches))

    def _extract_dependencies(self, expr: str) -> List[str]:
        """셀 의존성 추출"""
        # 단일 셀: A1, $A$1, A$1, $A1
        cell_pattern = r'\$?([A-Z]{1,3})\$?(\d+)'
        refs = []
        for match in re.finditer(cell_pattern, expr):
            ref = f"{match.group(1)}{match.group(2)}"
            if ref not in refs:
                refs.append(ref)
        return refs

    def _transpile_expression(self, expr: str, context: Dict) -> str:
        """표현식을 Python으로 변환"""
        # 1. 최외곽 함수 확인
        main_func = self._get_main_function(expr)

        if main_func == 'IF':
            return self._transpile_if(expr, context)
        elif main_func == 'IFERROR':
            return self._transpile_iferror(expr, context)
        elif main_func == 'INDEX':
            return self._transpile_index(expr, context)
        elif main_func == 'MATCH':
            return self._transpile_match(expr, context)
        elif main_func == 'VLOOKUP':
            return self._transpile_vlookup(expr, context)
        elif main_func == 'HLOOKUP':
            return self._transpile_hlookup(expr, context)
        elif main_func == 'SUM':
            return self._transpile_sum(expr, context)
        elif main_func == 'AVERAGE':
            return self._transpile_average(expr, context)
        elif main_func == 'MAX':
            return self._transpile_max(expr, context)
        elif main_func == 'ROUND':
            return self._transpile_round(expr, context)
        elif main_func == 'OR':
            return self._transpile_or(expr, context)
        elif main_func == 'AND':
            return self._transpile_and(expr, context)
        else:
            # 산술 연산 또는 단순 참조
            return self._transpile_arithmetic(expr, context)

    def _get_main_function(self, expr: str) -> str:
        """최외곽 함수명 추출"""
        match = re.match(r'([A-Z]+)\s*\(', expr, re.IGNORECASE)
        return match.group(1).upper() if match else ''

    def _get_function_args(self, expr: str, func_name: str) -> List[str]:
        """함수 인자 추출 (괄호 깊이 고려)"""
        start_idx = expr.upper().find(func_name.upper() + '(')
        if start_idx == -1:
            return []

        start_idx += len(func_name) + 1
        depth = 1
        current_arg = ""
        args = []

        for char in expr[start_idx:]:
            if char == '(':
                depth += 1
                current_arg += char
            elif char == ')':
                depth -= 1
                if depth == 0:
                    if current_arg.strip():
                        args.append(current_arg.strip())
                    break
                current_arg += char
            elif char == ',' and depth == 1:
                if current_arg.strip():
                    args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char

        return args

    # ========================================
    # 함수별 변환 로직
    # ========================================

    def _transpile_if(self, expr: str, context: Dict) -> str:
        """IF 함수 변환"""
        args = self._get_function_args(expr, 'IF')
        if len(args) < 2:
            return "None"

        condition = self._transpile_expression(args[0], context)
        true_val = self._transpile_expression(args[1], context) if len(args) > 1 else "None"
        false_val = self._transpile_expression(args[2], context) if len(args) > 2 else "None"

        return f"({true_val} if {condition} else {false_val})"

    def _transpile_iferror(self, expr: str, context: Dict) -> str:
        """IFERROR 함수 변환"""
        args = self._get_function_args(expr, 'IFERROR')
        if len(args) < 2:
            return "None"

        try_expr = self._transpile_expression(args[0], context)
        fallback = self._transpile_expression(args[1], context)

        return f"_safe_eval(lambda: {try_expr}, {fallback})"

    def _transpile_or(self, expr: str, context: Dict) -> str:
        """OR 함수 변환"""
        args = self._get_function_args(expr, 'OR')
        conditions = [self._transpile_expression(arg, context) for arg in args]
        return "(" + " or ".join(conditions) + ")"

    def _transpile_and(self, expr: str, context: Dict) -> str:
        """AND 함수 변환"""
        args = self._get_function_args(expr, 'AND')
        conditions = [self._transpile_expression(arg, context) for arg in args]
        return "(" + " and ".join(conditions) + ")"

    def _transpile_vlookup(self, expr: str, context: Dict) -> str:
        """VLOOKUP 함수 변환"""
        args = self._get_function_args(expr, 'VLOOKUP')
        if len(args) < 3:
            return "None"

        lookup_val = self._convert_cell_ref(args[0])
        table_ref = self._convert_range_ref(args[1])
        col_idx = args[2]
        approx = args[3] if len(args) > 3 else "False"

        return f"_vlookup({lookup_val}, {table_ref}, {col_idx}, {approx})"

    def _transpile_hlookup(self, expr: str, context: Dict) -> str:
        """HLOOKUP 함수 변환"""
        args = self._get_function_args(expr, 'HLOOKUP')
        if len(args) < 3:
            return "None"

        lookup_val = self._convert_cell_ref(args[0])
        table_ref = self._convert_range_ref(args[1])
        row_idx = args[2]
        approx = args[3] if len(args) > 3 else "False"

        return f"_hlookup({lookup_val}, {table_ref}, {row_idx}, {approx})"

    def _transpile_match(self, expr: str, context: Dict) -> str:
        """
        MATCH 함수 독립 변환
        MATCH(lookup_value, lookup_array, [match_type])
        → _match(lookup_value, lookup_array, match_type)
        """
        args = self._get_function_args(expr, 'MATCH')
        if len(args) < 2:
            return "None"

        lookup_val = self._convert_cell_ref_with_sheet(args[0])
        lookup_array = self._convert_range_ref(args[1])
        match_type = args[2] if len(args) > 2 else "0"

        return f"_match({lookup_val}, {lookup_array}, {match_type})"

    def _transpile_index(self, expr: str, context: Dict) -> str:
        """INDEX 함수 변환 (MATCH와 조합 포함)"""
        args = self._get_function_args(expr, 'INDEX')
        if len(args) < 2:
            return "None"

        array_ref = self._convert_range_ref(args[0])

        # MATCH 함수가 인자로 있는지 확인
        if len(args) >= 3 and 'MATCH' in args[1].upper() and 'MATCH' in args[2].upper():
            # INDEX/MATCH 2D
            row_match = self._transpile_expression(args[1], context)
            col_match = self._transpile_expression(args[2], context)
            return f"_index_match_2d({array_ref}, {row_match}, {col_match})"
        elif len(args) >= 2 and 'MATCH' in args[1].upper():
            # INDEX/MATCH 1D
            row_match = self._transpile_expression(args[1], context)
            col = self._convert_cell_ref_with_sheet(args[2]) if len(args) > 2 else "0"
            return f"_index({array_ref}, {row_match}, {col})"
        else:
            # 단순 INDEX
            row = self._convert_cell_ref_with_sheet(args[1]) if len(args) > 1 else "0"
            col = self._convert_cell_ref_with_sheet(args[2]) if len(args) > 2 else "0"
            return f"_index({array_ref}, {row}, {col})"

    def _transpile_sum(self, expr: str, context: Dict) -> str:
        """SUM 함수 변환"""
        args = self._get_function_args(expr, 'SUM')
        converted = [self._convert_cell_ref(arg) for arg in args]
        return f"sum([{', '.join(converted)}])"

    def _transpile_average(self, expr: str, context: Dict) -> str:
        """AVERAGE 함수 변환"""
        args = self._get_function_args(expr, 'AVERAGE')
        converted = [self._convert_cell_ref(arg) for arg in args]
        return f"np.nanmean([{', '.join(converted)}])"

    def _transpile_max(self, expr: str, context: Dict) -> str:
        """MAX 함수 변환"""
        args = self._get_function_args(expr, 'MAX')
        converted = [self._convert_cell_ref(arg) for arg in args]
        return f"max([{', '.join(converted)}])"

    def _transpile_round(self, expr: str, context: Dict) -> str:
        """ROUND 함수 변환"""
        args = self._get_function_args(expr, 'ROUND')
        if len(args) < 1:
            return "0"
        value = self._transpile_expression(args[0], context)
        decimals = args[1] if len(args) > 1 else "0"
        return f"round({value}, {decimals})"

    def _transpile_arithmetic(self, expr: str, context: Dict) -> str:
        """
        산술 표현식 변환 (시트 참조 완전 지원)

        변환 예시:
        - 수능입력!$C$18="" → sheets['수능입력']['C18']==''
        - $G6*1>=$J6*1 → row['G6']*1>=row['J6']*1
        - A1&" / "&B1 → row['A1']+' / '+row['B1']
        """
        result = expr

        # 1. 시트 참조 처리 (먼저 처리해야 함)
        # 패턴: Sheet!$A$1 또는 'Sheet Name'!$A$1
        sheet_ref_pattern = r"'?([가-힣A-Za-z0-9_\s]+)'?!\$?([A-Z]+)\$?(\d+)"
        result = re.sub(
            sheet_ref_pattern,
            lambda m: f"sheets['{m.group(1).strip()}']['{m.group(2)}{m.group(3)}']",
            result
        )

        # 2. 단순 셀 참조 처리 (시트 참조 처리 후)
        # 패턴: $A$1, A$1, $A1, A1 (시트 참조가 아닌 것만)
        # 주의: sheets['...']['...'] 형태는 제외해야 함
        cell_pattern = r"(?<![\['\w])\$?([A-Z]+)\$?(\d+)(?![\]'\w:])"
        result = re.sub(
            cell_pattern,
            lambda m: f"row['{m.group(1)}{m.group(2)}']",
            result
        )

        # 3. 비교 연산자 변환
        result = result.replace('<>', '!=')
        # = → == (단, ==, !=, <=, >= 제외)
        result = re.sub(r'(?<![=!<>])=(?![=])', '==', result)

        # 4. 문자열 결합 변환 (&  → +)
        result = result.replace('&', ' + ')

        # 5. 빈 문자열
        result = result.replace('""', "''")

        # 6. TRUE/FALSE → True/False
        result = re.sub(r'\bTRUE\b', 'True', result, flags=re.IGNORECASE)
        result = re.sub(r'\bFALSE\b', 'False', result, flags=re.IGNORECASE)

        return result

    def _convert_cell_ref(self, ref: str) -> str:
        """셀 참조를 Python 표현식으로 변환 (하위 호환)"""
        return self._convert_cell_ref_with_sheet(ref)

    def _convert_cell_ref_with_sheet(self, ref: str) -> str:
        """
        셀 참조를 Python 표현식으로 변환 (시트 참조 완전 지원)

        변환 예시:
        - 수능입력!$C$18 → sheets['수능입력']['C18']
        - 'Sheet Name'!A1 → sheets['Sheet Name']['A1']
        - $A$1 → row['A1']
        - A1 → row['A1']
        - "문자열" → '문자열'
        - 123 → 123
        """
        if not ref:
            return "None"

        ref = ref.strip()

        # 문자열 리터럴
        if ref.startswith('"'):
            return ref.replace('"', "'")
        if ref.startswith("'") and '!' not in ref:
            return ref

        # 숫자
        try:
            float(ref)
            return ref
        except ValueError:
            pass

        # 시트 참조 패턴: Sheet!Cell 또는 'Sheet Name'!Cell
        sheet_ref_pattern = r"^'?([^'!]+)'?!\$?([A-Z]+)\$?(\d+)$"
        match = re.match(sheet_ref_pattern, ref, re.IGNORECASE)
        if match:
            sheet_name = match.group(1)
            col = match.group(2)
            row_num = match.group(3)
            return f"sheets['{sheet_name}']['{col}{row_num}']"

        # 시트 참조 (범위 포함): Sheet!A1:B10
        sheet_range_pattern = r"^'?([^'!]+)'?!\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)$"
        match = re.match(sheet_range_pattern, ref, re.IGNORECASE)
        if match:
            sheet_name = match.group(1)
            return f"sheets['{sheet_name}']['{match.group(2)}{match.group(3)}:{match.group(4)}{match.group(5)}']"

        # 단순 셀 참조
        ref = ref.replace('$', '')

        # 셀 참조 패턴 확인
        cell_pattern = r'^([A-Z]+)(\d+)$'
        match = re.match(cell_pattern, ref, re.IGNORECASE)
        if match:
            return f"row['{match.group(1)}{match.group(2)}']"

        # 기타 (변환 불가 시 원본 반환)
        return f"'{ref}'"

    def _convert_range_ref(self, ref: str) -> str:
        """범위 참조를 Python 표현식으로 변환"""
        ref = ref.strip().replace('$', '')

        # 시트 참조 포함 범위: Sheet!A:C 또는 Sheet!A1:B10
        if '!' in ref:
            parts = ref.split('!', 1)
            sheet = parts[0].strip("'")
            range_ref = parts[1]
            return f"'{sheet}!{range_ref}'"

        return f"'{ref}'"


def transpile_analysis_formulas():
    """이과/문과계열분석결과 시트의 수식 변환"""
    print("=" * 70)
    print("복잡한 수식 변환 테스트")
    print("=" * 70)

    transpiler = AdvancedLogicTranspiler()

    # 테스트 수식 목록
    test_formulas = [
        # 1. 시트 참조 테스트: 수능입력!$C$18 → sheets['수능입력']['C18']
        '=IF(OR(수능입력!$C$18="",수능입력!$C$18=0,수능입력!$C$18>9),"오류",IF($G6>=100,"합격","불합격"))',

        # 2. INDEX/MATCH 2D
        '=IFERROR(INDEX(COMPUTE!$A$1:$UG$72,MATCH(E$5,COMPUTE!$B$1:$B$72,0),MATCH($AK6,COMPUTE!$A$2:$UG$2,0)),0)',

        # 3. 독립 MATCH 함수 테스트
        '=MATCH("서울대",COMPUTE!$A$2:$UG$2,0)',

        # 4. 단순 SUM
        '=SUM(E6,F6)',

        # 5. HLOOKUP + AVERAGE
        '=IF($G6=0,"",AVERAGE(HLOOKUP($AK6,COMPUTE!$2:$8,4,FALSE),HLOOKUP($AK6,COMPUTE!$2:$8,5,FALSE)))',

        # 6. 문자열 결합 (&)
        '=ROUND(HLOOKUP($AK6,COMPUTE!$2:$8,4,FALSE)*100,0)&" / 100"',

        # 7. 복잡한 다중 시트 참조
        '=VLOOKUP($B6&" "&$C6,RESTRICT!$I:$L,4,FALSE)',
    ]

    for i, formula in enumerate(test_formulas):
        print(f"\n[수식 {i+1}]")
        print(f"  원본: {formula[:80]}...")

        result = transpiler.transpile(formula)

        print(f"  복잡도: {result.complexity}")
        print(f"  시트 참조: {result.sheet_refs}")
        print(f"  Python: {result.python_code[:100]}...")

    # 실제 메타데이터에서 변환
    print("\n" + "=" * 70)
    print("이과계열분석결과 실제 수식 변환")
    print("=" * 70)

    metadata_path = Path('./output/이과계열분석결과_formula_metadata.json')
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        for col_name, data in metadata.get('formula_samples', {}).items():
            formula = data.get('formula', '')
            if formula:
                result = transpiler.transpile(formula)
                print(f"\n[{col_name}]")
                print(f"  패턴: {metadata['formula_patterns'].get(col_name, 'unknown')}")
                print(f"  복잡도: {result.complexity}")
                print(f"  Python: {result.python_code[:120]}...")


def generate_analysis_engine():
    """분석결과 시트용 엔진 생성"""
    print("\n" + "=" * 70)
    print("분석결과 엔진 클래스 생성")
    print("=" * 70)

    transpiler = AdvancedLogicTranspiler()

    # 이과계열분석결과 메타데이터 로드
    metadata_path = Path('./output/이과계열분석결과_formula_metadata.json')
    if not metadata_path.exists():
        print("[오류] 메타데이터 파일 없음")
        return

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 엔진 클래스 생성
    engine_code = '''# ============================================================
# Auto-Generated: 이과계열분석결과 Calculator Engine
# Generated by Logic Transpiler v2.3
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


def _safe_eval(expr_func, fallback=None):
    """IFERROR 구현"""
    try:
        result = expr_func()
        if pd.isna(result) or result is None:
            return fallback
        return result
    except:
        return fallback


def _vlookup(sheets, lookup_val, table_ref: str, col_idx: int, approx: bool = False):
    """
    VLOOKUP 구현
    table_ref: 'Sheet!A:C' 형태
    """
    try:
        sheet_name, range_ref = table_ref.split('!')
        df = sheets.get(sheet_name)
        if df is None:
            return None
        # 첫 번째 컬럼에서 lookup_val 찾기
        mask = df.iloc[:, 0] == lookup_val
        if not mask.any():
            return None
        idx = mask.idxmax()
        return df.iloc[idx, col_idx - 1]
    except:
        return None


def _hlookup(sheets, lookup_val, table_ref: str, row_idx: int, approx: bool = False):
    """
    HLOOKUP 구현
    table_ref: 'Sheet!2:8' 형태
    """
    try:
        sheet_name, range_ref = table_ref.split('!')
        df = sheets.get(sheet_name)
        if df is None:
            return None
        # 첫 번째 행에서 lookup_val 찾기
        first_row = df.iloc[0]
        mask = first_row == lookup_val
        if not mask.any():
            return None
        col_idx = mask.idxmax()
        return df.iloc[row_idx - 1, col_idx]
    except:
        return None


def _match(sheets, lookup_val, array_ref: str, match_type: int = 0):
    """
    MATCH 함수 구현
    array_ref: 'Sheet!A2:UG2' 형태
    match_type: 0 (정확히 일치), 1 (이하 최대), -1 (이상 최소)
    Returns: 1-based 인덱스
    """
    try:
        sheet_name, range_ref = array_ref.split('!')
        df = sheets.get(sheet_name)
        if df is None:
            return None

        # 범위 파싱 (예: A2:UG2 → 행 2의 A부터 UG까지)
        # 1차원 배열로 변환
        arr = df.values.flatten()

        if match_type == 0:  # 정확히 일치
            idx = np.where(arr == lookup_val)[0]
            return idx[0] + 1 if len(idx) > 0 else None
        elif match_type == 1:  # 이하 최대값
            mask = arr <= lookup_val
            if not mask.any():
                return None
            return np.where(mask)[0][-1] + 1
        else:  # 이상 최소값
            mask = arr >= lookup_val
            if not mask.any():
                return None
            return np.where(mask)[0][0] + 1
    except:
        return None


def _index(sheets, array_ref: str, row: int, col: int = 0):
    """
    INDEX 함수 구현
    array_ref: 'Sheet!A1:UG72' 형태
    """
    try:
        sheet_name, range_ref = array_ref.split('!')
        df = sheets.get(sheet_name)
        if df is None:
            return None
        return df.iloc[row - 1, col - 1 if col > 0 else 0]
    except:
        return None


def _index_match_2d(sheets, array_ref: str, row_match, col_match):
    """INDEX/MATCH 2D 구현"""
    try:
        if row_match is None or col_match is None:
            return None
        sheet_name, range_ref = array_ref.split('!')
        df = sheets.get(sheet_name)
        if df is None:
            return None
        return df.iloc[row_match - 1, col_match - 1]
    except:
        return None


class AnalysisResultEngine:
    """이과/문과계열분석결과 계산 엔진"""

    def __init__(self, sheets: Dict[str, pd.DataFrame]):
        """
        Args:
            sheets: 시트명 → DataFrame 매핑
        """
        self.sheets = sheets

'''

    # 각 컬럼별 메서드 생성
    for col_name, data in metadata.get('formula_samples', {}).items():
        formula = data.get('formula', '')
        if not formula:
            continue

        result = transpiler.transpile(formula)
        pattern = metadata['formula_patterns'].get(col_name, 'unknown')

        method_code = f'''
    def calc_{col_name}(self, row: Dict[str, Any]) -> Any:
        """
        {col_name} 계산
        패턴: {pattern}
        원본: {formula[:60]}...
        """
        sheets = self.sheets
        try:
            return {result.python_code}
        except Exception as e:
            return None
'''
        engine_code += method_code

    # 전체 계산 메서드
    engine_code += '''
    def calculate_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """행 전체 계산"""
        results = {}
'''
    for col_name in metadata.get('formula_samples', {}).keys():
        engine_code += f"        results['{col_name}'] = self.calc_{col_name}(row)\n"

    engine_code += "        return results\n"

    # 파일 저장
    output_path = Path('./output/analysis_result_engine.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(engine_code)

    print(f"[완료] {output_path}")
    print(f"  - 메서드 수: {len(metadata.get('formula_samples', {}))}개")


if __name__ == '__main__':
    transpile_analysis_formulas()
    generate_analysis_engine()
