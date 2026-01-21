"""
공유수식/배열수식 확장

XML에서 공유수식은 마스터 셀에만 저장되고, 나머지 셀은 인덱스만 참조합니다.
이를 전체 셀로 확장하여 각 셀의 실제 수식을 생성합니다.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging
from openpyxl.formula.translate import Translator
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormulaExpander:
    """공유수식 확장 클래스"""
    
    def __init__(self, formula_catalog_path: str = "outputs/formula_catalog.csv"):
        self.catalog_path = Path(formula_catalog_path)
        self.df: Optional[pd.DataFrame] = None
        self.expanded_df: Optional[pd.DataFrame] = None
    
    def load_catalog(self):
        """수식 카탈로그 로드"""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"수식 카탈로그를 찾을 수 없습니다: {self.catalog_path}")
        
        # dtype 안정화: shared_si가 float로 깨지면 그룹핑이 망가짐
        self.df = pd.read_csv(
            self.catalog_path,
            dtype={
                "sheet_name": "string",
                "cell_ref": "string",
                "formula_type": "string",
                "shared_si": "string",
                "shared_master": "string",
            },
            keep_default_na=True,
        )
        logger.info(f"수식 카탈로그 로드: {len(self.df)}개")
    
    def expand_shared_formulas(self) -> pd.DataFrame:
        """공유수식 확장"""
        if self.df is None:
            self.load_catalog()
        
        logger.info("공유수식 확장 시작...")
        
        # 공유수식 그룹 찾기 (NaN 제외)
        shared_df = self.df[(self.df["formula_type"] == "shared") & (self.df["shared_si"].notna())]
        logger.info(f"공유수식 셀 수: {len(shared_df)}개")
        
        shared_groups = shared_df.groupby(["sheet_name", "shared_si"], dropna=True)
        logger.info(f"공유수식 그룹 수: {shared_groups.ngroups}개")
        
        expanded_formulas = []
        expanded_count = 0
        
        for (sheet_name, shared_si), group in shared_groups:
            # 컬럼 호환: 이전 run에서 formula_x/formula_y가 생긴 경우도 방어
            formula_col = "formula"
            if formula_col not in group.columns:
                if "formula_x" in group.columns:
                    formula_col = "formula_x"
                elif "formula_y" in group.columns:
                    formula_col = "formula_y"

            # 마스터 셀 찾기 우선순위:
            # 1) shared_master 컬럼이 있으면 그 값과 cell_ref가 일치하는 row
            # 2) formula(text)가 비어있지 않은 row (master shared formula)
            master_cell = None
            if "shared_master" in group.columns:
                candidates = group.dropna(subset=["shared_master"])
                if len(candidates) > 0:
                    master_cell = str(candidates.iloc[0]["shared_master"])

            master_row = None
            if master_cell:
                hit = group[group["cell_ref"] == master_cell]
                if len(hit) > 0:
                    master_row = hit.iloc[0]
            if master_row is None:
                non_empty = group[group[formula_col].notna() & (group[formula_col].astype(str).str.len() > 0)]
                if len(non_empty) > 0:
                    master_row = non_empty.iloc[0]
                else:
                    master_row = group.iloc[0]

            master_cell = str(master_row["cell_ref"])
            master_formula = str(master_row[formula_col]) if pd.notna(master_row[formula_col]) else ""
            if master_formula and not master_formula.startswith("="):
                master_formula = "=" + master_formula
            
            # Translator로 각 셀에 맞게 수식 변환
            for idx, row in group.iterrows():
                target_cell = row['cell_ref']
                
                # 원본 formula(text)가 있으면 그대로 쓰고, 비어있으면 master에서 translate
                raw_formula = row.get(formula_col, "")
                raw_formula = "" if pd.isna(raw_formula) else str(raw_formula)
                if raw_formula and not raw_formula.startswith("="):
                    raw_formula = "=" + raw_formula

                if raw_formula:
                    effective_formula = raw_formula
                else:
                    if not master_formula:
                        effective_formula = ""
                    elif target_cell == master_cell:
                        effective_formula = master_formula
                    else:
                        try:
                            translator = Translator(master_formula, origin=master_cell)
                            effective_formula = translator.translate_formula(target_cell)
                        except Exception as e:
                            logger.debug(f"수식 변환 실패 ({master_cell} -> {target_cell}): {e}")
                            effective_formula = master_formula  # 폴백
                
                # 확장된 수식 데이터
                expanded_row = row.to_dict()
                expanded_row['effective_formula'] = effective_formula
                expanded_row['master_cell'] = master_cell
                expanded_formulas.append(expanded_row)
                expanded_count += 1
        
        # 일반 수식도 추가
        normal_formulas = self.df[self.df['formula_type'] == 'normal']
        formula_col = 'formula' if 'formula' in normal_formulas.columns else ('formula_x' if 'formula_x' in normal_formulas.columns else 'formula_y')
        for idx, row in normal_formulas.iterrows():
            expanded_row = row.to_dict()
            expanded_row['effective_formula'] = row[formula_col]
            expanded_row['master_cell'] = None
            expanded_formulas.append(expanded_row)
        
        # 배열수식도 추가
        array_formulas = self.df[self.df['formula_type'] == 'array']
        for idx, row in array_formulas.iterrows():
            expanded_row = row.to_dict()
            expanded_row['effective_formula'] = row[formula_col]
            expanded_row['master_cell'] = None
            expanded_formulas.append(expanded_row)
        
        self.expanded_df = pd.DataFrame(expanded_formulas)
        logger.info(f"공유수식 확장 완료: {expanded_count}개 확장")
        
        return self.expanded_df
    
    def save_expanded(self, output_path: str = "outputs/formula_catalog.csv"):
        """확장된 카탈로그 저장"""
        if self.expanded_df is None:
            self.expand_shared_formulas()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.expanded_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"확장된 카탈로그 저장: {output_file} ({len(self.expanded_df)}개)")
        return output_file


def main():
    """메인 함수"""
    expander = FormulaExpander()
    expanded_df = expander.expand_shared_formulas()
    expander.save_expanded()
    
    print(f"\n공유수식 확장 완료!")
    print(f"총 {len(expanded_df)}개 수식")
    print(f"effective_formula 컬럼이 추가되었습니다.")


if __name__ == "__main__":
    main()
