# ============================================================
# Column Mapper: Excel 셀 참조 → BigQuery 컬럼 매핑
# NEO GOD Ultra Framework v2.3
# ============================================================
"""
Excel 컬럼 문자(A, B, ..., JL)를 숫자 인덱스로 변환하고,
BigQuery 테이블의 실제 컬럼명과 매핑합니다.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def excel_col_to_index(col: str) -> int:
    """Excel 컬럼 문자를 0-based 인덱스로 변환
    A=0, B=1, ..., Z=25, AA=26, AB=27, ..., JL=271
    """
    col = col.upper()
    result = 0
    for char in col:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result - 1


def index_to_excel_col(idx: int) -> str:
    """0-based 인덱스를 Excel 컬럼 문자로 변환"""
    result = ""
    idx += 1  # 1-based for calculation
    while idx > 0:
        idx, remainder = divmod(idx - 1, 26)
        result = chr(ord('A') + remainder) + result
    return result


class ColumnMapper:
    """Excel 셀 참조 ↔ BigQuery 컬럼 매핑 관리"""

    # COMPUTE 시트의 영역별 행 매핑 (Excel 행 번호)
    SUBJECT_ROW_MAP = {
        58: '국어',
        59: '수학',
        60: '영어',
        61: '탐구1',
        62: '탐구2',
        63: '탐구평균',
        64: '한국사',
        65: '제2외국어',
    }

    def __init__(self, metadata_dir: str = './output'):
        self.metadata_dir = Path(metadata_dir)
        self.univ_col_map: Dict[str, str] = {}  # 대학명 → Excel 컬럼
        self.col_univ_map: Dict[str, str] = {}  # Excel 컬럼 → 대학명
        self._load_university_mappings()

    def _load_university_mappings(self):
        """COMPUTE 메타데이터에서 대학-컬럼 매핑 로드"""
        metadata_path = self.metadata_dir / 'COMPUTE_formula_metadata.json'
        if not metadata_path.exists():
            print(f"[경고] 메타데이터 파일 없음: {metadata_path}")
            return

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        formula_samples = metadata.get('formula_samples', {})

        for univ_name, data in formula_samples.items():
            formula = data.get('formula', '')
            # =F$58 에서 F 추출
            match = re.search(r'=([A-Z]+)\$', formula)
            if match:
                col_letter = match.group(1)
                self.univ_col_map[univ_name] = col_letter
                self.col_univ_map[col_letter] = univ_name

        print(f"[매핑 로드] 대학 수: {len(self.univ_col_map)}개")

    def cell_ref_to_dict_key(self, cell_ref: str) -> Tuple[str, str]:
        """
        Excel 셀 참조를 (대학명, 영역) 튜플로 변환

        Args:
            cell_ref: 'JL58', 'F59' 등

        Returns:
            ('서울대', '국어') 형태의 튜플
        """
        # $ 기호 제거
        cell_ref = cell_ref.replace('$', '')

        # 컬럼과 행 분리
        match = re.match(r'([A-Z]+)(\d+)', cell_ref.upper())
        if not match:
            return ('unknown', 'unknown')

        col_letter = match.group(1)
        row_num = int(match.group(2))

        # 대학명
        univ_name = self.col_univ_map.get(col_letter, f'col_{col_letter}')

        # 영역
        subject = self.SUBJECT_ROW_MAP.get(row_num, f'row_{row_num}')

        return (univ_name, subject)

    def cell_ref_to_bq_column(self, cell_ref: str, bq_columns: List[str]) -> Optional[str]:
        """
        Excel 셀 참조를 BigQuery 컬럼명으로 변환

        현재 BigQuery 컬럼이 column_0, column_1 형태이므로,
        Excel 컬럼 인덱스를 사용하여 매핑
        """
        cell_ref = cell_ref.replace('$', '')
        match = re.match(r'([A-Z]+)(\d+)', cell_ref.upper())
        if not match:
            return None

        col_letter = match.group(1)
        col_idx = excel_col_to_index(col_letter)

        # BigQuery 컬럼명 찾기 (인덱스 기반)
        # 주의: 행에 따라 다른 매핑이 필요할 수 있음
        if col_idx < len(bq_columns):
            return bq_columns[col_idx]

        return None

    def generate_semantic_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        의미론적 매핑 생성: 대학명 → {영역: 실제값}

        Returns:
            {
                '서울대': {'국어': 'JL58', '수학': 'JL59', ...},
                '연세대': {'국어': 'XX58', '수학': 'XX59', ...},
                ...
            }
        """
        semantic_map = {}

        for univ_name, col_letter in self.univ_col_map.items():
            semantic_map[univ_name] = {}
            for row_num, subject in self.SUBJECT_ROW_MAP.items():
                cell_ref = f"{col_letter}{row_num}"
                semantic_map[univ_name][subject] = cell_ref

        return semantic_map

    def export_mapping_json(self, output_path: str = './output/column_mapping_v2.json'):
        """매핑 정보를 JSON으로 내보내기"""
        mapping = {
            'version': '2.3',
            'description': 'Excel 셀 참조 ↔ BigQuery 컬럼 매핑',
            'university_column_map': self.univ_col_map,
            'subject_row_map': {str(k): v for k, v in self.SUBJECT_ROW_MAP.items()},
            'semantic_mapping': self.generate_semantic_mapping(),
            'total_universities': len(self.univ_col_map)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        print(f"[내보내기 완료] {output_path}")
        return mapping


def create_enhanced_engine():
    """
    향상된 엔진 생성: BigQuery 컬럼명과 직접 연동 가능

    BigQuery의 실제 데이터 구조:
    - COMPUTE 테이블의 각 행은 특정 데이터 포인트
    - 컬럼은 대학별 계산 결과

    접근 방식:
    1. COMPUTE 테이블에서 행 58-65를 조회 (국어~제2외국어 점수)
    2. 각 대학 컬럼의 값을 직접 사용
    """
    pass  # 다음 단계에서 구현


if __name__ == '__main__':
    print("=" * 60)
    print("Column Mapper: Excel → BigQuery 매핑 분석")
    print("=" * 60)

    mapper = ColumnMapper()

    # 테스트
    print("\n[테스트] 셀 참조 변환:")
    test_refs = ['JL58', 'JL59', 'F58', 'F59', 'JK60']
    for ref in test_refs:
        univ, subject = mapper.cell_ref_to_dict_key(ref)
        col_idx = excel_col_to_index(re.match(r'([A-Z]+)', ref).group(1))
        print(f"  {ref} → ({univ}, {subject}) [컬럼 인덱스: {col_idx}]")

    # 매핑 내보내기
    print("\n[내보내기]")
    mapping = mapper.export_mapping_json()

    # 일부 대학 매핑 출력
    print("\n[대학별 매핑 예시]:")
    semantic = mapping['semantic_mapping']
    for univ in ['서울대', '연세대', '고려대', '가천대']:
        if univ in semantic:
            print(f"\n  {univ}:")
            for subject, cell in list(semantic[univ].items())[:3]:
                print(f"    • {subject}: {cell}")
