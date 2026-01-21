"""
참조 해석: 네임드/테이블/구조화 참조를 실제 Range로 변환
"""

import json
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReferenceResolver:
    """참조 해석 클래스"""
    
    def __init__(self):
        self.named_ranges: Dict = {}
        self.tables: Dict = {}
    
    def load_metadata(self, metadata_dir: str = "outputs"):
        """메타데이터 로드"""
        metadata_path = Path(metadata_dir)
        
        # 네임드레인지
        named_file = metadata_path / "named_ranges.json"
        if named_file.exists():
            with open(named_file, 'r', encoding='utf-8') as f:
                self.named_ranges = {nr['name']: nr for nr in json.load(f)}
        
        # 테이블
        tables_file = metadata_path / "tables.json"
        if tables_file.exists():
            with open(tables_file, 'r', encoding='utf-8') as f:
                self.tables = {t['name']: t for t in json.load(f)}
    
    def resolve_named_range(self, name: str) -> List[Dict]:
        """네임드레인지 해석"""
        if name in self.named_ranges:
            return self.named_ranges[name].get('destinations', [])
        return []
    
    def resolve_table_ref(self, table_name: str, column: str = None) -> Dict:
        """테이블 참조 해석"""
        if table_name in self.tables:
            table = self.tables[table_name]
            return {
                'sheet': table['sheet'],
                'ref': table['ref'],
                'column': column,
            }
        return {}


def main():
    """메인 함수"""
    resolver = ReferenceResolver()
    resolver.load_metadata()
    logger.info("참조 해석 준비 완료")


if __name__ == "__main__":
    main()
