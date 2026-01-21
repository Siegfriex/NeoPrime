"""
룰 후보 한국어 요약 생성: 템플릿 기반
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleSummarizer:
    """룰 요약기"""
    
    def __init__(self, rule_candidates_path: str = "outputs/rule_candidates.csv"):
        self.rule_candidates_path = Path(rule_candidates_path)
        self.df: pd.DataFrame = None
    
    def load_rules(self):
        """룰 후보 로드"""
        if not self.rule_candidates_path.exists():
            raise FileNotFoundError(f"룰 후보 파일을 찾을 수 없습니다: {self.rule_candidates_path}")
        self.df = pd.read_csv(self.rule_candidates_path)
        logger.info(f"룰 후보 로드: {len(self.df)}개")
    
    def summarize_all(self) -> pd.DataFrame:
        """모든 룰 요약"""
        if self.df is None:
            self.load_rules()
        
        logger.info("룰 요약 생성 중...")
        
        summaries = []
        tags_list = []
        
        for idx, row in self.df.iterrows():
            summary = self._summarize_rule(row)
            tags = self._extract_tags(row)
            summaries.append(summary)
            tags_list.append(tags)
        
        self.df['summary_ko'] = summaries
        self.df['tags'] = tags_list
        
        logger.info("룰 요약 완료")
        return self.df
    
    def _summarize_rule(self, row: pd.Series) -> str:
        """단일 룰 요약"""
        source_type = row.get('source_type', '')
        condition = str(row.get('condition', ''))
        true_value = str(row.get('true_value', ''))
        false_value = str(row.get('false_value', ''))
        location = str(row.get('location', ''))
        
        # 소스 타입별 템플릿 적용
        if source_type == 'formula_if':
            cond_ko = self._normalize_expression(condition)
            true_ko = self._normalize_expression(true_value)
            false_ko = self._normalize_expression(false_value)
            return f"만약 {cond_ko}이면 {true_ko}, 아니면 {false_ko}"
        
        elif source_type == 'formula_ifs':
            cond_ko = self._normalize_expression(condition)
            true_ko = self._normalize_expression(true_value)
            false_ko = self._normalize_expression(false_value)
            if false_value:
                return f"조건 {cond_ko}이면 {true_ko} (그 외: {false_ko})"
            return f"조건 {cond_ko}이면 {true_ko}"
        
        elif source_type == 'formula_switch':
            cond_ko = self._normalize_expression(condition)
            true_ko = self._normalize_expression(true_value)
            false_ko = self._normalize_expression(false_value)
            if false_value:
                return f"{cond_ko}이면 {true_ko} (그 외: {false_ko})"
            return f"{cond_ko}이면 {true_ko}"
        
        elif source_type == 'conditional_format':
            cond_ko = self._normalize_expression(condition)
            return f"셀({location})에 대해 조건부서식: {cond_ko}"
        
        elif source_type == 'data_validation':
            cond_ko = self._normalize_expression(condition)
            return f"입력값 검증({location}): {cond_ko}"
        
        return f"규칙: {condition}"
    
    def _normalize_expression(self, expr: str) -> str:
        """수식을 한국어로 정규화"""
        if pd.isna(expr) or not expr:
            return "값 없음"
        
        s = str(expr).strip()
        
        # 너무 길면 요약
        if len(s) > 100:
            return s[:50] + "..." + s[-20:]
        
        # $ 제거 (절대 참조)
        s = re.sub(r'\$', '', s)
        
        # 연산자 한국어화
        s = re.sub(r'\s*=\s*', '는 ', s)
        s = re.sub(r'\s*<>\s*', '는 아님 ', s)
        s = re.sub(r'\s*<=\s*', ' 이하 ', s)
        s = re.sub(r'\s*>=\s*', ' 이상 ', s)
        s = re.sub(r'\s*<\s*', ' 미만 ', s)
        s = re.sub(r'\s*>\s*', ' 초과 ', s)
        
        # 논리 연산자
        s = re.sub(r'\bAND\b', '그리고', s, flags=re.IGNORECASE)
        s = re.sub(r'\bOR\b', '또는', s, flags=re.IGNORECASE)
        s = re.sub(r'\bNOT\b', '아님', s, flags=re.IGNORECASE)
        
        # 빈 값/0 값 패턴 정리
        s = re.sub(r'=\s*""', '는 빈 값', s)
        s = re.sub(r'=\s*0\b', '는 0', s)
        
        return s
    
    def _extract_tags(self, row: pd.Series) -> str:
        """태그 추출"""
        tags = []
        source_type = row.get('source_type', '')
        location = str(row.get('location', ''))
        
        if source_type:
            tags.append(source_type)
        
        # 시트명 태그
        if '!' in location:
            sheet = location.split('!')[0]
            tags.append(f"sheet:{sheet}")
        
        # 조건 패턴 태그
        condition = str(row.get('condition', ''))
        if 'OR(' in condition.upper():
            tags.append('or_condition')
        if 'AND(' in condition.upper():
            tags.append('and_condition')
        if '=' in condition:
            tags.append('equality_check')
        if '>' in condition or '<' in condition:
            tags.append('comparison')
        
        return ','.join(tags)
    
    def save_summarized(self, output_path: str = "outputs/rule_candidates_summarized.csv"):
        """요약된 룰 저장"""
        if self.df is None or 'summary_ko' not in self.df.columns:
            self.summarize_all()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"요약된 룰 저장: {output_file} ({len(self.df)}개)")
        return output_file


def main():
    """메인 함수"""
    summarizer = RuleSummarizer()
    summarized_df = summarizer.summarize_all()
    summarizer.save_summarized()
    
    print(f"\n룰 요약 완료!")
    print(f"총 {len(summarized_df)}개 룰")
    print("\n샘플 요약:")
    for idx, row in summarized_df.head(5).iterrows():
        print(f"  {row.get('rule_id', 'N/A')}: {row.get('summary_ko', 'N/A')}")


if __name__ == "__main__":
    main()
