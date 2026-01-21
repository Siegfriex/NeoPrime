"""
룰 번들러: Excel 맥락 기반 룰 그룹화
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import json
import logging
from collections import defaultdict
from .excel_context import ExcelContextExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleBundler:
    """룰 번들러"""
    
    def __init__(self, 
                 rule_candidates_path: str = "outputs/rule_candidates.csv",
                 excel_path: str = r"C:\Neoprime\202511고속성장분석기(가채점)20251114 (1).xlsx"):
        self.rule_candidates_path = Path(rule_candidates_path)
        self.excel_path = excel_path
        self.df: pd.DataFrame = None
        self.context_extractor: ExcelContextExtractor = None
        self.bundles: Dict[str, List[Dict]] = defaultdict(list)
    
    def load_rules(self):
        """룰 후보 로드"""
        if not self.rule_candidates_path.exists():
            raise FileNotFoundError(f"룰 후보 파일을 찾을 수 없습니다: {self.rule_candidates_path}")
        self.df = pd.read_csv(self.rule_candidates_path)
        logger.info(f"룰 후보 로드: {len(self.df)}개")
    
    def extract_contexts(self):
        """Excel 맥락 추출"""
        if self.context_extractor is None:
            self.context_extractor = ExcelContextExtractor(self.excel_path)
            self.context_extractor.open_workbook()
        
        logger.info("Excel 맥락 추출 중...")
        
        contexts = []
        for idx, row in self.df.iterrows():
            location = str(row.get('location', ''))
            sheet, row_label, col_header = self.context_extractor.extract_context(location)
            contexts.append({
                'sheet': sheet,
                'row_label': row_label,
                'col_header': col_header,
            })
        
        # 컨텍스트를 DataFrame에 추가
        context_df = pd.DataFrame(contexts)
        self.df = pd.concat([self.df, context_df], axis=1)
        
        logger.info("Excel 맥락 추출 완료")
    
    def create_bundles(self):
        """룰 번들 생성"""
        if self.df is None:
            self.load_rules()
        
        if 'sheet' not in self.df.columns:
            self.extract_contexts()
        
        logger.info("룰 번들 생성 중...")
        
        # COMPUTE/RESTRICT 중심으로 번들링
        target_sheets = {'COMPUTE', 'RESTRICT'}
        
        for idx, row in self.df.iterrows():
            sheet = row.get('sheet')
            row_label = row.get('row_label')
            col_header = row.get('col_header')
            
            # 번들 키 생성
            if sheet in target_sheets:
                bundle_key = self._create_bundle_key(sheet, row_label, col_header)
                rule_dict = row.to_dict()
                self.bundles[bundle_key].append(rule_dict)
        
        logger.info(f"룰 번들 생성 완료: {len(self.bundles)}개 번들")
    
    def _create_bundle_key(self, sheet: str, row_label: str, col_header: str) -> str:
        """번들 키 생성"""
        parts = [sheet or 'UNKNOWN']
        if row_label:
            parts.append(f"row:{row_label}")
        if col_header:
            parts.append(f"col:{col_header}")
        return " | ".join(parts)
    
    def save_bundles(self, output_dir: str = "outputs"):
        """번들 저장"""
        if not self.bundles:
            self.create_bundles()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON 저장 (상세)
        bundles_json = {}
        for bundle_key, rules in self.bundles.items():
            bundles_json[bundle_key] = {
                'bundle_key': bundle_key,
                'rule_count': len(rules),
                'rules': rules[:10],  # 샘플만 (전체는 너무 큼)
            }
        
        json_file = output_path / "rule_bundles.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(bundles_json, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"번들 JSON 저장: {json_file}")
        
        # CSV 저장 (요약)
        bundle_summaries = []
        for bundle_key, rules in self.bundles.items():
            # 샘플 요약문 추출
            sample_summaries = []
            for rule in rules[:3]:
                summary = rule.get('summary_ko') or rule.get('human_hint', '')
                if summary:
                    sample_summaries.append(summary[:50])
            
            bundle_summaries.append({
                'bundle_key': bundle_key,
                'rule_count': len(rules),
                'sample_summaries': ' | '.join(sample_summaries),
            })
        
        bundle_df = pd.DataFrame(bundle_summaries)
        bundle_df = bundle_df.sort_values('rule_count', ascending=False)
        
        csv_file = output_path / "rule_bundles.csv"
        bundle_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        logger.info(f"번들 CSV 저장: {csv_file} ({len(bundle_df)}개 번들)")
        
        return json_file, csv_file
    
    def get_bundle_stats(self) -> Dict:
        """번들 통계"""
        if not self.bundles:
            self.create_bundles()
        
        total_rules = sum(len(rules) for rules in self.bundles.values())
        empty_bundles = sum(1 for key in self.bundles.keys() if 'UNKNOWN' in key or not key)
        
        return {
            'total_bundles': len(self.bundles),
            'total_rules': total_rules,
            'empty_bundles': empty_bundles,
            'coverage': (total_rules - empty_bundles) / max(total_rules, 1) * 100,
        }
    
    def close(self):
        """리소스 정리"""
        if self.context_extractor:
            self.context_extractor.close_workbook()


def main():
    """메인 함수"""
    bundler = RuleBundler()
    bundler.load_rules()
    bundler.extract_contexts()
    bundler.create_bundles()
    bundler.save_bundles()
    
    stats = bundler.get_bundle_stats()
    print(f"\n번들 통계:")
    print(f"  총 번들 수: {stats['total_bundles']}")
    print(f"  총 룰 수: {stats['total_rules']}")
    print(f"  커버리지: {stats['coverage']:.1f}%")
    
    bundler.close()
    print("\n룰 번들링 완료!")


if __name__ == "__main__":
    main()
