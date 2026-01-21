"""
수식 파싱: 함수/참조/상수 추출

수식에서 함수명, 셀/범위 참조, 네임드레인지, 구조화 참조, 외부 참조, 상수를 추출합니다.
"""

import pandas as pd
import re
import json
from typing import Dict, List
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormulaParser:
    """수식 파서"""
    
    def __init__(self, formula_catalog_path: str = "outputs/formula_catalog.csv"):
        self.catalog_path = formula_catalog_path
        self.df: pd.DataFrame = None
    
    def load_catalog(self):
        """카탈로그 로드"""
        self.df = pd.read_csv(self.catalog_path)
        logger.info(f"카탈로그 로드: {len(self.df)}개")
    
    def parse_all(self) -> pd.DataFrame:
        """모든 수식 파싱"""
        if self.df is None:
            self.load_catalog()
        
        logger.info("수식 파싱 시작...")
        
        # effective_formula 또는 formula 컬럼 사용
        formula_col = 'effective_formula' if 'effective_formula' in self.df.columns else 'formula'
        
        results = []
        for idx, row in self.df.iterrows():
            formula = row[formula_col]
            if pd.isna(formula) or not str(formula).strip():
                continue
            
            parsed = self.parse_formula(str(formula))
            parsed['sheet_name'] = row['sheet_name']
            parsed['cell_ref'] = row['cell_ref']
            results.append(parsed)
        
        result_df = pd.DataFrame(results)
        
        # 원본과 병합
        merged_df = self.df.merge(result_df, on=['sheet_name', 'cell_ref'], how='left')
        
        logger.info("수식 파싱 완료")
        return merged_df
    
    def parse_formula(self, formula: str) -> Dict:
        """단일 수식 파싱"""
        if not formula or not formula.startswith('='):
            return {
                'functions_used': [],
                'cell_refs': [],
                'range_refs': [],
                'named_refs': [],
                'table_refs': [],
                'external_refs': [],
                'constants': [],
            }

        # 문자열 리터럴 제거 (함수/참조 오탐 방지)
        body = re.sub(r'"[^"]*"', '""', formula)
        body = re.sub(r"'[^']*'", "''", body)

        functions = self._extract_functions(body)
        range_refs = self._extract_range_refs(body)
        cell_refs = self._extract_cell_refs(body)
        table_refs = self._extract_table_refs(body)
        external_refs = self._extract_external_refs(body)
        constants = self._extract_numeric_constants(body)

        # named refs는 현재 파일에서 0개로 보고되고 있으므로 보수적으로 빈 리스트 유지
        named_refs: List[str] = []

        return {
            'functions_used': sorted(set(functions)),
            'cell_refs': sorted(set(cell_refs)),
            'range_refs': sorted(set(range_refs)),
            'named_refs': named_refs,
            'table_refs': sorted(set(table_refs)),
            'external_refs': sorted(set(external_refs)),
            'constants': sorted(set(constants)),
        }
    
    def _extract_functions(self, formula: str) -> List[str]:
        """함수명 추출"""
        # 예: IFERROR(, INDEX(, MATCH( 등
        return re.findall(r'(?i)\b([A-Z][A-Z0-9_\.]*)\s*\(', formula)

    def _extract_range_refs(self, formula: str) -> List[str]:
        """범위 참조 추출 (시트 포함/열범위/행범위 포함)"""
        sheet = r"(?:'[^']+'|[A-Za-z0-9_가-힣]+)"
        a1 = r"\$?[A-Z]{1,3}\$?\d{1,7}"
        a1_range = rf"{a1}:{a1}"
        col_range = r"\$?[A-Z]{1,3}:\$?[A-Z]{1,3}"
        row_range = r"\$?\d{1,7}:\$?\d{1,7}"
        rng = rf"(?:{a1_range}|{col_range}|{row_range})"
        pattern = re.compile(rf"(?:(?P<sheet>{sheet})!)?(?P<rng>{rng})")
        out: List[str] = []
        for m in pattern.finditer(formula):
            sh = m.group("sheet")
            r = m.group("rng")
            if not r:
                continue
            out.append(f"{sh}!{r}" if sh else r)
        return out

    def _extract_cell_refs(self, formula: str) -> List[str]:
        """셀 참조 추출 (시트 포함)"""
        sheet = r"(?:'[^']+'|[A-Za-z0-9_가-힣]+)"
        a1 = r"\$?[A-Z]{1,3}\$?\d{1,7}"
        pattern = re.compile(rf"(?:(?P<sheet>{sheet})!)?(?P<cell>{a1})(?!:)")
        out: List[str] = []
        for m in pattern.finditer(formula):
            sh = m.group("sheet")
            c = m.group("cell")
            if not c:
                continue
            out.append(f"{sh}!{c}" if sh else c)
        return out

    def _extract_numeric_constants(self, formula: str) -> List[float]:
        """숫자 상수 추출"""
        # 0, 1, 1.23, -5 등
        nums = re.findall(r'(?<![A-Z0-9_])(-?\d+(?:\.\d+)?)(?![A-Z0-9_])', formula, re.IGNORECASE)
        out: List[float] = []
        for n in nums:
            try:
                out.append(float(n))
            except:
                pass
        return out

    def _extract_table_refs(self, formula: str) -> List[str]:
        """구조화 참조 추출 (Table[Column] 형식)"""
        # 간단한 패턴: TableName[ColumnName] 또는 [@ColumnName]
        refs: List[str] = []
        # TableName[Column]
        refs.extend([m.group(0) for m in re.finditer(r"\b\w+\[[^\]]+\]", formula)])
        # [@Column], [#Headers] 등 단독 bracket
        refs.extend([m.group(0) for m in re.finditer(r"\[(?:@|#)[^\]]+\]", formula)])
        return refs
    
    def _extract_external_refs(self, formula: str) -> List[str]:
        """외부 워크북 참조 추출"""
        # [Book.xlsx]Sheet!A1 형식
        return re.findall(r'\[([^\]]+)\]', formula)
    
    def save_parsed(self, output_path: str = "outputs/formula_catalog.csv"):
        """파싱 결과 저장"""
        parsed_df = self.parse_all()
        output_file = Path(output_path)
        # list 컬럼은 JSON 문자열로 직렬화 (graph_builder에서 안전하게 파싱)
        list_cols = [
            "functions_used",
            "cell_refs",
            "range_refs",
            "named_refs",
            "table_refs",
            "external_refs",
            "constants",
        ]
        for col in list_cols:
            if col in parsed_df.columns:
                parsed_df[col] = parsed_df[col].apply(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v)

        parsed_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"파싱 결과 저장: {output_file}")
        return output_file


def main():
    """메인 함수"""
    parser = FormulaParser()
    parsed_df = parser.parse_all()
    parser.save_parsed()
    
    print(f"\n수식 파싱 완료!")
    print(f"총 {len(parsed_df)}개 수식 파싱")
    
    # 함수 통계
    all_functions = []
    for funcs in parsed_df['functions_used'].dropna():
        if isinstance(funcs, list):
            all_functions.extend(funcs)
        elif isinstance(funcs, str) and funcs.strip():
            try:
                parsed = json.loads(funcs)
                if isinstance(parsed, list):
                    all_functions.extend(parsed)
                else:
                    all_functions.append(str(parsed))
            except Exception:
                # legacy repr(list)
                try:
                    import ast
                    parsed = ast.literal_eval(funcs)
                    if isinstance(parsed, list):
                        all_functions.extend(parsed)
                except Exception:
                    all_functions.append(funcs)
    
    from collections import Counter
    func_counts = Counter(all_functions)
    print(f"\n주요 함수 TOP 10:")
    for func, count in func_counts.most_common(10):
        print(f"  {func}: {count}")


if __name__ == "__main__":
    main()
