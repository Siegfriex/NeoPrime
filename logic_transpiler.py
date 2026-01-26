# ============================================================
# Logic Transpiler: Excel Formula → Python Code
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
엑셀 수식을 실행 가능한 Python 코드로 변환하는 트랜스파일러

지원 함수 매핑:
- IF → np.where / Python if
- OR/AND → np.logical_or / np.logical_and
- VLOOKUP → dict.get / df.merge
- HLOOKUP → df.loc lookup
- INDEX/MATCH → df.iloc / df.loc
- SUM → np.sum / df.sum()
- AVERAGE → np.mean / df.mean()
- IFERROR → try-except wrapper
- ROUND → np.round
- MAX/MIN → np.maximum / np.minimum
"""

import re
import json
import ast
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class FormulaType(Enum):
    """수식 유형 분류"""
    CONDITIONAL = "conditional"          # IF, IFS
    LOOKUP = "lookup"                    # VLOOKUP, HLOOKUP
    INDEX_MATCH = "index_match"          # INDEX/MATCH
    AGGREGATION = "aggregation"          # SUM, AVERAGE, COUNT, MAX, MIN
    ARITHMETIC = "arithmetic"            # +, -, *, /
    REFERENCE = "reference"              # 단순 셀 참조
    ERROR_HANDLER = "error_handler"      # IFERROR, IFNA
    COMPOUND = "compound"                # 복합 수식


@dataclass
class ParsedFormula:
    """파싱된 수식 구조체"""
    original: str
    formula_type: FormulaType
    function_name: str
    arguments: List[Any]
    cell_references: List[str]
    sheet_references: List[str]
    python_code: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class UniversityLogic:
    """대학별 환산 로직"""
    university_name: str
    formula: str
    weight_columns: List[str]  # 반영 영역 (국어, 수학, 영어 등)
    python_function: str = ""


class ExcelFunctionMapper:
    """엑셀 함수 → Python 코드 매퍼"""

    # 함수 매핑 테이블
    FUNCTION_MAP = {
        # 조건문
        'IF': 'np.where({cond}, {true_val}, {false_val})',
        'IFS': '_ifs({conditions})',
        'OR': 'np.logical_or.reduce([{args}])',
        'AND': 'np.logical_and.reduce([{args}])',

        # 룩업
        'VLOOKUP': 'self._vlookup({lookup_val}, {table}, {col_idx}, {approx})',
        'HLOOKUP': 'self._hlookup({lookup_val}, {table}, {row_idx}, {approx})',
        'INDEX': 'self._index({array}, {row}, {col})',
        'MATCH': 'self._match({lookup_val}, {array}, {match_type})',

        # 집계
        'SUM': 'np.nansum([{args}])',
        'AVERAGE': 'np.nanmean([{args}])',
        'COUNT': 'np.count_nonzero(~np.isnan([{args}]))',
        'MAX': 'np.nanmax([{args}])',
        'MIN': 'np.nanmin([{args}])',

        # 에러 핸들링
        'IFERROR': 'self._iferror(lambda: {expr}, {fallback})',
        'IFNA': 'self._ifna(lambda: {expr}, {fallback})',

        # 수학
        'ROUND': 'np.round({value}, {decimals})',
        'ABS': 'np.abs({value})',
        'SQRT': 'np.sqrt({value})',

        # 문자열
        'CONCATENATE': '"".join([str(x) for x in [{args}]])',
        'LEN': 'len(str({value}))',
        'LEFT': 'str({value})[:{num_chars}]',
        'RIGHT': 'str({value})[-{num_chars}:]',
    }

    @classmethod
    def get_python_equivalent(cls, func_name: str) -> Optional[str]:
        """엑셀 함수명에 대응하는 Python 템플릿 반환"""
        return cls.FUNCTION_MAP.get(func_name.upper())


class FormulaParser:
    """엑셀 수식 파서"""

    # 셀 참조 패턴
    CELL_REF_PATTERN = r'\$?([A-Z]{1,3})\$?(\d+)'
    RANGE_REF_PATTERN = r'\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)'
    SHEET_REF_PATTERN = r"'?([^'!]+)'?!\$?([A-Z]{1,3})\$?(\d+)"

    # 함수 패턴
    FUNCTION_PATTERN = r'([A-Z]+)\s*\('

    def __init__(self):
        self.parsed_formulas: Dict[str, ParsedFormula] = {}

    def parse(self, formula: str) -> ParsedFormula:
        """수식 파싱"""
        if not formula or not formula.startswith('='):
            return ParsedFormula(
                original=formula,
                formula_type=FormulaType.REFERENCE,
                function_name="",
                arguments=[],
                cell_references=[],
                sheet_references=[]
            )

        # 수식에서 '=' 제거
        expr = formula[1:]

        # 셀 참조 추출
        cell_refs = self._extract_cell_references(expr)
        sheet_refs = self._extract_sheet_references(expr)

        # 함수 추출
        func_name = self._extract_main_function(expr)
        func_type = self._classify_formula(expr, func_name)

        # 인자 추출
        arguments = self._extract_arguments(expr, func_name)

        return ParsedFormula(
            original=formula,
            formula_type=func_type,
            function_name=func_name,
            arguments=arguments,
            cell_references=cell_refs,
            sheet_references=sheet_refs
        )

    def _extract_cell_references(self, expr: str) -> List[str]:
        """셀 참조 추출"""
        refs = []
        # 범위 참조
        for match in re.finditer(self.RANGE_REF_PATTERN, expr):
            refs.append(f"{match.group(1)}{match.group(2)}:{match.group(3)}{match.group(4)}")
        # 단일 셀 참조
        for match in re.finditer(self.CELL_REF_PATTERN, expr):
            ref = f"{match.group(1)}{match.group(2)}"
            if ref not in refs:
                refs.append(ref)
        return refs

    def _extract_sheet_references(self, expr: str) -> List[str]:
        """시트 참조 추출"""
        refs = []
        for match in re.finditer(self.SHEET_REF_PATTERN, expr):
            refs.append(match.group(1))
        return list(set(refs))

    def _extract_main_function(self, expr: str) -> str:
        """메인 함수명 추출"""
        match = re.match(self.FUNCTION_PATTERN, expr)
        if match:
            return match.group(1).upper()
        return ""

    def _classify_formula(self, expr: str, func_name: str) -> FormulaType:
        """수식 유형 분류"""
        expr_upper = expr.upper()

        if func_name in ['IF', 'IFS']:
            return FormulaType.CONDITIONAL
        elif func_name in ['VLOOKUP', 'HLOOKUP']:
            return FormulaType.LOOKUP
        elif func_name == 'INDEX' or 'MATCH' in expr_upper:
            return FormulaType.INDEX_MATCH
        elif func_name in ['SUM', 'AVERAGE', 'COUNT', 'MAX', 'MIN']:
            return FormulaType.AGGREGATION
        elif func_name in ['IFERROR', 'IFNA']:
            return FormulaType.ERROR_HANDLER
        elif any(op in expr for op in ['+', '-', '*', '/']):
            return FormulaType.ARITHMETIC
        else:
            return FormulaType.REFERENCE

    def _extract_arguments(self, expr: str, func_name: str) -> List[str]:
        """함수 인자 추출 (괄호 깊이 고려)"""
        if not func_name:
            return []

        # 함수 시작 위치 찾기
        start = expr.upper().find(func_name + '(')
        if start == -1:
            return []

        start += len(func_name) + 1  # '(' 다음부터

        # 괄호 매칭으로 인자 추출
        depth = 1
        current_arg = ""
        args = []

        for i, char in enumerate(expr[start:], start):
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


class LogicTranspiler:
    """
    엑셀 수식 → Python 코드 트랜스파일러

    핵심 기능:
    1. 수식 메타데이터 로드
    2. 수식 파싱 및 분류
    3. Python 코드 생성
    4. 대학별 환산 로직 생성
    """

    def __init__(self, metadata_dir: str = './output'):
        self.metadata_dir = Path(metadata_dir)
        self.parser = FormulaParser()
        self.university_logics: Dict[str, UniversityLogic] = {}
        self.generated_functions: Dict[str, str] = {}

    def load_formula_metadata(self, sheet_name: str) -> Dict[str, Any]:
        """수식 메타데이터 로드"""
        metadata_path = self.metadata_dir / f"{sheet_name}_formula_metadata.json"
        if not metadata_path.exists():
            return {}

        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def transpile_formula(self, formula: str, context: Dict[str, Any] = None) -> str:
        """단일 수식을 Python 코드로 변환"""
        parsed = self.parser.parse(formula)

        if parsed.formula_type == FormulaType.CONDITIONAL:
            return self._transpile_conditional(parsed, context)
        elif parsed.formula_type == FormulaType.LOOKUP:
            return self._transpile_lookup(parsed, context)
        elif parsed.formula_type == FormulaType.INDEX_MATCH:
            return self._transpile_index_match(parsed, context)
        elif parsed.formula_type == FormulaType.AGGREGATION:
            return self._transpile_aggregation(parsed, context)
        elif parsed.formula_type == FormulaType.ARITHMETIC:
            return self._transpile_arithmetic(parsed, context)
        elif parsed.formula_type == FormulaType.ERROR_HANDLER:
            return self._transpile_error_handler(parsed, context)
        else:
            return self._transpile_reference(parsed, context)

    def _transpile_conditional(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """IF/IFS 수식 변환"""
        args = parsed.arguments
        if len(args) < 2:
            return "None"

        # IF(condition, true_value, false_value)
        condition = self._convert_cell_ref(args[0])
        true_val = self._convert_cell_ref(args[1]) if len(args) > 1 else "None"
        false_val = self._convert_cell_ref(args[2]) if len(args) > 2 else "None"

        # OR/AND 처리
        condition = self._convert_logical_operators(condition)

        return f"np.where({condition}, {true_val}, {false_val})"

    def _transpile_lookup(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """VLOOKUP/HLOOKUP 변환"""
        args = parsed.arguments
        if len(args) < 3:
            return "None"

        func_name = parsed.function_name
        lookup_val = self._convert_cell_ref(args[0])
        table_ref = self._convert_table_ref(args[1])
        col_or_row_idx = args[2]
        approx = args[3] if len(args) > 3 else "False"

        if func_name == 'VLOOKUP':
            return f"self._vlookup({lookup_val}, {table_ref}, {col_or_row_idx}, {approx})"
        else:  # HLOOKUP
            return f"self._hlookup({lookup_val}, {table_ref}, {col_or_row_idx}, {approx})"

    def _transpile_index_match(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """INDEX/MATCH 변환"""
        expr = parsed.original[1:]  # '=' 제거

        # INDEX(array, MATCH(...), MATCH(...)) 패턴 감지
        index_match = re.search(
            r'INDEX\s*\(\s*([^,]+),\s*MATCH\s*\(([^)]+)\)\s*,\s*MATCH\s*\(([^)]+)\)\s*\)',
            expr, re.IGNORECASE
        )

        if index_match:
            array = self._convert_table_ref(index_match.group(1))
            row_match = index_match.group(2)
            col_match = index_match.group(3)

            return f"self._index_match_2d({array}, {self._parse_match_args(row_match)}, {self._parse_match_args(col_match)})"

        # 단순 INDEX(array, row, col)
        args = parsed.arguments
        if len(args) >= 2:
            array = self._convert_table_ref(args[0])
            row = self._convert_cell_ref(args[1])
            col = self._convert_cell_ref(args[2]) if len(args) > 2 else "0"
            return f"self._index({array}, {row}, {col})"

        return "None"

    def _transpile_aggregation(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """SUM/AVERAGE/COUNT 등 집계 함수 변환"""
        func_name = parsed.function_name
        args = parsed.arguments

        converted_args = [self._convert_cell_ref(arg) for arg in args]
        args_str = ", ".join(converted_args)

        func_map = {
            'SUM': f'np.nansum([{args_str}])',
            'AVERAGE': f'np.nanmean([{args_str}])',
            'COUNT': f'np.count_nonzero(~np.isnan([{args_str}]))',
            'MAX': f'np.nanmax([{args_str}])',
            'MIN': f'np.nanmin([{args_str}])',
        }

        return func_map.get(func_name, f"None  # Unknown: {func_name}")

    def _transpile_arithmetic(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """산술 연산 변환"""
        expr = parsed.original[1:]  # '=' 제거

        # 먼저 모든 셀 참조 패턴을 찾아서 변환 (A$1, $A1, $A$1, A1 모두 지원)
        # 패턴: [시트!]$?[A-Z]+$?[0-9]+
        cell_pattern = r"(\$?[A-Z]+\$?\d+)"

        def replace_cell_ref(match):
            ref = match.group(1)
            clean_ref = ref.replace('$', '')  # $ 기호 제거
            return f"row['{clean_ref}']"

        expr = re.sub(cell_pattern, replace_cell_ref, expr, flags=re.IGNORECASE)

        return expr

    def _transpile_error_handler(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """IFERROR/IFNA 변환"""
        args = parsed.arguments
        if len(args) < 2:
            return "None"

        expr = self.transpile_formula('=' + args[0], context)
        fallback = self._convert_cell_ref(args[1])

        return f"self._safe_eval(lambda: {expr}, {fallback})"

    def _transpile_reference(self, parsed: ParsedFormula, context: Dict = None) -> str:
        """단순 참조 변환"""
        if parsed.cell_references:
            return self._cell_ref_to_var(parsed.cell_references[0])
        return "None"

    # ========================================
    # 헬퍼 메서드
    # ========================================

    def _convert_cell_ref(self, ref: str) -> str:
        """셀 참조를 Python 변수명으로 변환"""
        if not ref:
            return "None"

        # 문자열 리터럴
        if ref.startswith('"') or ref.startswith("'"):
            return ref

        # 숫자
        try:
            float(ref)
            return ref
        except ValueError:
            pass

        # 셀 참조
        ref = ref.replace('$', '')

        # 시트 참조 처리: Sheet!A1 → sheets['Sheet']['A1']
        if '!' in ref:
            sheet, cell = ref.split('!', 1)
            sheet = sheet.strip("'")
            return f"self.sheets['{sheet}']['{cell}']"

        return f"self.current_sheet['{ref}']"

    def _convert_table_ref(self, ref: str) -> str:
        """테이블 범위 참조를 Python으로 변환"""
        ref = ref.replace('$', '').strip()

        # Sheet!A1:B10 형태
        if '!' in ref:
            sheet, range_ref = ref.split('!', 1)
            sheet = sheet.strip("'")
            return f"self.sheets['{sheet}']['{range_ref}']"

        return f"self.current_sheet['{ref}']"

    def _cell_ref_to_var(self, ref: str) -> str:
        """셀 참조를 변수명으로 변환 (예: A1 → col_A_row_1)"""
        ref = ref.replace('$', '')
        match = re.match(r'([A-Z]+)(\d+)', ref.upper())
        if match:
            return f"row['{match.group(1)}{match.group(2)}']"
        return f"row['{ref}']"

    def _convert_logical_operators(self, expr: str) -> str:
        """OR/AND를 Python으로 변환"""
        # OR(a, b, c) → (a) | (b) | (c)
        or_match = re.search(r'OR\s*\(([^)]+)\)', expr, re.IGNORECASE)
        if or_match:
            args = or_match.group(1).split(',')
            converted = ' | '.join([f'({arg.strip()})' for arg in args])
            expr = expr[:or_match.start()] + f'({converted})' + expr[or_match.end():]

        # AND(a, b, c) → (a) & (b) & (c)
        and_match = re.search(r'AND\s*\(([^)]+)\)', expr, re.IGNORECASE)
        if and_match:
            args = and_match.group(1).split(',')
            converted = ' & '.join([f'({arg.strip()})' for arg in args])
            expr = expr[:and_match.start()] + f'({converted})' + expr[and_match.end():]

        # 비교 연산자 변환
        expr = expr.replace('=', '==').replace('<>', '!=')
        expr = re.sub(r'([^=!<>])=([^=])', r'\1==\2', expr)

        return expr

    def _parse_match_args(self, match_expr: str) -> str:
        """MATCH 함수 인자 파싱"""
        args = match_expr.split(',')
        if len(args) >= 2:
            lookup_val = self._convert_cell_ref(args[0].strip())
            lookup_array = self._convert_table_ref(args[1].strip())
            match_type = args[2].strip() if len(args) > 2 else "0"
            return f"({lookup_val}, {lookup_array}, {match_type})"
        return "(None, None, 0)"

    # ========================================
    # 대학별 환산 로직 생성
    # ========================================

    def generate_university_logic(self, university_name: str, formula: str) -> UniversityLogic:
        """대학별 환산 로직 생성"""
        parsed = self.parser.parse(formula)
        python_code = self.transpile_formula(formula)

        # 가중치 컬럼 추출 (수식에서 참조하는 영역)
        weight_columns = []
        for ref in parsed.cell_references:
            # 행 번호로 영역 추정 (58=국어, 59=수학, 60=영어, 61=탐구1, 62=탐구2 등)
            match = re.match(r'([A-Z]+)(\d+)', ref)
            if match:
                row = int(match.group(2))
                area_map = {58: '국어', 59: '수학', 60: '영어', 61: '탐구1', 62: '탐구2'}
                if row in area_map:
                    weight_columns.append(area_map[row])

        logic = UniversityLogic(
            university_name=university_name,
            formula=formula,
            weight_columns=weight_columns,
            python_function=python_code
        )

        self.university_logics[university_name] = logic
        return logic

    def generate_all_university_logics(self) -> Dict[str, UniversityLogic]:
        """COMPUTE 시트에서 모든 대학 로직 생성"""
        metadata = self.load_formula_metadata('COMPUTE')
        if not metadata:
            return {}

        formula_samples = metadata.get('formula_samples', {})

        for col_name, sample_data in formula_samples.items():
            # 대학명 컬럼만 처리 (특수 컬럼 제외)
            if col_name.startswith('★') or col_name.startswith('□') or col_name.startswith('col_'):
                continue

            formula = sample_data.get('formula', '')
            if formula:
                self.generate_university_logic(col_name, formula)

        return self.university_logics

    # ========================================
    # Python 클래스 코드 생성
    # ========================================

    def generate_engine_class(self) -> str:
        """실행 가능한 Python 엔진 클래스 생성"""
        # 대학 로직 생성
        self.generate_all_university_logics()

        # 클래스 코드 생성
        code = '''# ============================================================
# Auto-Generated: University Score Calculator Engine
# Generated by Logic Transpiler v2.3
# ============================================================

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


class UniversityScoreEngine:
    """대학별 환산점수 계산 엔진"""

    def __init__(self, sheets: Dict[str, pd.DataFrame]):
        """
        Args:
            sheets: 시트명 → DataFrame 매핑
        """
        self.sheets = sheets
        self.current_sheet = None

    # ========================================
    # 기본 함수 구현
    # ========================================

    def _vlookup(self, lookup_val, table_ref: str, col_idx: int, approx: bool = False):
        """VLOOKUP 구현"""
        try:
            sheet_name, range_ref = self._parse_table_ref(table_ref)
            df = self.sheets.get(sheet_name)
            if df is None:
                return None

            # 첫 번째 컬럼에서 lookup_val 찾기
            mask = df.iloc[:, 0] == lookup_val
            if not mask.any():
                if approx:
                    # 근사 매칭: 가장 가까운 값 찾기
                    idx = (df.iloc[:, 0] - lookup_val).abs().idxmin()
                else:
                    return None
            else:
                idx = mask.idxmax()

            return df.iloc[idx, col_idx - 1]
        except:
            return None

    def _hlookup(self, lookup_val, table_ref: str, row_idx: int, approx: bool = False):
        """HLOOKUP 구현"""
        try:
            sheet_name, range_ref = self._parse_table_ref(table_ref)
            df = self.sheets.get(sheet_name)
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

    def _index(self, table_ref: str, row: int, col: int = 0):
        """INDEX 구현"""
        try:
            sheet_name, range_ref = self._parse_table_ref(table_ref)
            df = self.sheets.get(sheet_name)
            if df is None:
                return None
            return df.iloc[row - 1, col - 1 if col > 0 else 0]
        except:
            return None

    def _match(self, lookup_val, array_ref: str, match_type: int = 0):
        """MATCH 구현"""
        try:
            sheet_name, range_ref = self._parse_table_ref(array_ref)
            df = self.sheets.get(sheet_name)
            if df is None:
                return None

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

    def _index_match_2d(self, table_ref: str, row_match: tuple, col_match: tuple):
        """INDEX/MATCH 2D 조합 구현"""
        row = self._match(*row_match)
        col = self._match(*col_match)
        if row is None or col is None:
            return None
        return self._index(table_ref, row, col)

    def _safe_eval(self, expr_func, fallback=None):
        """IFERROR 구현"""
        try:
            result = expr_func()
            if pd.isna(result) or result is None:
                return fallback
            return result
        except:
            return fallback

    def _parse_table_ref(self, ref: str) -> tuple:
        """테이블 참조 파싱"""
        if "self.sheets['" in ref:
            # 이미 파싱된 형태
            match = re.search(r"self\.sheets\['([^']+)'\]\['([^']+)'\]", ref)
            if match:
                return match.group(1), match.group(2)

        if '!' in ref:
            parts = ref.split('!')
            return parts[0].strip("'"), parts[1]
        return 'COMPUTE', ref

    # ========================================
    # 대학별 환산점수 계산
    # ========================================

'''

        # 각 대학별 메서드 추가
        for univ_name, logic in self.university_logics.items():
            method_name = self._sanitize_method_name(univ_name)
            code += f'''
    def calc_{method_name}(self, row: Dict[str, Any]) -> float:
        """
        {univ_name} 환산점수 계산
        원본 수식: {logic.formula}
        반영 영역: {', '.join(logic.weight_columns) if logic.weight_columns else '전체'}
        """
        try:
            return {logic.python_function}
        except Exception as e:
            return 0.0
'''

        # 통합 계산 메서드
        code += '''
    def calculate_all(self, row: Dict[str, Any]) -> Dict[str, float]:
        """모든 대학 환산점수 계산"""
        results = {}
'''
        for univ_name in self.university_logics.keys():
            method_name = self._sanitize_method_name(univ_name)
            code += f'''        results['{univ_name}'] = self.calc_{method_name}(row)
'''

        code += '''        return results
'''

        return code

    def _sanitize_method_name(self, name: str) -> str:
        """메서드명으로 사용 가능한 형태로 변환"""
        # 한글 → 영문 매핑 (기본)
        name = re.sub(r'[^a-zA-Z0-9가-힣]', '_', name)
        name = name.replace(' ', '_')

        # 한글 유지 (Python 3 지원)
        return name.lower()

    def save_engine(self, output_path: str = './output/university_score_engine.py'):
        """생성된 엔진 코드를 파일로 저장"""
        code = self.generate_engine_class()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"[완료] 엔진 코드 생성: {output_path}")
        print(f"  - 대학 수: {len(self.university_logics)}개")

        return output_path


# ============================================================
# 분석 리포트 생성
# ============================================================

def generate_transpiler_report(transpiler: LogicTranspiler) -> Dict[str, Any]:
    """트랜스파일러 분석 리포트 생성"""
    report = {
        'total_universities': len(transpiler.university_logics),
        'formula_types': {},
        'universities': {}
    }

    for univ_name, logic in transpiler.university_logics.items():
        parsed = transpiler.parser.parse(logic.formula)

        # 수식 유형 집계
        ftype = parsed.formula_type.value
        report['formula_types'][ftype] = report['formula_types'].get(ftype, 0) + 1

        # 대학별 상세
        report['universities'][univ_name] = {
            'formula': logic.formula,
            'type': ftype,
            'weight_columns': logic.weight_columns,
            'cell_references': parsed.cell_references
        }

    return report


# ============================================================
# CLI 실행
# ============================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Logic Transpiler: Excel → Python')
    parser.add_argument('--metadata-dir', type=str, default='./output', help='메타데이터 디렉토리')
    parser.add_argument('--output', type=str, default='./output/university_score_engine.py', help='출력 파일')
    parser.add_argument('--report', action='store_true', help='분석 리포트 출력')

    args = parser.parse_args()

    print("=" * 60)
    print("Logic Transpiler: Excel Formula → Python Code")
    print("=" * 60)

    transpiler = LogicTranspiler(args.metadata_dir)

    # 대학 로직 생성
    print("\n[Step 1] 대학별 수식 로딩...")
    transpiler.generate_all_university_logics()
    print(f"  - 로드된 대학: {len(transpiler.university_logics)}개")

    # 엔진 코드 생성
    print("\n[Step 2] Python 엔진 코드 생성...")
    transpiler.save_engine(args.output)

    # 리포트
    if args.report:
        print("\n[Step 3] 분석 리포트 생성...")
        report = generate_transpiler_report(transpiler)

        report_path = Path(args.metadata_dir) / 'transpiler_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"  - 리포트 저장: {report_path}")

        print(f"\n수식 유형별 분포:")
        for ftype, count in report['formula_types'].items():
            print(f"  - {ftype}: {count}개")

    print("\n[완료]")
